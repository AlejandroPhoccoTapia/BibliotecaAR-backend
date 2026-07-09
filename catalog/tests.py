import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image, ImageDraw

from .models import Book, Scene, StudentProfile


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
        self.assertEqual(response.json()['glb_model_name'], 'bosque.glb')
        self.assertTrue(response.json()['glb_model_url'].endswith('/media/scenes/models/bosque.glb'))

    def test_replacing_glb_model_deletes_old_file(self):
        book = Book.objects.create(title='Libro Demo', is_published=True)
        scene = Scene.objects.create(
            book=book,
            text='Texto para Unity',
            prefab_key='Bosque',
            glb_model=SimpleUploadedFile(
                'modelo-anterior.glb',
                b'old glb content',
                content_type='model/gltf-binary',
            ),
        )
        old_path = Path(scene.glb_model.path)

        scene.glb_model = SimpleUploadedFile(
            'modelo-nuevo.glb',
            b'new glb content',
            content_type='model/gltf-binary',
        )
        scene.save()

        self.assertFalse(old_path.exists())
        self.assertTrue(Path(scene.glb_model.path).exists())

    def test_teacher_can_remove_glb_model(self):
        book = Book.objects.create(title='Libro Demo', is_published=True)
        scene = Scene.objects.create(
            book=book,
            text='Texto para Unity',
            prefab_key='Bosque',
            glb_model=SimpleUploadedFile(
                'modelo-removible.glb',
                b'glb content',
                content_type='model/gltf-binary',
            ),
        )
        old_path = Path(scene.glb_model.path)

        response = self.client.patch(
            reverse('teacher-scene-detail', kwargs={'pk': scene.pk}),
            {'remove_glb_model': True},
            content_type='application/json',
        )

        scene.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['glb_model_name'])
        self.assertIsNone(response.json()['glb_model_url'])
        self.assertFalse(scene.glb_model)
        self.assertFalse(old_path.exists())

    def test_teacher_api_requires_staff_user(self):
        self.client.logout()

        response = self.client.get(reverse('teacher-book-list'))

        self.assertIn(response.status_code, (302, 403))

    def test_teacher_can_login_through_api(self):
        self.client.logout()

        response = self.client.post(
            reverse('teacher-login'),
            {
                'username': 'docente',
                'password': 'test-pass',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_authenticated'])
        self.assertEqual(response.json()['user']['username'], 'docente')
        self.assertTrue(response.json()['csrf_token'])

    def test_teacher_session_reports_anonymous_user(self):
        self.client.logout()

        response = self.client.get(reverse('teacher-session'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_authenticated'])
        self.assertTrue(response.json()['csrf_token'])

    def test_first_teacher_can_register_without_existing_teacher(self):
        self.client.logout()
        get_user_model().objects.all().delete()

        response = self.client.post(
            reverse('teacher-register'),
            {
                'username': 'primer-docente',
                'password': 'strong-pass-123',
                'first_name': 'Primer',
                'last_name': 'Docente',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['is_authenticated'])
        self.assertTrue(response.json()['csrf_token'])
        user = get_user_model().objects.get(username='primer-docente')
        self.assertTrue(user.is_staff)

    def test_anonymous_user_cannot_register_second_teacher(self):
        self.client.logout()

        response = self.client.post(
            reverse('teacher-register'),
            {
                'username': 'otro-docente',
                'password': 'strong-pass-123',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_authenticated_teacher_can_register_another_teacher(self):
        response = self.client.post(
            reverse('teacher-register'),
            {
                'username': 'colega',
                'password': 'strong-pass-123',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(get_user_model().objects.get(username='colega').is_staff)

    def test_teacher_can_create_student_with_face_signature_and_books(self):
        book = Book.objects.create(title='Libro asignado', is_published=True)

        response = self.client.post(
            reverse('teacher-student-list'),
            {
                'full_name': 'Ana Torres',
                'classroom': 'Inicial 5',
                'photo': face_image_upload('ana.png'),
                'assigned_books': [book.id],
                'is_active': True,
            },
        )

        self.assertEqual(response.status_code, 201)
        student = StudentProfile.objects.get(pk=response.json()['id'])
        self.assertTrue(student.face_signature)
        self.assertEqual(list(student.assigned_books.values_list('id', flat=True)), [book.id])
        self.assertTrue(response.json()['has_face_signature'])

    def test_student_face_login_returns_matching_student(self):
        book = Book.objects.create(title='Libro asignado', is_published=True)
        student = StudentProfile.objects.create(
            full_name='Ana Torres',
            classroom='Inicial 5',
            photo=face_image_upload('ana.png'),
            is_active=True,
        )
        from .face_recognition import build_face_signature
        student.face_signature = build_face_signature(student.photo)
        student.save()
        student.assigned_books.set([book])

        self.client.logout()
        response = self.client.post(
            reverse('student-face-login'),
            {'image': face_image_upload('ana-login.png')},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['student']['full_name'], 'Ana Torres')
        self.assertEqual(response.json()['student']['assigned_books'][0]['title'], 'Libro asignado')


def face_image_upload(name):
    image = Image.new('RGB', (180, 180), 'white')
    draw = ImageDraw.Draw(image)
    draw.ellipse((45, 30, 135, 125), fill=(220, 170, 135), outline=(80, 60, 50), width=3)
    draw.ellipse((70, 65, 82, 78), fill='black')
    draw.ellipse((104, 65, 116, 78), fill='black')
    draw.arc((72, 78, 115, 110), 15, 165, fill=(120, 40, 40), width=3)
    draw.rectangle((65, 125, 115, 160), fill=(80, 150, 210))

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')
