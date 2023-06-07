from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Comment

PILIHAN_PEMBAYARAN = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
)

class CheckoutForm(forms.Form):
    alamat_1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Alamat Anda', 'class': 'textinput form-control'}))
    alamat_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartement, Rumah, atau yang lain (opsional)', 'class': 'textinput form-control'}))
    negara = CountryField(blank_label='(Pilih Negara)').formfield(widget=CountrySelectWidget(attrs={'class': 'countryselectwidget form-select'}))
    kode_pos = forms.CharField(widget=forms.TextInput(attrs={'class': 'textinput form-control', 'placeholder': 'Kode Pos'}))
    simpan_info_alamat = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    opsi_pembayaran = forms.ChoiceField(widget=forms.RadioSelect(), choices=PILIHAN_PEMBAYARAN)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

class ContactForm(forms.Form):
    from_email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            'placeholder': 'name@mail.com', 
            'class': 'form-control"',
            'id':'email'
            })
        , required=True, max_length=100)
    subject = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Subject..', 
            'class': 'form-control"',
            'id': 'subject'
            })
        , required=True, max_length=100)
    message = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': 'Masukkan pesan disini..', 
            'class': 'form-control"', 
            'cols':'30',
            'rows': '5',
            'id': 'message'
            })
        , required=True)