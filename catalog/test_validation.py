from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .face_recognition import FaceRecognitionError, compare_signatures
from .models import Book, Scene
from .tests import glb_test_content
from .validators import validate_glb_upload


class UploadValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_login(get_user_model().objects.create_user('teacher', is_staff=True))
        self.book = Book.objects.create(title='Demo')

    def create_scene(self, **extra):
        return self.client.post(reverse('teacher-scene-list'), {
            'book': self.book.pk, 'text': 'Narración', 'prefab_key': 'Demo', **extra,
        }, format='multipart')

    def test_fake_glb_is_rejected_before_scene_creation(self):
        response = self.create_scene(glb_model=SimpleUploadedFile('fake.glb', b'not a model'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('glb_model', response.data)
        self.assertEqual(Scene.objects.count(), 0)

    def test_valid_glb_is_accepted(self):
        response = self.create_scene(glb_model=SimpleUploadedFile('model.glb', glb_test_content()))
        self.assertEqual(response.status_code, 201)

    def test_zero_order_is_rejected(self):
        response = self.create_scene(order=0)
        self.assertEqual(response.status_code, 400)
        self.assertIn('order', response.data)

    @override_settings(MAX_GLB_UPLOAD_BYTES=16)
    def test_oversize_model_is_rejected(self):
        response = self.create_scene(glb_model=SimpleUploadedFile('model.glb', glb_test_content()))
        self.assertEqual(response.status_code, 400)

    def test_audio_extension_is_validated(self):
        response = self.create_scene(audio=SimpleUploadedFile('script.html', b'<script>'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('audio', response.data)

    def test_invalid_edit_does_not_remove_existing_model(self):
        scene = Scene.objects.create(book=self.book, text='Original', prefab_key='Demo',
            glb_model=SimpleUploadedFile('old.glb', glb_test_content()))
        original_name = scene.glb_model.name
        response = self.client.patch(reverse('teacher-scene-detail', args=[scene.pk]), {
            'text': '', 'remove_glb_model': True,
        }, format='json')
        self.assertEqual(response.status_code, 400)
        scene.refresh_from_db()
        self.assertEqual(scene.glb_model.name, original_name)
        self.assertTrue(scene.glb_model.storage.exists(original_name))

    def test_new_book_returns_scene_count(self):
        response = self.client.post(reverse('teacher-book-list'), {'title': 'Nuevo'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['scenes_count'], 0)


class SignatureAndHeaderTests(SimpleTestCase):
    def test_corrupt_signatures_raise_domain_error(self):
        valid = [1 / 256] * 256
        for invalid in [None, {}, [0] * 256, ['x'] * 256, [float('nan')] * 256, [-1] * 256, [True] * 256]:
            with self.subTest(invalid=repr(invalid)[:30]):
                with self.assertRaises(FaceRecognitionError):
                    compare_signatures(valid, invalid)
        self.assertEqual(compare_signatures(valid, valid), 0)

    def test_glb_validation_preserves_stream_position(self):
        upload = SimpleUploadedFile('model.glb', glb_test_content())
        upload.seek(5)
        validate_glb_upload(upload)
        self.assertEqual(upload.tell(), 5)
