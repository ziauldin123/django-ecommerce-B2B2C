from dataclasses import field
from pyexpat import model
from django import forms

from apps.ordering.models import Order

from .models import District, Sector, Cell, Village


class CheckoutForm(forms.Form):
    def __init__(self, use_vendor_delivery=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if use_vendor_delivery:
            choices = [
                ('Store', 'Pick up from Store'),
                ('Vendor', 'Vendor Delivery'),
            ]
        else:
            choices = [
                ('Store', 'Pick up from Store'),
                ('Basic_Delivery', 'Basic delivery'),
                ('Express_Delivery', 'Express delivery'),
            ]
        self.fields['delivery_option'].choices = choices

        address_required = not use_vendor_delivery
        print('addr req: ', address_required, use_vendor_delivery)
        self.fields['district'].required = address_required
        self.fields['sector'].required = address_required
        self.fields['cell'].required = address_required
        self.fields['village'].required = address_required
        self.fields['delivery_address'].required = address_required

    district = forms.ChoiceField(choices=[
                                 (-1, '')] + [(entry.id, entry.district) for entry in District.objects.all()])

    sector = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.sector) for entry in Sector.objects.all()])

    cell = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.cell) for entry in Cell.objects.all()])

    village = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.village) for entry in Village.objects.all()])

    delivery_address = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 2, 'cols': 85}), max_length=170)

    delivery_option = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[]
    )



class PaymentForm(forms.Form):
    service_provider = forms.CharField()
    phone_number = forms.CharField()