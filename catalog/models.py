from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from django.utils.text import slugify
import qrcode
from io import BytesIO
from uuid import uuid4


class Book(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class StudentProfile(models.Model):
    full_name = models.CharField(max_length=180)
    classroom = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to='students/faces/', blank=True, null=True)
    face_signature = models.JSONField(blank=True, null=True)
    assigned_books = models.ManyToManyField(Book, related_name='assigned_students', blank=True)
    access_code_lookup = models.CharField(max_length=64, unique=True, blank=True, null=True)
    access_code_hash = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class StudentSession(models.Model):
    student = models.ForeignKey(StudentProfile, related_name='sessions', on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


class StudentReadingProgress(models.Model):
    student = models.ForeignKey(StudentProfile, related_name='reading_progress', on_delete=models.CASCADE)
    scene = models.ForeignKey('Scene', related_name='student_progress', on_delete=models.CASCADE)
    last_opened_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'scene'], name='unique_student_scene_progress'),
        ]


class Scene(models.Model):
    book = models.ForeignKey(Book, related_name='scenes', on_delete=models.CASCADE)
    title = models.CharField(max_length=180, blank=True)
    order = models.PositiveIntegerField(default=1)
    text = models.TextField()
    audio = models.FileField(upload_to='scenes/audio/', blank=True, null=True)
    glb_model = models.FileField(upload_to='scenes/models/', blank=True, null=True)
    prefab_key = models.CharField(max_length=120, blank=True, default='')
    qr_code = models.CharField(max_length=80, unique=True, blank=True)
    qr_image = models.ImageField(upload_to='scenes/qr/', blank=True, null=True)
    ar_marker_width_cm = models.FloatField(default=6.0, validators=[MinValueValidator(2), MaxValueValidator(30)])
    ar_model_size_cm = models.FloatField(default=8.0, validators=[MinValueValidator(1), MaxValueValidator(50)])
    ar_offset_x_cm = models.FloatField(default=0.0, validators=[MinValueValidator(-50), MaxValueValidator(50)])
    ar_offset_y_cm = models.FloatField(default=0.5, validators=[MinValueValidator(-50), MaxValueValidator(50)])
    ar_offset_z_cm = models.FloatField(default=0.0, validators=[MinValueValidator(-50), MaxValueValidator(50)])
    ar_yaw_degrees = models.FloatField(default=0.0, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['book', 'order', 'id']

    def __str__(self):
        label = self.title or f'Escena {self.order}'
        return f'{self.book.title} - {label}'

    def save(self, *args, **kwargs):
        if not self.qr_code:
            base = slugify(self.book.title)[:32] if self.book_id else 'book'
            self.qr_code = f'{base}-scene-{uuid4().hex[:10]}'

        if not self.qr_image or self._qr_code_changed():
            self.qr_image.save(
                f'{self.qr_code}.png',
                self._build_qr_file(),
                save=False,
            )

        super().save(*args, **kwargs)

    def _qr_code_changed(self):
        if not self.pk:
            return False

        old_qr_code = (
            Scene.objects
            .filter(pk=self.pk)
            .values_list('qr_code', flat=True)
            .first()
        )
        return old_qr_code is not None and old_qr_code != self.qr_code

    def _build_qr_file(self):
        image = qrcode.make(self.qr_code)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue())
