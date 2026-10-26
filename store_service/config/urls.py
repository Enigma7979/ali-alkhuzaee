from django.contrib import admin
from django.urls import path
from orders import views as v
urlpatterns=[path('store/availability/',v.availability),path('store/checkout/',v.checkout),path('store/status/',v.status),path('store/cancel/',v.cancel),path('store/paypal/return/',v.paypal_return),path('store/paypal/capture/',v.capture),path('store/webhooks/stripe/',v.stripe_webhook),path('store/webhooks/paypal/',v.paypal_webhook),path('store/download/<str:token>/',v.download_page),path('store/download/<str:token>/file/',v.download_file),path('store/recover/',v.recover),path('store/admin/',admin.site.urls)]
