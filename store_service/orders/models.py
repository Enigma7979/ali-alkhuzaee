import uuid
from django.db import models
from django.utils import timezone
class Order(models.Model):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 email=models.EmailField()
 # Printed with the email on every page of the delivered PDF (orders/stamp.py).
 name=models.CharField(max_length=80,blank=True,default='')
 language=models.CharField(max_length=2,choices=[('en','English'),('ar','العربية'),('ru','Русский')])
 product=models.CharField(max_length=60,default='creator-guide')
 provider=models.CharField(max_length=10,choices=[('stripe','Stripe'),('paypal','PayPal')])
 mode=models.CharField(max_length=4,default='test')
 status=models.CharField(max_length=15,choices=[('pending','Pending'),('paid','Paid'),('refunded','Refunded'),('disputed','Disputed'),('failed','Failed')],default='pending',db_index=True)
 amount_cents=models.PositiveIntegerField(default=1400)
 currency=models.CharField(max_length=3,default='EUR')
 provider_order_id=models.CharField(max_length=255,unique=True,null=True,blank=True)
 capture_id=models.CharField(max_length=255,unique=True,null=True,blank=True)
 created_at=models.DateTimeField(default=timezone.now,db_index=True)
 fulfilled_at=models.DateTimeField(null=True,blank=True)
 consent_at=models.DateTimeField(default=timezone.now)
 terms_version=models.CharField(max_length=30,default='draft-v1')
 @property
 def licence_ref(self):return str(self.id)[:8].upper()
class PaymentEvent(models.Model):
 provider=models.CharField(max_length=10)
 event_id=models.CharField(max_length=255)
 order=models.ForeignKey(Order,on_delete=models.PROTECT)
 kind=models.CharField(max_length=100)
 created_at=models.DateTimeField(default=timezone.now)
 class Meta:constraints=[models.UniqueConstraint(fields=['provider','event_id'],name='one_payment_event')]
class DownloadGrant(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE)
 token_hash=models.CharField(max_length=64,unique=True)
 expires_at=models.DateTimeField()
 revoked=models.BooleanField(default=False)
 downloads=models.PositiveIntegerField(default=0)
class EmailJob(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE)
 kind=models.CharField(max_length=40)
 # Signed link is held only in private DB, never in logs or public source.
 link=models.TextField()
 sent_at=models.DateTimeField(null=True,blank=True)
 attempts=models.PositiveIntegerField(default=0)
 created_at=models.DateTimeField(default=timezone.now)
 class Meta:constraints=[models.UniqueConstraint(fields=['order','kind'],name='unique_order_email')]
class RateBucket(models.Model):
 key=models.CharField(max_length=64,primary_key=True)
 hits=models.PositiveIntegerField(default=0)
 expires_at=models.DateTimeField(db_index=True)
