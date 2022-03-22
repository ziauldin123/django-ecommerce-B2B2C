from collections import defaultdict

from django import forms

from apps.newProduct.models import Length, Product


class BaseProductVariantsForm:
    def fill_form_variants(self, products, none_needed=True):
        filters_list = products.values('keywords',)

        filters_dict = defaultdict(list)
        for d in filters_list:
            for k, v in d.items():
                if v:
                    filters_dict[k].append((v, v))
                elif not v and not filters_dict.get(k):
                    filters_dict[k] = []

        filters_dict = {k: list(set(v)) for k, v in filters_dict.items()}

        for k, v in filters_dict.items():
            if v:
                if none_needed:
                    v.append((None, None))
                self.fields[k].choices = v
                if not none_needed:
                    self.fields[k].initial = v[0]
            else:
                self.fields.pop(k)


class TestForm(forms.Form):
    color = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[('a', 'a'), ('b', 'b')],
    )


class AddToCartForm(forms.Form, BaseProductVariantsForm):
    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products') if kwargs.get('products') is not None else Product.objects.none()
        super().__init__(*args, **kwargs)
        self.fill_form_variants(products, False)

    quantity = forms.IntegerField()
    brand = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )
    color = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )
    weight = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )
    size = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )


class AddToCartInListForm(forms.Form):
    slug = forms.CharField(max_length=50)




class SearchForm(forms.Form, BaseProductVariantsForm):
    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products') if kwargs.get('products') is not None else Product.objects.all()
        super().__init__(*args, **kwargs)


    query = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'input'}), required=False)
    instock = forms.BooleanField(required=False)
    price_from = forms.IntegerField(initial=0, required=False, widget=forms.TextInput(attrs={'class': 'input'}))
    price_to = forms.IntegerField(initial=5000000, required=False, widget=forms.TextInput(attrs={'class': 'input'}))

    # brand = []
    color = forms.CharField(widget=forms.Select(),required=False)
    weight = forms.CharField(widget=forms.Select(),required=False)
    size = forms.CharField(widget=forms.Select(),required=False)
    height = forms.CharField(widget=forms.Select(),required=False)
    length = forms.CharField(widget=forms.Select(),required=False)
    width = forms.CharField(widget=forms.Select(),required=False)


    def clean_price_to(self) -> int:
        price_to = self.cleaned_data['price_to']
        if price_to is None:
            return 500000
        return price_to

    def clean_price_from(self) -> int:
        price_from = self.cleaned_data['price_from']
        if price_from is None:
            return 0
        return price_from
