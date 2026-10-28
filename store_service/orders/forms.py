from django import forms
class CheckoutForm(forms.Form):
 name=forms.CharField(max_length=80)
 email=forms.EmailField(max_length=254)
 language=forms.ChoiceField(choices=[('en','English'),('ar','العربية'),('ru','Русский')])
 provider=forms.ChoiceField(choices=[('stripe','Stripe'),('paypal','PayPal')])
 terms=forms.BooleanField()
 immediate=forms.BooleanField()
 website=forms.CharField(required=False,widget=forms.HiddenInput)
class RecoveryForm(forms.Form):email=forms.EmailField(max_length=254)
