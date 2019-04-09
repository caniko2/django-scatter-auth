from django.contrib.auth import get_user_model, backends

from scatterauth.utils import validate_signature, sign_data, InvalidSignatureException
from scatterauth.settings import app_settings

class ScatterAuthBackend(backends.ModelBackend):
    def authenticate(self, request, public_key, nonce, res):
        User = get_user_model()
        # check if the address the user has provided matches the signature
        shaData = sign_data("helloworldiamtheonethatknocks", nonce)
        print('public_key:', public_key)
        print('nonce:', nonce)
        print('res:', res)
        print('shaData:', shaData)
        is_valid = validate_signature(public_key=public_key, shaData=shaData, res=res)

        if not is_valid:
            return None
        else:
            # get public_key field for the user model
            pubkey_field = app_settings.SCATTERAUTH_USER_PUBKEY_FIELD
            kwargs = {
                pubkey_field+"__iexact": public_key
            }
            # try to get user with provided data
            user = User.objects.filter(**kwargs).first()
            return user
