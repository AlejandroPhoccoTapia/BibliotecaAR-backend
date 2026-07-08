from django.db import models
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


class Scene(models.Model):
    book = models.ForeignKey(Book, related_name='scenes', on_delete=models.CASCADE)
    title = models.CharField(max_length=180, blank=True)
    order = models.PositiveIntegerField(default=1)
    text = models.TextField()
    audio = models.FileField(upload_to='scenes/audio/', blank=True, null=True)
    glb_model = models.FileField(upload_to='scenes/models/', blank=True, null=True)
    prefab_key = models.CharField(max_length=120)
    qr_code = models.CharField(max_length=80, unique=True, blank=True)
    qr_image = models.ImageField(upload_to='scenes/qr/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['book', 'order', 'id']

    def __str__(self):
        label = self.title or f'Escena {self.order}'
        return f'{self.book.title} - {label}'

    def save(self, *args, **kwargs):
        old_glb_model = self._old_file_name('glb_model')

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
        self._delete_replaced_file(old_glb_model, self.glb_model)

    def delete(self, *args, **kwargs):
        glb_model = self.glb_model
        super().delete(*args, **kwargs)
        self._delete_file(glb_model)

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

    def _old_file_name(self, field_name):
        if not self.pk:
            return None

        return (
            Scene.objects
            .filter(pk=self.pk)
            .values_list(field_name, flat=True)
            .first()
        )

    def _delete_replaced_file(self, old_name, current_file):
        if old_name and old_name != current_file.name:
            self._delete_file_by_name(old_name)

    def _delete_file(self, file_field):
        if file_field:
            self._delete_file_by_name(file_field.name)

    def _delete_file_by_name(self, file_name):
        if self.glb_model.storage.exists(file_name):
            self.glb_model.storage.delete(file_name)
