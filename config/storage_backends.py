from urllib.parse import quote, urljoin

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class SupabaseMediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False

    def url(self, name, parameters=None, expire=None, http_method=None):
        public_base_url = getattr(settings, 'SUPABASE_STORAGE_PUBLIC_URL', '').rstrip('/')
        if not public_base_url:
            return super().url(name, parameters=parameters, expire=expire, http_method=http_method)

        clean_name = str(name).replace('\\', '/').lstrip('/')
        return urljoin(f'{public_base_url}/', quote(clean_name))
