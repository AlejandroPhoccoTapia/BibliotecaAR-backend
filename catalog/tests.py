import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
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

# Create your tests here.
