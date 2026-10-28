import tempfile,json,hashlib
import pymupdf
from pathlib import Path
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.utils import timezone
from django.core.management import call_command
from .models import Order,PaymentEvent,EmailJob,DownloadGrant
from .fulfillment import paid,revoke,grant,digest,release_path,validate_stripe,validate_paypal,VerificationError
class StoreTests(TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  editions={}
  for lang in ['en','ar','ru']:
   doc=pymupdf.open();[doc.new_page(width=499,height=709).insert_text((60,100),'Edition '+lang) for _ in range(3)];b=doc.tobytes()
   p=self.root/(lang+'.pdf');p.write_bytes(b);editions[lang]={'file':p.name,'sha256':hashlib.sha256(b).hexdigest()}
  self.manifest=self.root/'release.json';self.manifest.write_text(json.dumps({'status':'approved','editions':editions}))
  self.settings_override=override_settings(PDF_ROOT=self.root,PDF_MANIFEST=self.manifest,PAYMENT_MODE='test',PUBLIC_ORIGIN='http://testserver',PAYPAL_MERCHANT_ID='merchant-test',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
  self.settings_override.enable();self.addCleanup(self.settings_override.disable);self.addCleanup(self.tmp.cleanup)
  self.order=Order.objects.create(name='علي الخزاعي',email='buyer@example.test',language='ar',provider='stripe',provider_order_id='cs_test_1')
 def stripe(self):return {'id':'cs_test_1','mode':'payment','payment_status':'paid','amount_total':1400,'currency':'eur','livemode':False,'metadata':{'order_id':str(self.order.id),'language':'ar','product':'creator-guide'},'payment_intent':{'id':'pi_1','status':'succeeded','latest_charge':{'id':'ch_1','paid':True,'amount_refunded':0,'disputed':False}}}
 def pp(self,o):return {'id':o.provider_order_id,'status':'COMPLETED','purchase_units':[{'custom_id':str(o.id),'invoice_id':str(o.id),'payee':{'merchant_id':'merchant-test'},'amount':{'value':'14.00','currency_code':'EUR'},'payments':{'captures':[{'id':'CAP1','status':'COMPLETED','final_capture':True,'amount':{'value':'14.00','currency_code':'EUR'}}]}}]}
 def test_checkout_closed_by_default(self):self.assertEqual(self.client.get('/store/checkout/').status_code,503)
 def test_availability_false_without_credentials(self):self.assertFalse(self.client.get('/store/availability/').json()['available'])
 def test_availability_readable_by_site_origin_only(self):
  r=self.client.get('/store/availability/');self.assertEqual(r['Access-Control-Allow-Origin'],'https://alialkhuzaee.com')
  self.assertFalse(self.client.get('/store/checkout/').has_header('Access-Control-Allow-Origin'))
 def test_checkout_redirect_allowed_by_csp(self):
  csp=self.client.get('/store/availability/')['Content-Security-Policy']
  for host in ('https://checkout.stripe.com','https://www.paypal.com','https://www.sandbox.paypal.com'):self.assertIn(host,csp.split('form-action')[1].split(';')[0])
 def test_rate_limit_uses_platform_client_header(self):
  from .views import client_ip
  from django.test import RequestFactory
  req=RequestFactory().get('/',HTTP_X_REAL_IP='203.0.113.7',REMOTE_ADDR='10.0.0.1')
  self.assertEqual(client_ip(req),'10.0.0.1')
  with override_settings(CLIENT_IP_HEADER='X-Real-IP'):self.assertEqual(client_ip(req),'203.0.113.7')
 def test_approved_three_files_required(self):
  self.manifest.write_text('{}')
  with self.assertRaises(VerificationError):release_path('en')
 def test_file_tampering_rejected(self):
  (self.root/'ar.pdf').write_bytes(b'tampered')
  with self.assertRaises(VerificationError):release_path('ar')
 def test_path_traversal_rejected(self):
  d=json.loads(self.manifest.read_text());d['editions']['ar']['file']='../outside.pdf';self.manifest.write_text(json.dumps(d))
  with self.assertRaises(VerificationError):release_path('ar')
 def test_stripe_amount_currency_language_mode_checked(self):
  validate_stripe(self.order,self.stripe())
  for field,value in [('amount_total',1),('currency','usd'),('livemode',True),('payment_status','unpaid'),('mode','subscription')]:
   d=self.stripe();d[field]=value
   with self.assertRaises(VerificationError):validate_stripe(self.order,d)
  d=self.stripe();d['metadata']['language']='ru'
  with self.assertRaises(VerificationError):validate_stripe(self.order,d)
 def test_stripe_refunded_disputed_charge_cannot_fulfill(self):
  for field,value in [('amount_refunded',1400),('disputed',True),('paid',False)]:
   d=self.stripe();d['payment_intent']['latest_charge'][field]=value
   with self.assertRaises(VerificationError):validate_stripe(self.order,d)
 def test_duplicate_events_and_distinct_events_one_fulfillment(self):
  paid(self.order.id,'evt_1','stripe','paid');paid(self.order.id,'evt_1','stripe','paid');paid(self.order.id,'evt_2','stripe','paid')
  self.assertEqual(DownloadGrant.objects.count(),1);self.assertEqual(EmailJob.objects.count(),1);self.assertEqual(PaymentEvent.objects.count(),2)
 def test_fulfillment_rolls_back_when_pdf_missing(self):
  (self.root/'ar.pdf').unlink()
  with self.assertRaises(VerificationError):paid(self.order.id,'evt','stripe','paid')
  self.assertEqual(PaymentEvent.objects.count(),0);self.order.refresh_from_db();self.assertEqual(self.order.status,'pending')
 def test_provider_mismatch(self):
  with self.assertRaises(VerificationError):paid(self.order.id,'evt','paypal','paid')
 def test_cross_order_event_collision(self):
  paid(self.order.id,'evt','stripe','paid');o=Order.objects.create(email='b@example.test',language='ru',provider='stripe')
  with self.assertRaises(VerificationError):paid(o.id,'evt','stripe','paid')
 def test_refund_revokes_and_late_payment_cannot_reactivate(self):
  paid(self.order.id,'evt','stripe','paid');revoke(self.order.id,'refund','stripe','refund');paid(self.order.id,'late','stripe','paid');self.order.refresh_from_db()
  self.assertEqual(self.order.status,'refunded');self.assertTrue(DownloadGrant.objects.get().revoked)
 def test_refund_before_payment_is_terminal(self):
  revoke(self.order.id,'refund','stripe','refund');paid(self.order.id,'evt','stripe','paid');self.assertEqual(DownloadGrant.objects.count(),0)
 def test_download_is_bound_to_order_language_not_query(self):
  paid(self.order.id,'evt','stripe','paid');token=EmailJob.objects.get().link.split('/download/')[1].split('/')[0]
  r=self.client.post('/store/download/'+token+'/file/?lang=ru',{'language':'ru'});self.assertEqual(r.status_code,200);self.assertIn('Creator_Guide_AR.pdf',r['Content-Disposition']);doc=pymupdf.open(stream=r.content)
  self.assertIn('Edition ar',doc[0].get_text());self.assertIn('علي الخزاعي · buyer@example.test',doc[0].get_text());self.assertIn(self.order.licence_ref,doc.metadata['subject'])
 def test_stamped_copy_keeps_book_text_and_marks_every_page(self):
  from .stamp import stamp
  for lang,name in [('en',"Jane O'Brien"),('ar','عليّ عبد الله'),('ru','Анна Петрова')]:
   doc=pymupdf.open(stream=stamp(self.root/(lang+'.pdf'),lang,name,'x@example.test','AB12CD34'))
   for page in doc:self.assertIn('Edition '+lang,page.get_text());self.assertIn(name,page.get_text());self.assertIn('AB12CD34',page.get_text())
   self.assertIn('x@example.test',doc[1].get_text())
   doc=pymupdf.open(stream=stamp(self.root/(lang+'.pdf'),lang,name,'x@example.test','AB12CD34','diagonal'));self.assertIn(name,doc[2].get_text())
 def test_expired_and_forged_links_denied(self):
  paid(self.order.id,'evt','stripe','paid');g=DownloadGrant.objects.get();g.expires_at=timezone.now()-timedelta(seconds=1);g.save();token=EmailJob.objects.get().link.split('/download/')[1].split('/')[0]
  self.assertEqual(self.client.post('/store/download/'+token+'/file/').status_code,410);self.assertEqual(self.client.get('/store/download/forged/').status_code,410)
 def test_get_does_not_download_or_consume(self):
  paid(self.order.id,'evt','stripe','paid');token=EmailJob.objects.get().link.split('/download/')[1].split('/')[0];self.assertEqual(self.client.get('/store/download/'+token+'/').status_code,200);self.assertEqual(DownloadGrant.objects.get().downloads,0);self.assertEqual(self.client.get('/store/download/'+token+'/file/').status_code,405)
 def test_private_download_form_requires_csrf(self):
  paid(self.order.id,'evt','stripe','paid');token=EmailJob.objects.get().link.split('/download/')[1].split('/')[0];c=Client(enforce_csrf_checks=True)
  self.assertEqual(c.post('/store/download/'+token+'/file/').status_code,403)
 def test_status_redirect_alone_cannot_fulfill(self):
  self.client.get('/store/status/?session_id=cs_test_1&paid=true');self.order.refresh_from_db();self.assertEqual(self.order.status,'pending')
 def test_recovery_is_generic_and_daily_idempotent(self):
  paid(self.order.id,'evt','stripe','paid');a=self.client.post('/store/recover/',{'email':'buyer@example.test'});b=self.client.post('/store/recover/',{'email':'unknown@example.test'});self.assertEqual(a.content,b.content)
  self.client.post('/store/recover/',{'email':'buyer@example.test'});self.assertEqual(EmailJob.objects.count(),2)
 def test_recovery_rate_limit(self):
  for _ in range(6):self.assertEqual(self.client.post('/store/recover/',{'email':'x@example.test'}).status_code,200)
  self.assertEqual(self.client.post('/store/recover/',{'email':'x@example.test'}).status_code,429)
 def test_translated_pages_and_rtl(self):
  for lang in ['ar','en','ru']:
   r=self.client.get('/store/recover/?lang='+lang);self.assertContains(r,'lang="'+lang+'"');self.assertContains(r,'dir="'+('rtl' if lang=='ar' else 'ltr')+'"')
 def test_french_falls_back_english(self):self.assertContains(self.client.get('/store/recover/?lang=fr'),'lang="en"')
 def test_admin_not_public(self):self.assertEqual(self.client.get('/store/admin/').status_code,302)
 def test_webhooks_reject_unsigned(self):
  with patch('orders.payments.stripe_verify',side_effect=ValueError):self.assertEqual(self.client.post('/store/webhooks/stripe/',b'{}',content_type='application/json').status_code,400)
  with patch('orders.payments.paypal_verify',return_value=False):self.assertEqual(self.client.post('/store/webhooks/paypal/',b'{}',content_type='application/json').status_code,400)
 def test_valid_stripe_webhook_and_duplicate(self):
  event={'id':'evt_ok','type':'checkout.session.completed','livemode':False,'data':{'object':{'id':'cs_test_1'}}}
  with patch('orders.payments.stripe_verify',return_value=event),patch('orders.payments.stripe_retrieve',return_value=self.stripe()):
   for _ in range(2):self.assertEqual(self.client.post('/store/webhooks/stripe/',b'{}',content_type='application/json').status_code,200)
  self.assertEqual(DownloadGrant.objects.count(),1)
 def test_paypal_checks_amount_payee_custom_id(self):
  o=Order.objects.create(email='p@example.test',language='ru',provider='paypal',provider_order_id='PP1');self.assertEqual(validate_paypal(o,self.pp(o)),'CAP1')
  for field,value in [('custom_id','other'),('payee',{'merchant_id':'attacker'}),('amount',{'value':'0.01','currency_code':'EUR'})]:
   d=self.pp(o);d['purchase_units'][0][field]=value
   with self.assertRaises(VerificationError):validate_paypal(o,d)
 def test_paypal_verified_webhook_fulfills(self):
  o=Order.objects.create(email='p@example.test',language='ru',provider='paypal',provider_order_id='PP1');event={'id':'ppevt','event_type':'PAYMENT.CAPTURE.COMPLETED','resource':{'id':'CAP1','supplementary_data':{'related_ids':{'order_id':'PP1'}}}}
  with patch('orders.payments.paypal_verify',return_value=True),patch('orders.payments.paypal_retrieve',return_value=self.pp(o)):
   for _ in range(2):self.assertEqual(self.client.post('/store/webhooks/paypal/',json.dumps(event),content_type='application/json').status_code,200)
  self.assertEqual(DownloadGrant.objects.count(),1)
 def test_paypal_return_does_not_capture(self):
  self.assertEqual(self.client.get('/store/paypal/return/?token=PP1').status_code,403);self.assertEqual(DownloadGrant.objects.count(),0)
 def test_email_worker_localized_and_no_duplicate_success(self):
  from django.core import mail
  paid(self.order.id,'evt','stripe','paid');call_command('send_order_emails');call_command('send_order_emails');self.assertEqual(len(mail.outbox),1);self.assertIn('AR',mail.outbox[0].body);self.assertIn('رابط',mail.outbox[0].body)
 def test_security_headers(self):
  r=self.client.get('/store/recover/');self.assertEqual(r['Cache-Control'],'private, no-store');self.assertEqual(r['Referrer-Policy'],'no-referrer');self.assertIn('noindex',r['X-Robots-Tag']);self.assertIn("frame-ancestors 'none'",r['Content-Security-Policy'])
 def test_checkout_server_sets_price_and_language(self):
  with patch('orders.views.ready',return_value=True),patch('orders.payments.stripe_session',return_value={'id':'cs_new','url':'https://checkout.stripe.com/c/pay/cs_new'}) as start:
   r=self.client.post('/store/checkout/?lang=ru',{'name':'Анна Петрова','email':'another@example.test','language':'ru','provider':'stripe','terms':'on','immediate':'on','amount':'1'})
  self.assertEqual(r.status_code,302);o=start.call_args.args[0];self.assertEqual(o.amount_cents,1400);self.assertEqual(o.language,'ru');self.assertEqual(o.mode,'test');self.assertEqual(o.name,'Анна Петрова')
 def test_checkout_requires_separate_consents_and_blocks_honeypot(self):
  with patch('orders.views.ready',return_value=True),patch('orders.payments.stripe_session') as start:
   for data in [{'email':'another@example.test','language':'ru','provider':'stripe','terms':'on'}, {'email':'another@example.test','language':'ru','provider':'stripe','terms':'on','immediate':'on','website':'spam'}]:
    self.assertEqual(self.client.post('/store/checkout/',data).status_code,200)
   start.assert_not_called()
 def test_invalid_language_cannot_create_order(self):
  with patch('orders.views.ready',return_value=True):
   self.client.post('/store/checkout/',{'email':'another@example.test','language':'fr','provider':'stripe','terms':'on','immediate':'on'})
  self.assertEqual(Order.objects.count(),1)
 def test_stripe_sdk_rejects_invalid_signature_without_mock(self):
  with override_settings(STRIPE_WEBHOOK_SECRET='whsec_local_test_only'):
   self.assertEqual(self.client.post('/store/webhooks/stripe/',b'{"id":"fake"}',content_type='application/json',HTTP_STRIPE_SIGNATURE='t=1,v1=invalid').status_code,400)
 def test_stripe_sdk_accepts_valid_local_signature(self):
  import hmac,time
  event={'id':'evt_signed','type':'checkout.session.completed','livemode':False,'data':{'object':{'id':'cs_test_1'}}};raw=json.dumps(event).encode();timestamp=str(int(time.time()));sig=hmac.new(b'whsec_local_test_only',timestamp.encode()+b'.'+raw,hashlib.sha256).hexdigest()
  with override_settings(STRIPE_WEBHOOK_SECRET='whsec_local_test_only'),patch('orders.payments.stripe_retrieve',return_value=self.stripe()):
   r=self.client.post('/store/webhooks/stripe/',raw,content_type='application/json',HTTP_STRIPE_SIGNATURE='t='+timestamp+',v1='+sig)
  self.assertEqual(r.status_code,200);self.assertEqual(DownloadGrant.objects.count(),1)
 def test_paypal_capture_reconciles_lost_response(self):
  o=Order.objects.create(email='p@example.test',language='en',provider='paypal',provider_order_id='PP1');s=self.client.session;s['order_id']=str(o.id);s.save()
  with patch('orders.payments.paypal_capture',side_effect=TimeoutError),patch('orders.payments.paypal_retrieve',return_value=self.pp(o)):
   self.assertEqual(self.client.post('/store/paypal/capture/').status_code,302)
  o.refresh_from_db();self.assertEqual(o.status,'paid')
 def test_refund_webhook_before_checkout_event_remains_revoked(self):
  event={'id':'evt_refund','livemode':False,'type':'charge.refunded','data':{'object':{'payment_intent':'pi_1','amount_refunded':1400}}}
  with patch('orders.payments.stripe_verify',return_value=event),patch('orders.payments.stripe_intent',return_value={'metadata':{'order_id':str(self.order.id)}}):
   self.assertEqual(self.client.post('/store/webhooks/stripe/',b'{}',content_type='application/json').status_code,200)
  self.order.refresh_from_db();self.assertEqual(self.order.status,'refunded')
 def test_confirmation_direct_link_is_checkout_session_bound(self):
  paid(self.order.id,'evt','stripe','paid');s=self.client.session;s['order_id']=str(self.order.id);s.save();self.assertContains(self.client.get('/store/status/'),'/store/download/')
  self.assertNotContains(Client().get('/store/status/'),'/store/download/')
 def test_mail_worker_refreshes_an_expired_unsent_link(self):
  paid(self.order.id,'evt','stripe','paid');DownloadGrant.objects.update(expires_at=timezone.now()-timedelta(days=1));old=EmailJob.objects.get().link;call_command('send_order_emails');self.assertNotEqual(EmailJob.objects.get().link,old)
 def test_verified_paypal_reversal_revokes_capture(self):
  o=Order.objects.create(email='p@example.test',language='en',provider='paypal',provider_order_id='PP1',capture_id='CAP1');paid(o.id,'paid','paypal','capture')
  event={'id':'reverse','event_type':'PAYMENT.CAPTURE.REVERSED','resource':{'id':'CAP1'}}
  with patch('orders.payments.paypal_verify',return_value=True):self.assertEqual(self.client.post('/store/webhooks/paypal/',json.dumps(event),content_type='application/json').status_code,200)
  o.refresh_from_db();self.assertEqual(o.status,'refunded');self.assertTrue(DownloadGrant.objects.get().revoked)
