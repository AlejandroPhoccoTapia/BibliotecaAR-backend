from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Book, StudentProfile
from .tests import face_image_upload


class ApiRegressionTests(TestCase):
    def setUp(self):
        cache.clear()
        self.teacher = get_user_model().objects.create_user('teacher', password='correct-pass', is_staff=True)
        self.client = APIClient()
        self.client.force_login(self.teacher)

    def test_registration_preserves_current_teacher_session(self):
        response = self.client.post(reverse('teacher-register'), {
            'username': 'colleague', 'password': 'B0sque-seguro!2048',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.teacher.pk)
        self.assertEqual(response.data['created_user']['username'], 'colleague')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.teacher.pk)

    def test_registration_rejects_common_password_and_invalid_username(self):
        for payload, field in [
            ({'username': 'new-teacher', 'password': '123456789'}, 'password'),
            ({'username': 'invalid user!', 'password': 'B0sque-seguro!2048'}, 'username'),
        ]:
            with self.subTest(field=field):
                response = self.client.post(reverse('teacher-register'), payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_login_and_registration_enforce_csrf_for_anonymous_browser(self):
        client = APIClient(enforce_csrf_checks=True)
        for endpoint in ['teacher-login', 'teacher-register']:
            response = client.post(reverse(endpoint), {'username': 'teacher', 'password': 'correct-pass'}, format='json')
            self.assertEqual(response.status_code, 403)
        token = client.get(reverse('teacher-session')).data['csrf_token']
        response = client.post(reverse('teacher-login'), {'username': 'teacher', 'password': 'correct-pass'}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)

    def test_login_is_rate_limited(self):
        self.client.logout()
        for _ in range(20):
            self.client.post(reverse('teacher-login'), {'username': 'none', 'password': 'wrong'}, format='json')
        response = self.client.post(reverse('teacher-login'), {'username': 'none', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response)

    def test_multipart_creates_multiple_assignments(self):
        books = [Book.objects.create(title=title) for title in ['Uno', 'Dos']]
        response = self.client.post(reverse('teacher-student-list'), {
            'full_name': 'Perfil demo', 'photo': face_image_upload('multi.png'),
            'assigned_books': [book.pk for book in books],
        }, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(response.data['assigned_books'], [book.pk for book in books])

    def test_put_with_photo_clears_all_assignments_and_classroom(self):
        student = StudentProfile.objects.create(full_name='Perfil demo', classroom='Anterior')
        student.assigned_books.add(Book.objects.create(title='Uno'))
        response = self.client.put(reverse('teacher-student-detail', args=[student.pk]), {
            'full_name': student.full_name, 'classroom': '', 'is_active': True,
            'photo': face_image_upload('empty.png'),
            # Browser FormData has no entries for an empty array.
        }, format='multipart')
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.classroom, '')
        self.assertEqual(student.assigned_books.count(), 0)
        self.assertTrue(student.face_signature)

    def test_patch_without_assignments_preserves_them(self):
        student = StudentProfile.objects.create(full_name='Perfil demo')
        student.assigned_books.add(Book.objects.create(title='Uno'))
        response = self.client.patch(reverse('teacher-student-detail', args=[student.pk]), {'classroom': 'Nueva'}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(student.assigned_books.count(), 1)

    def test_removing_photo_clears_signature(self):
        student = StudentProfile.objects.create(full_name='Perfil demo', face_signature=[1])
        response = self.client.patch(reverse('teacher-student-detail', args=[student.pk]), {'photo': None}, format='json')
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertIsNone(student.face_signature)

    def test_student_result_excludes_draft_books(self):
        from .serializers import StudentFaceLoginResultSerializer
        student = StudentProfile.objects.create(full_name='Perfil demo')
        published = Book.objects.create(title='Publicado', is_published=True)
        student.assigned_books.add(published, Book.objects.create(title='Borrador'))
        data = StudentFaceLoginResultSerializer({'student': student, 'distance': 0, 'confidence': 1}).data
        self.assertEqual([book['id'] for book in data['student']['assigned_books']], [published.pk])
