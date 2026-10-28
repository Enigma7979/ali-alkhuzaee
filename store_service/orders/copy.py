import json
from django.conf import settings
COPY=json.loads((settings.ROOT/'assets/products/translations.json').read_text())
def context(request):
 lang=getattr(request,'LANGUAGE_CODE','en')
 return {'c':COPY[lang],'lang':lang,'rtl':lang=='ar','price':'%.2f'%(settings.PRICE_CENTS/100)}
