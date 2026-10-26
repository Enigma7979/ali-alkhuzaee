from django.utils import translation
class Locale:
 def __init__(self,get_response):self.get_response=get_response
 def __call__(self,request):
  lang=request.GET.get('lang') or request.session.get('ali-language','en')
  if lang not in ('ar','en','ru'):lang='en'
  request.LANGUAGE_CODE=lang;request.session['ali-language']=lang
  with translation.override(lang):return self.get_response(request)
class Security:
 def __init__(self,get_response):self.get_response=get_response
 def __call__(self,request):
  r=self.get_response(request)
  r['Cache-Control']='private, no-store';r['Referrer-Policy']='no-referrer';r['X-Robots-Tag']='noindex, nofollow'
  r['Content-Security-Policy']="default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self'; script-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; object-src 'none'"
  return r
