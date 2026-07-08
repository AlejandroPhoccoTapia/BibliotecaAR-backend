import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Book, Scene


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class UnitySceneEndpointTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_scene_generates_qr_code_and_image(self):
        book = Book.objects.create(title='Libro Demo', is_published=True)
        scene = Scene.objects.create(
            book=book,
            text='Texto para Unity',
            prefab_key='Bosque',
        )

        self.assertTrue(scene.qr_code)
        self.assertTrue(scene.qr_image.name.endswith('.png'))

    def test_unity_endpoint_returns_published_scene(self):
        book = Book.objects.create(title='Libro Demo', is_published=True)
        scene = Scene.objects.create(
            book=book,
            title='Escena 1',
            text='Texto para Unity',
            prefab_key='Bosque',
            glb_model=SimpleUploadedFile(
                'bosque.glb',
                b'glTF binary test content',
                content_type='model/gltf-binary',
            ),
        )

        response = self.client.get(
            reverse('unity-scene-detail', kwargs={'qr_code': scene.qr_code})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['prefab_key'], 'Bosque')
        self.assertEqual(response.json()['text'], 'Texto para Unity')
        self.assertTrue(response.json()['glb_model_url'].endswith('/media/scenes/models/bosque.glb'))

    def test_unity_endpoint_hides_unpublished_books(self):
        book = Book.objects.create(title='Borrador', is_published=False)
        scene = Scene.objects.create(
            book=book,
            text='No visible',
            prefab_key='Bosque',
        )

        response = self.client.get(
            reverse('unity-scene-detail', kwargs={'qr_code': scene.qr_code})
        )

        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TeacherApiTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = get_user_model().objects.create_user(
            username='docente',
            password='test-pass',
            is_staff=True,
        )
        self.client.force_login(self.teacher)

    def test_teacher_can_create_book(self):
        response = self.client.post(
            reverse('teacher-book-list'),
            {
                'title': 'Cuento del bosque',
                'description': 'Libro de prueba',
                'is_published': True,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], 'Cuento del bosque')
        self.assertTrue(response.json()['is_published'])

    def test_teacher_can_create_scene_with_glb_and_get_qr(self):
        book = Book.objects.create(title='Libro Demo', is_published=True)

        response = self.client.post(
            reverse('teacher-scene-list'),
            {
                'book': book.id,
                'title': 'Escena con modelo',
                'order': 1,
                'text': 'Texto para Unity',
                'prefab_key': 'Bosque',
                'glb_model': SimpleUploadedFile(
                    'bosque.glb',
                    b'glTF binary test content',
                    content_type='model/gltf-binary',
                ),
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['qr_code'])
        self.assertTrue(response.json()['qr_image_url'])
        self.assertTrue(response.json()['glb_model_url'].endswith('/media/scenes/models/bosque.glb'))

    def test_teacher_api_requires_staff_user(self):
        self.client.logout()

        response = self.client.get(reverse('teacher-book-list'))

        self.assertIn(response.status_code, (302, 403))
