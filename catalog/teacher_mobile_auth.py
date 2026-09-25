from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.crypto import constant_time_compare
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


TOKEN_SALT = 'catalog.teacher.ar-preview.v1'
TOKEN_MAX_AGE_SECONDS = 30 * 60


def issue_teacher_mobile_token(user):
    return signing.dumps(
        {'user_id': user.pk, 'password_hash': user.password},
        salt=TOKEN_SALT,
        compress=True,
    )


class TeacherMobileAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization', '')
        if not header.startswith('TeacherPreview '):
            return None

        token = header[len('TeacherPreview '):].strip()
        try:
            payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
            user = get_user_model().objects.get(pk=payload['user_id'])
        except (signing.BadSignature, KeyError, ValueError, TypeError, get_user_model().DoesNotExist) as exc:
            raise AuthenticationFailed('Vista docente caducada o inválida.') from exc

        if not user.is_active or not user.is_staff or not constant_time_compare(
            user.password, payload.get('password_hash', ''),
        ):
            raise AuthenticationFailed('Vista docente caducada o inválida.')
        return user, None

    def authenticate_header(self, request):
        return 'TeacherPreview'
