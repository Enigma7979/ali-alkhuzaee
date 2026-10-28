from django.contrib import admin
from .models import Order,PaymentEvent,DownloadGrant,EmailJob
class ReadOnly(admin.ModelAdmin):
 def has_add_permission(self,request):return False
 def has_delete_permission(self,request,obj=None):return False
 def get_readonly_fields(self,request,obj=None):return [f.name for f in self.model._meta.fields]
@admin.register(Order)
class OrderAdmin(ReadOnly):
 list_display=['id','created_at','provider','language','mode','status','fulfilled_at'];list_filter=['status','mode','provider','language'];search_fields=['email','name','id','provider_order_id'];ordering=['-created_at']
@admin.register(PaymentEvent)
class EventAdmin(ReadOnly):list_display=['provider','kind','event_id','created_at']
@admin.register(DownloadGrant)
class GrantAdmin(ReadOnly):list_display=['order','expires_at','revoked','downloads'];exclude=['token_hash']
@admin.register(EmailJob)
class JobAdmin(ReadOnly):list_display=['order','kind','sent_at','attempts'];exclude=['link']
