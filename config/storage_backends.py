from urllib.parse import urljoin

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class SupabaseMediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False

    def url(self, name, parameters=None, expire=None, http_method=None):
        public_base_url = getattr(settings, 'SUPABASE_STORAGE_PUBLIC_URL', '').rstrip('/')
        if not public_base_url:
            return super().url(name, parameters=parameters, expire=expire, http_method=http_method)

        clean_name = self._normalize_name(self._clean_name(name)).lstrip('/')
        return urljoin(f'{public_base_url}/', clean_name)
