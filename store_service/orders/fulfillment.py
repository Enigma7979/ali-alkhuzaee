import hashlib,json,secrets
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Order,PaymentEvent,DownloadGrant,EmailJob
class VerificationError(Exception):pass
def digest(token):return hashlib.sha256(token.encode()).hexdigest()
def release_path(language):
 if language not in ('en','ar','ru'):raise VerificationError('Invalid language')
 try:
  manifest=json.loads(settings.PDF_MANIFEST.read_text());item=manifest['editions'][language]
  path=(settings.PDF_ROOT/item['file']).resolve()
  if manifest.get('status')!='approved' or not path.is_relative_to(settings.PDF_ROOT) or path.suffix!='.pdf':raise VerificationError('Unapproved release')
  if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise VerificationError('Release hash mismatch')
  return path
 except (OSError,KeyError,ValueError) as exc:raise VerificationError('PDF release unavailable') from exc
def grant(order,kind):
 raw=secrets.token_urlsafe(32)
 DownloadGrant.objects.create(order=order,token_hash=digest(raw),expires_at=timezone.now()+timedelta(seconds=settings.DOWNLOAD_MAX_AGE))
 link=settings.PUBLIC_ORIGIN+'/store/download/'+raw+'/?lang='+order.language
 EmailJob.objects.get_or_create(order=order,kind=kind,defaults={'link':link})
 return link
@transaction.atomic
def paid(order_id,event_id,provider,kind):
 order=Order.objects.select_for_update().get(pk=order_id)
 if order.provider!=provider or order.mode!=settings.PAYMENT_MODE:raise VerificationError('Provider/mode mismatch')
 existing=PaymentEvent.objects.filter(provider=provider,event_id=event_id).first()
 if existing:
  if existing.order_id!=order.id:raise VerificationError('Event/order mismatch')
  return order
 PaymentEvent.objects.create(provider=provider,event_id=event_id,order=order,kind=kind)
 if order.status in ('refunded','disputed'):return order
 if order.status=='paid':return order
 release_path(order.language)
 order.status='paid';order.fulfilled_at=timezone.now();order.save(update_fields=['status','fulfilled_at'])
 grant(order,'fulfillment')
 return order
@transaction.atomic
def revoke(order_id,event_id,provider,kind,status='refunded'):
 order=Order.objects.select_for_update().get(pk=order_id)
 if order.provider!=provider:raise VerificationError('Provider mismatch')
 event,created=PaymentEvent.objects.get_or_create(provider=provider,event_id=event_id,defaults={'order':order,'kind':kind})
 if event.order_id!=order.id:raise VerificationError('Event/order mismatch')
 if created:
  order.status=status;order.save(update_fields=['status']);DownloadGrant.objects.filter(order=order).update(revoked=True)
 return order

def validate_stripe(order,session):
 if session.get('id')!=order.provider_order_id or session.get('mode')!='payment' or session.get('payment_status')!='paid':raise VerificationError('Unpaid session')
 if session.get('amount_total')!=299 or session.get('currency','').upper()!='EUR':raise VerificationError('Amount/currency mismatch')
 meta=session.get('metadata',{})
 if meta.get('order_id')!=str(order.id) or meta.get('language')!=order.language or meta.get('product')!='creator-guide':raise VerificationError('Metadata mismatch')
 if bool(session.get('livemode'))!=(order.mode=='live'):raise VerificationError('Mode mismatch')
 intent=session.get('payment_intent')
 if not isinstance(intent,dict) or intent.get('status')!='succeeded':raise VerificationError('Payment intent must be retrieved and settled')
 charge=intent.get('latest_charge')
 if not isinstance(charge,dict) or charge.get('amount_refunded',0)>0 or charge.get('disputed') or not charge.get('paid'):raise VerificationError('Payment is refunded, disputed or unpaid')

def validate_paypal(order,data):
 if data.get('id')!=order.provider_order_id or data.get('status')!='COMPLETED':raise VerificationError('Incomplete PayPal order')
 units=data.get('purchase_units',[])
 if len(units)!=1:raise VerificationError('Unexpected units')
 u=units[0];amount=u.get('amount',{})
 if u.get('custom_id')!=str(order.id) or u.get('invoice_id')!=str(order.id) or u.get('payee',{}).get('merchant_id')!=settings.PAYPAL_MERCHANT_ID:raise VerificationError('Identity mismatch')
 if Decimal(amount.get('value','0'))!=Decimal('2.99') or amount.get('currency_code')!='EUR':raise VerificationError('Amount mismatch')
 captures=u.get('payments',{}).get('captures',[])
 if len(captures)!=1:raise VerificationError('Unexpected captures')
 cap=captures[0]
 if cap.get('status')!='COMPLETED' or not cap.get('final_capture'):raise VerificationError('Unsettled capture')
 if Decimal(cap.get('amount',{}).get('value','0'))!=Decimal('2.99') or cap.get('amount',{}).get('currency_code')!='EUR':raise VerificationError('Capture amount mismatch')
 return cap['id']
