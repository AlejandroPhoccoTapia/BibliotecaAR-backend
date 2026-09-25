"""Local-only test configuration: never connect to production DB or storage."""
import tempfile

from .settings import *  # noqa: F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
_test_media = tempfile.TemporaryDirectory(prefix='bibliotecaar-tests-')
MEDIA_ROOT = _test_media.name
USE_SUPABASE_STORAGE = False
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
