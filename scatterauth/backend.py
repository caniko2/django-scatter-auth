from django.contrib.auth import get_user_model, backends

from scatterauth.utils import validate_signature, InvalidSignatureException
from scatterauth.settings import app_settings

class ScatterAuthBackend(backends.ModelBackend):
    def authenticate(self, public_key, msg, signed_msg):
        User = get_user_model()
        print(public_key)
        print(msg)
        print(signed_msg)
        # check if the address the user has provided matches the signature
        msg = user_utils.sign_data_for_desktop(msg, public_key)
        is_valid = validate_signature(public_key=public_key, msg=msg, signed_msg=signed_msg)

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
