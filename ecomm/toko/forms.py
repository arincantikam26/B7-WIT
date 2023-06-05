from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PILIHAN_PEMBAYARAN = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
)

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','password1', 'password2', )

class CheckoutForm(forms.Form):
    alamat_1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Alamat Anda', 'class': 'textinput form-control'}))
    alamat_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartement, Rumah, atau yang lain (opsional)', 'class': 'textinput form-control'}))
    negara = CountryField(blank_label='(Pilih Negara)').formfield(widget=CountrySelectWidget(attrs={'class': 'countryselectwidget form-select'}))
    kode_pos = forms.CharField(widget=forms.TextInput(attrs={'class': 'textinput form-outline', 'placeholder': 'Kode Pos'}))
    simpan_info_alamat = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    opsi_pembayaran = forms.ChoiceField(widget=forms.RadioSelect(), choices=PILIHAN_PEMBAYARAN)