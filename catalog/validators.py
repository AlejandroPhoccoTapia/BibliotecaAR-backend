"""Cheap upload checks before writing files to local or remote storage."""
from pathlib import Path
import struct

from django.conf import settings
from rest_framework import serializers


def validate_size(upload, setting, default_mb):
    limit = getattr(settings, setting, default_mb * 1024 * 1024)
    if upload.size > limit:
        raise serializers.ValidationError(f'El archivo supera el límite de {limit // (1024 * 1024)} MB.')
    return upload


def validate_image_upload(upload):
    return validate_size(upload, 'MAX_IMAGE_UPLOAD_BYTES', 10)


def validate_audio_upload(upload):
    validate_size(upload, 'MAX_AUDIO_UPLOAD_BYTES', 50)
    if Path(upload.name).suffix.lower() not in {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}:
        raise serializers.ValidationError('Usa audio MP3, WAV, OGG, M4A, AAC o FLAC.')
    return upload


def validate_glb_upload(upload):
    validate_size(upload, 'MAX_GLB_UPLOAD_BYTES', 100)
    if Path(upload.name).suffix.lower() != '.glb':
        raise serializers.ValidationError('El modelo debe ser un archivo .glb.')
    position = upload.tell()
    try:
        upload.seek(0)
        header = upload.read(12)
    finally:
        upload.seek(position)
    if len(header) != 12:
        raise serializers.ValidationError('El archivo GLB está incompleto.')
    magic, version, length = struct.unpack('<4sII', header)
    if magic != b'glTF' or version != 2 or length != upload.size or length < 20:
        raise serializers.ValidationError('La cabecera GLB no es válida o el archivo está incompleto.')
    return upload
