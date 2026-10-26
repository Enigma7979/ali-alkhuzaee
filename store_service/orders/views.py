import hashlib,json,secrets,logging
from datetime import timedelta
from urllib.parse import urlparse
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse,HttpResponse,FileResponse,HttpResponseForbidden,HttpResponseNotFound
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from . import payments
from .models import Order,RateBucket,EmailJob,DownloadGrant
from .forms import CheckoutForm,RecoveryForm
from .fulfillment import paid,revoke,validate_stripe,validate_paypal,release_path,VerificationError,digest,grant
logger=logging.getLogger(__name__)
def notice(request,key,status=200):return render(request,'orders/notice.html',{'key':key},status=status)
def limit(request,scope,maximum=6):
 key=hashlib.sha256((settings.SECRET_KEY+request.META.get('REMOTE_ADDR','')+scope).encode()).hexdigest();now=timezone.now()
 with transaction.atomic():
  b,_=RateBucket.objects.get_or_create(key=key,defaults={'expires_at':now+timedelta(minutes=15)})
  RateBucket.objects.filter(key=key,expires_at__lte=now).update(hits=0,expires_at=now+timedelta(minutes=15))
  RateBucket.objects.filter(key=key).update(hits=F('hits')+1);b.refresh_from_db()
 return b.hits<=maximum

def ready():
 if not settings.CHECKOUT_ENABLED:return False
 if not all([settings.STRIPE_SECRET_KEY,settings.STRIPE_WEBHOOK_SECRET,settings.PAYPAL_CLIENT_ID,settings.PAYPAL_CLIENT_SECRET,settings.PAYPAL_WEBHOOK_ID,settings.PAYPAL_MERCHANT_ID]):return False
 try:
  for lang in ('en','ar','ru'):release_path(lang)
 except VerificationError:return False
 return True
@require_GET
def availability(request):return JsonResponse({'available':ready(),'mode':settings.PAYMENT_MODE,'currency':'EUR','amount':299,'languages':['en','ar','ru']})
@require_http_methods(['GET','POST'])
def checkout(request):
 if not ready():return notice(request,'unavailable',503)
 form=CheckoutForm(request.POST or None,initial={'language':request.LANGUAGE_CODE})
 if request.method=='POST':
  if not limit(request,'checkout'):return notice(request,'rateLimited',429)
  if form.is_valid() and not form.cleaned_data['website']:
   d=form.cleaned_data;release_path(d['language'])
   order=Order.objects.create(email=d['email'].strip().lower(),language=d['language'],provider=d['provider'],mode=settings.PAYMENT_MODE,terms_version='v1-approved' if settings.LEGAL_APPROVED else 'v1-draft')
   request.session['order_id']=str(order.id)
   try:
    if order.provider=='stripe':
     result=payments.stripe_session(order);provider_id=result['id'];url=result['url']
     valid=urlparse(url).scheme=='https' and urlparse(url).hostname=='checkout.stripe.com'
    else:
     result=payments.paypal_create(order);provider_id=result['id'];url=next(x['href'] for x in result['links'] if x['rel'] in ('payer-action','approve'))
     valid=urlparse(url).scheme=='https' and urlparse(url).hostname in ('www.paypal.com','www.sandbox.paypal.com')
    if not valid:raise VerificationError('Invalid approval origin')
    order.provider_order_id=provider_id;order.save(update_fields=['provider_order_id']);return redirect(url)
   except Exception:
    order.status='failed';order.save(update_fields=['status']);logger.warning('Checkout provider request failed; order=%s',order.id)
    return notice(request,'paymentError',502)
 return render(request,'orders/checkout.html',{'form':form,'test_mode':settings.PAYMENT_MODE=='test'})
@require_GET
def status(request):
 order=Order.objects.filter(pk=request.session.get('order_id')).first() if request.session.get('order_id') else None
 link=EmailJob.objects.filter(order=order,kind='fulfillment').values_list('link',flat=True).first() if order and order.status=='paid' else None
 return render(request,'orders/status.html',{'order':order,'download_link':link})
@require_GET
def cancel(request):return notice(request,'cancelled')
@require_GET
def paypal_return(request):
 # An approval redirect is not payment proof. Capture requires CSRF-protected POST and the checkout session.
 oid=request.session.get('order_id');order=Order.objects.filter(pk=oid,provider='paypal').first() if oid else None
 if not order or request.GET.get('token')!=order.provider_order_id:return notice(request,'invalid',403)
 return render(request,'orders/capture.html',{'order':order})
@require_POST
def capture(request):
 if not limit(request,'capture',12):return notice(request,'rateLimited',429)
 oid=request.session.get('order_id');order=Order.objects.filter(pk=oid,provider='paypal').first() if oid else None
 if not order:return notice(request,'invalid',403)
 if order.status=='paid':return redirect('/store/status/?lang='+order.language)
 if order.status!='pending':return notice(request,'invalid',403)
 try:
  # PayPal-Request-Id makes a retried capture idempotent. Always retrieve authoritative order afterwards.
  try:payments.paypal_capture(order.provider_order_id,str(order.id))
  except Exception:pass # A lost capture response is reconciled with an authoritative read.
  data=payments.paypal_retrieve(order.provider_order_id);cap_id=validate_paypal(order,data)
  order.capture_id=cap_id;order.save(update_fields=['capture_id']);paid(order.id,'capture-'+cap_id,'paypal','server-capture')
 except Exception:
  logger.warning('PayPal capture/reconciliation pending; order=%s',order.id)
  return notice(request,'paymentError',502)
 return redirect('/store/status/?lang='+order.language)
@csrf_exempt
@require_POST
def stripe_webhook(request):
 try:event=payments.stripe_verify(request.body,request.headers.get('Stripe-Signature',''))
 except Exception:return HttpResponse(status=400)
 if bool(event.get('livemode'))!=(settings.PAYMENT_MODE=='live'):return HttpResponse(status=400)
 typ=event['type'];obj=event['data']['object']
 try:
  if typ in ('checkout.session.completed','checkout.session.async_payment_succeeded'):
   order=Order.objects.get(provider='stripe',provider_order_id=obj['id']);session=payments.stripe_retrieve(obj['id']);validate_stripe(order,session)
   # Store the verified payment reference for refund/dispute matching.
   order.capture_id=session['payment_intent']['id'];order.save(update_fields=['capture_id']);paid(order.id,event['id'],'stripe',typ)
  elif typ=='charge.refunded' and obj.get('amount_refunded',0)>0:
   order=Order.objects.filter(provider='stripe',capture_id=obj['payment_intent']).first()
   if not order:
    intent=payments.stripe_intent(obj['payment_intent']);order=Order.objects.get(pk=intent.get('metadata',{}).get('order_id'),provider='stripe',mode=settings.PAYMENT_MODE)
   revoke(order.id,event['id'],'stripe',typ)
  elif typ=='charge.dispute.created':
   order=Order.objects.filter(provider='stripe',capture_id=obj['payment_intent']).first()
   if not order:
    intent=payments.stripe_intent(obj['payment_intent']);order=Order.objects.get(pk=intent.get('metadata',{}).get('order_id'),provider='stripe',mode=settings.PAYMENT_MODE)
   revoke(order.id,event['id'],'stripe',typ,'disputed')
  elif typ=='checkout.session.expired':
   Order.objects.filter(provider='stripe',provider_order_id=obj['id'],status='pending').update(status='failed')
 except Order.DoesNotExist:return HttpResponse(status=200) # Not one of this store's orders.
 except VerificationError:return HttpResponse(status=400)
 except Exception:
  logger.warning('Stripe webhook processing needs retry; type=%s',typ);return HttpResponse(status=503)
 return HttpResponse(status=200)
@csrf_exempt
@require_POST
def paypal_webhook(request):
 try:
  event=json.loads(request.body)
  if not payments.paypal_verify(event,request.headers):return HttpResponse(status=400)
  typ=event['event_type'];resource=event.get('resource',{})
  if typ=='PAYMENT.CAPTURE.COMPLETED':
   provider_id=resource.get('supplementary_data',{}).get('related_ids',{}).get('order_id')
   order=Order.objects.get(provider='paypal',provider_order_id=provider_id)
   data=payments.paypal_retrieve(provider_id);cap_id=validate_paypal(order,data)
   if cap_id!=resource['id']:raise VerificationError('Capture mismatch')
   order.capture_id=cap_id;order.save(update_fields=['capture_id']);paid(order.id,event['id'],'paypal',typ)
  elif typ in ('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED'):
   capture_id=resource.get('id') if typ=='PAYMENT.CAPTURE.REVERSED' else resource.get('supplementary_data',{}).get('related_ids',{}).get('capture_id')
   if not capture_id:
    # A verified API link is parsed only for an ID, never fetched as an arbitrary URL.
    import re
    links=[x.get('href','') for x in resource.get('links',[]) if x.get('rel')=='up']
    capture_id=next((m.group(1) for u in links if (m:=re.search(r'/v2/payments/captures/([A-Za-z0-9]+)$',u))),None)
   if not capture_id:raise VerificationError('Missing capture reference')
   order=Order.objects.get(provider='paypal',capture_id=capture_id);revoke(order.id,event['id'],'paypal',typ)
 except Order.DoesNotExist:return HttpResponse(status=200)
 except (ValueError,KeyError,VerificationError):return HttpResponse(status=400)
 except Exception:
  logger.warning('PayPal webhook processing needs retry');return HttpResponse(status=503)
 return HttpResponse(status=200)
@require_GET
def download_page(request,token):
 obj=DownloadGrant.objects.select_related('order').filter(token_hash=digest(token),revoked=False,expires_at__gt=timezone.now(),order__status='paid').first()
 if not obj:return notice(request,'expired',410)
 # Language selection affects chrome only, never the delivered edition.
 return render(request,'orders/download.html',{'download_token':token,'edition':obj.order.language.upper()})
@require_POST
def download_file(request,token):
 if not limit(request,'download',30):return notice(request,'rateLimited',429)
 with transaction.atomic():
  obj=DownloadGrant.objects.select_for_update().select_related('order').filter(token_hash=digest(token),revoked=False,expires_at__gt=timezone.now(),order__status='paid').first()
  if not obj:return notice(request,'expired',410)
  try:path=release_path(obj.order.language)
  except VerificationError:return notice(request,'unavailable',503)
  obj.downloads=F('downloads')+1;obj.save(update_fields=['downloads'])
  return FileResponse(path.open('rb'),as_attachment=True,filename='Creator_Guide_'+obj.order.language.upper()+'.pdf',content_type='application/pdf')
@require_http_methods(['GET','POST'])
def recover(request):
 form=RecoveryForm(request.POST or None)
 if request.method=='POST':
  if not limit(request,'recover'):return notice(request,'rateLimited',429)
  if form.is_valid():
   for order in Order.objects.filter(email__iexact=form.cleaned_data['email'].strip(),status='paid',mode=settings.PAYMENT_MODE).order_by('-created_at')[:5]:
    with transaction.atomic():
     order=Order.objects.select_for_update().get(pk=order.id)
     if order.status=='paid':
      kind='recovery-'+timezone.now().strftime('%Y%m%d')
      if not EmailJob.objects.filter(order=order,kind=kind).exists():grant(order,kind)
   return notice(request,'recoverySent')
 return render(request,'orders/recover.html',{'form':form})
