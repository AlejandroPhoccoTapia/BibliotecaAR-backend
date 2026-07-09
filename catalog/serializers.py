from rest_framework import serializers
from django.contrib.auth import get_user_model

from .face_recognition import FaceRecognitionError, build_face_signature
from .models import Book, Scene, StudentProfile


class FileUrlMixin:
    def _absolute_file_url(self, file_field):
        if not file_field:
            return None

        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return file_field.url


class TeacherRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError('Este usuario ya existe.')
        return value

    def create(self, validated_data):
        return get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=True,
        )


class TeacherSceneSerializer(FileUrlMixin, serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    audio_url = serializers.SerializerMethodField()
    glb_model_name = serializers.SerializerMethodField()
    glb_model_url = serializers.SerializerMethodField()
    qr_image_url = serializers.SerializerMethodField()
    remove_glb_model = serializers.BooleanField(write_only=True, required=False, default=False)

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
            'glb_model_name',
            'glb_model_url',
            'remove_glb_model',
            'prefab_key',
            'qr_code',
            'qr_image_url',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('qr_code', 'created_at', 'updated_at')

    def get_audio_url(self, obj):
        return self._absolute_file_url(obj.audio)

    def get_glb_model_name(self, obj):
        if not obj.glb_model:
            return None
        return obj.glb_model.name.rsplit('/', 1)[-1]

    def get_glb_model_url(self, obj):
        return self._absolute_file_url(obj.glb_model)

    def get_qr_image_url(self, obj):
        return self._absolute_file_url(obj.qr_image)

    def create(self, validated_data):
        validated_data.pop('remove_glb_model', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove_glb_model = validated_data.pop('remove_glb_model', False)

        if remove_glb_model and 'glb_model' not in validated_data:
            instance.glb_model.delete(save=False)
            instance.glb_model = None

        return super().update(instance, validated_data)


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


class TeacherStudentSerializer(FileUrlMixin, serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    assigned_books = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Book.objects.all(),
        required=False,
    )
    assigned_books_detail = TeacherBookSerializer(
        source='assigned_books',
        many=True,
        read_only=True,
    )
    has_face_signature = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            'id',
            'full_name',
            'classroom',
            'photo',
            'photo_url',
            'assigned_books',
            'assigned_books_detail',
            'has_face_signature',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_photo_url(self, obj):
        return self._absolute_file_url(obj.photo)

    def get_has_face_signature(self, obj):
        return bool(obj.face_signature)

    def create(self, validated_data):
        assigned_books = validated_data.pop('assigned_books', [])
        self._attach_face_signature(validated_data)
        student = super().create(validated_data)
        student.assigned_books.set(assigned_books)
        return student

    def update(self, instance, validated_data):
        assigned_books = validated_data.pop('assigned_books', None)
        self._attach_face_signature(validated_data)
        student = super().update(instance, validated_data)

        if assigned_books is not None:
            student.assigned_books.set(assigned_books)

        return student

    def _attach_face_signature(self, validated_data):
        photo = validated_data.get('photo')
        if not photo:
            return

        try:
            validated_data['face_signature'] = build_face_signature(photo)
        except FaceRecognitionError as exc:
            raise serializers.ValidationError({'photo': str(exc)}) from exc


class StudentAssignedBookSerializer(FileUrlMixin, serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'description',
            'cover_url',
        )

    def get_cover_url(self, obj):
        return self._absolute_file_url(obj.cover)


class StudentFaceLoginSerializer(serializers.Serializer):
    image = serializers.ImageField()


class StudentFaceLoginResultSerializer(FileUrlMixin, serializers.Serializer):
    student = serializers.SerializerMethodField()
    confidence = serializers.FloatField()
    distance = serializers.FloatField()

    def get_student(self, obj):
        student = obj['student']
        return {
            'id': student.id,
            'full_name': student.full_name,
            'classroom': student.classroom,
            'photo_url': self._absolute_file_url(student.photo),
            'assigned_books': StudentAssignedBookSerializer(
                student.assigned_books.all(),
                many=True,
                context=self.context,
            ).data,
        }


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
