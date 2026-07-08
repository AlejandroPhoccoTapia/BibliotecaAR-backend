from rest_framework import serializers

from .models import Book, Scene


class FileUrlMixin:
    def _absolute_file_url(self, file_field):
        if not file_field:
            return None

        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return file_field.url


class TeacherSceneSerializer(FileUrlMixin, serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    audio_url = serializers.SerializerMethodField()
    glb_model_url = serializers.SerializerMethodField()
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Scene
        fields = (
            'id',
            'book',
            'book_title',
            'title',
            'order',
            'text',
            'audio',
            'audio_url',
            'glb_model',
            'glb_model_url',
            'prefab_key',
            'qr_code',
            'qr_image_url',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('qr_code', 'created_at', 'updated_at')

    def get_audio_url(self, obj):
        return self._absolute_file_url(obj.audio)

    def get_glb_model_url(self, obj):
        return self._absolute_file_url(obj.glb_model)

    def get_qr_image_url(self, obj):
        return self._absolute_file_url(obj.qr_image)


class TeacherBookSerializer(FileUrlMixin, serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    scenes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'description',
            'cover',
            'cover_url',
            'is_published',
            'scenes_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_cover_url(self, obj):
        return self._absolute_file_url(obj.cover)


class UnitySceneSerializer(FileUrlMixin, serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title')
    cover_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    glb_model_url = serializers.SerializerMethodField()
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Scene
        fields = (
            'qr_code',
            'book_title',
            'title',
            'order',
            'text',
            'prefab_key',
            'cover_url',
            'audio_url',
            'glb_model_url',
            'qr_image_url',
        )

    def get_cover_url(self, obj):
        return self._absolute_file_url(obj.book.cover)

    def get_audio_url(self, obj):
        return self._absolute_file_url(obj.audio)

    def get_glb_model_url(self, obj):
        return self._absolute_file_url(obj.glb_model)

    def get_qr_image_url(self, obj):
        return self._absolute_file_url(obj.qr_image)
