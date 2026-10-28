"""Provider adapters. No browser success parameter can mark an order paid."""
import requests
import stripe
from django.conf import settings
class ProviderError(Exception):pass
def stripe_session(order):
 stripe.api_key=settings.STRIPE_SECRET_KEY
 return stripe.checkout.Session.create(mode='payment',payment_method_types=['card'],customer_email=order.email,line_items=[{'price_data':{'currency':'eur','unit_amount':settings.PRICE_CENTS,'tax_behavior':'inclusive','product_data':{'name':'From Zero to Hero / '+order.language.upper()}},'quantity':1}],metadata={'order_id':str(order.id),'language':order.language,'product':'creator-guide'},payment_intent_data={'metadata':{'order_id':str(order.id),'language':order.language,'product':'creator-guide'}},client_reference_id=str(order.id),success_url=settings.PUBLIC_ORIGIN+'/store/status/?lang='+order.language,cancel_url=settings.PUBLIC_ORIGIN+'/store/cancel/?lang='+order.language,billing_address_collection='required',idempotency_key='checkout-'+str(order.id)).to_dict()
def stripe_retrieve(session_id):
 stripe.api_key=settings.STRIPE_SECRET_KEY
 return stripe.checkout.Session.retrieve(session_id,expand=['payment_intent.latest_charge']).to_dict()
def stripe_verify(raw,signature):return stripe.Webhook.construct_event(raw,signature,settings.STRIPE_WEBHOOK_SECRET).to_dict()
def pp_token():
 r=requests.post(settings.PAYPAL_ORIGIN+'/v1/oauth2/token',auth=(settings.PAYPAL_CLIENT_ID,settings.PAYPAL_CLIENT_SECRET),data={'grant_type':'client_credentials'},timeout=15);r.raise_for_status();return r.json()['access_token']
def pp(method,path,data=None,key=None):
 headers={'Authorization':'Bearer '+pp_token(),'Content-Type':'application/json'}
 if key:headers['PayPal-Request-Id']=key
 r=requests.request(method,settings.PAYPAL_ORIGIN+path,headers=headers,json=data,timeout=20);r.raise_for_status();return r.json()
def paypal_create(order):
 return pp('POST','/v2/checkout/orders',{'intent':'CAPTURE','purchase_units':[{'reference_id':str(order.id),'custom_id':str(order.id),'invoice_id':str(order.id),'payee':{'merchant_id':settings.PAYPAL_MERCHANT_ID},'amount':{'currency_code':'EUR','value':'%.2f'%(settings.PRICE_CENTS/100)},'description':'From Zero to Hero / '+order.language.upper()}],'payment_source':{'paypal':{'experience_context':{'shipping_preference':'NO_SHIPPING','user_action':'PAY_NOW','return_url':settings.PUBLIC_ORIGIN+'/store/paypal/return/?lang='+order.language,'cancel_url':settings.PUBLIC_ORIGIN+'/store/cancel/?lang='+order.language}}}},'create-'+str(order.id))
def paypal_capture(provider_id,order_id):return pp('POST','/v2/checkout/orders/'+provider_id+'/capture',{},'capture-'+str(order_id))
def paypal_retrieve(provider_id):return pp('GET','/v2/checkout/orders/'+provider_id)
def paypal_verify(event,headers):
 fields={'transmission_id':'PAYPAL-TRANSMISSION-ID','transmission_time':'PAYPAL-TRANSMISSION-TIME','cert_url':'PAYPAL-CERT-URL','auth_algo':'PAYPAL-AUTH-ALGO','transmission_sig':'PAYPAL-TRANSMISSION-SIG'}
 if not all(headers.get(h) for h in fields.values()):return False
 body={k:headers.get(h) for k,h in fields.items()};body.update(webhook_id=settings.PAYPAL_WEBHOOK_ID,webhook_event=event)
 return pp('POST','/v1/notifications/verify-webhook-signature',body).get('verification_status')=='SUCCESS'

def stripe_intent(intent_id):
 stripe.api_key=settings.STRIPE_SECRET_KEY
 return stripe.PaymentIntent.retrieve(intent_id).to_dict()
