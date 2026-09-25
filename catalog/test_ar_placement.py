import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Book, Scene


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TeacherArPlacementTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = get_user_model().objects.create_user(
            username='docente-ar', password='clave-segura', is_staff=True,
        )
        self.student = get_user_model().objects.create_user(
            username='sin-permiso', password='clave-segura',
        )
        self.book = Book.objects.create(title='Borrador AR')
        self.scene = Scene.objects.create(book=self.book, text='La hormiga camina.', prefab_key='ant')
        self.url = reverse('teacher-mobile-scene', kwargs={'qr_code': self.scene.qr_code})

    def login_mobile(self, username='docente-ar', password='clave-segura'):
        return self.client.post(
            reverse('teacher-mobile-login'),
            {'username': username, 'password': password},
            content_type='application/json',
        )

    def test_mobile_teacher_can_preview_and_save_draft_placement(self):
        token = self.login_mobile().json()['token']
        header = {'HTTP_AUTHORIZATION': 'TeacherPreview ' + token}
        preview = self.client.get(self.url, **header)
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.json()['ar_model_size_cm'], 8.0)
        self.assertEqual(self.client.get(reverse('unity-scene-detail', kwargs={'qr_code': self.scene.qr_code})).status_code, 404)

        saved = self.client.patch(
            self.url,
            {'ar_marker_width_cm': 9, 'ar_model_size_cm': 4, 'ar_offset_x_cm': 3,
             'ar_offset_y_cm': 1, 'ar_offset_z_cm': -2, 'ar_yaw_degrees': 45},
            content_type='application/json', **header,
        )
        self.assertEqual(saved.status_code, 200)
        self.scene.refresh_from_db()
        self.assertEqual(self.scene.ar_model_size_cm, 4)
        self.assertEqual(self.scene.ar_offset_x_cm, 3)

        self.book.is_published = True
        self.book.save()
        public = self.client.get(reverse('unity-scene-detail', kwargs={'qr_code': self.scene.qr_code}))
        self.assertEqual(public.json()['ar_model_size_cm'], 4)
        self.assertEqual(public.json()['ar_yaw_degrees'], 45)

    def test_placement_requires_teacher_and_valid_measurements(self):
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
        self.assertEqual(self.login_mobile('sin-permiso').status_code, 403)
        self.assertEqual(self.login_mobile(password='incorrecta').status_code, 403)

        token = self.login_mobile().json()['token']
        header = {'HTTP_AUTHORIZATION': 'TeacherPreview ' + token}
        invalid = self.client.patch(
            self.url, {'ar_model_size_cm': 0, 'ar_marker_width_cm': 0},
            content_type='application/json', **header,
        )
        self.assertEqual(invalid.status_code, 400)
        self.scene.refresh_from_db()
        self.assertEqual(self.scene.ar_model_size_cm, 8.0)

        self.teacher.set_password('nueva-clave')
        self.teacher.save()
        self.assertEqual(self.client.get(self.url, **header).status_code, 401)
