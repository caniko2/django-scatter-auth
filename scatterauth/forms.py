from scatterauth.settings import app_settings

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    nonce = forms.CharField(widget=forms.HiddenInput, max_length=12)
    public_key = forms.CharField(widget=forms.HiddenInput, max_length=53)
    res = forms.CharField(widget=forms.HiddenInput, max_length=101)

    # def clean_signature(self):
    #     sig = self.cleaned_data['signature']
    #     if len(sig) != 101:
    #         raise forms.ValidationError(_('Invalid signature'))
    #     return sig


# list(set()) here is to eliminate the possibility of double including the address field
signup_fields = list(set(app_settings.SCATTERAUTH_USER_SIGNUP_FIELDS + [app_settings.SCATTERAUTH_USER_PUBKEY_FIELD]))


class SignupForm(forms.ModelForm):
    def clean_address_field(self):
        # validate_eth_address(self.cleaned_data[app_settings.SCATTERAUTH_USER_PUBKEY_FIELD])
        return self.cleaned_data[app_settings.SCATTERAUTH_USER_PUBKEY_FIELD]

    class Meta:
        model = get_user_model()
        fields = signup_fields


# hack to set the method for cleaning address field
setattr(SignupForm, 'clean_' + app_settings.SCATTERAUTH_USER_PUBKEY_FIELD, SignupForm.clean_address_field)
