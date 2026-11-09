from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['plan', 'payment_method', 'phone_number']
        widgets = {
            'payment_method': forms.Select(choices=[
                ('', 'Select Method'),
                ('mpesa', 'M-Pesa'),
                ('tigopesa', 'Tigo Pesa'),
                ('airtelmoney', 'Airtel Money'),
                ('halopesa', 'Halo Pesa'),
                ('bank', 'Bank Transfer'),
            ]),
        }
