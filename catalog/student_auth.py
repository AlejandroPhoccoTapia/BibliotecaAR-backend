import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from .models import StudentProfile, StudentSession


ACCESS_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
ACCESS_CODE_LENGTH = 6
LEGACY_ACCESS_CODE_LENGTH = 10
SESSION_LIFETIME = timedelta(days=30)


def normalize_access_code(value):
    return ''.join(character for character in str(value or '').upper() if character not in ' -')


def access_code_lookup(code):
    return hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        code.encode('ascii'),
        hashlib.sha256,
    ).hexdigest()


@transaction.atomic
def reset_student_access_code(student):
    for _ in range(5):
        code = ''.join(secrets.choice(ACCESS_ALPHABET) for _ in range(ACCESS_CODE_LENGTH))
        lookup = access_code_lookup(code)
        if not StudentProfile.objects.filter(access_code_lookup=lookup).exists():
            break
    else:
        raise RuntimeError('No se pudo generar un código de acceso único.')

    student.access_code_lookup = lookup
    student.access_code_hash = make_password(code)
    student.save(update_fields=['access_code_lookup', 'access_code_hash', 'updated_at'])
    student.sessions.all().delete()
    return code


def authenticate_student_code(value):
    code = normalize_access_code(value)
    if len(code) not in (ACCESS_CODE_LENGTH, LEGACY_ACCESS_CODE_LENGTH) or any(character not in ACCESS_ALPHABET for character in code):
        return None
    student = StudentProfile.objects.filter(
        access_code_lookup=access_code_lookup(code), is_active=True,
    ).first()
    if student and check_password(code, student.access_code_hash):
        return student
    return None


def issue_student_token(student):
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + SESSION_LIFETIME
    StudentSession.objects.create(
        student=student,
        token_hash=hashlib.sha256(token.encode('ascii')).hexdigest(),
        expires_at=expires_at,
    )
    return token, expires_at


class StudentBearerAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        if not header:
            return None
        scheme, separator, token = header.partition(' ')
        if scheme.lower() != 'bearer' or not separator or not token.strip():
            raise AuthenticationFailed('Se necesita una sesión de estudiante válida.')

        token_hash = hashlib.sha256(token.strip().encode('utf-8')).hexdigest()
        session = StudentSession.objects.select_related('student').filter(token_hash=token_hash).first()
        if not session or session.expires_at <= timezone.now() or not session.student.is_active:
            raise AuthenticationFailed('La sesión de estudiante venció. Vuelve a entrar.')
        return session.student, session

    def authenticate_header(self, request):
        return 'Bearer'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, StudentProfile) and request.user.is_active
