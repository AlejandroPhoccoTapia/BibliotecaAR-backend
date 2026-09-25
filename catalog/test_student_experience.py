from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Book, Scene, StudentProfile


class StudentExperienceTests(TestCase):
    def setUp(self):
        self.teacher = get_user_model().objects.create_user(
            username='teacher', password='test-password', is_staff=True,
        )
        self.assigned_book = Book.objects.create(title='Asignado', is_published=True)
        self.other_book = Book.objects.create(title='Explorado', is_published=True)
        self.draft_book = Book.objects.create(title='Borrador', is_published=False)
        self.assigned_chapter = Scene.objects.create(
            book=self.assigned_book, title='Capítulo 1', text='Leer aquí', prefab_key='Demo',
        )
        self.other_chapter = Scene.objects.create(
            book=self.other_book, title='Capítulo libre', text='También se puede leer', prefab_key='Demo',
        )
        self.draft_chapter = Scene.objects.create(
            book=self.draft_book, title='Inédito', text='Oculto', prefab_key='Demo',
        )
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse('teacher-student-list'),
            {'full_name': 'Ana', 'assigned_books': [self.assigned_book.id], 'is_active': True},
        )
        self.assertEqual(response.status_code, 201)
        self.student_id = response.json()['id']
        self.code = response.json()['access_code']
        self.assertTrue(response.json()['has_access_code'])
        self.client.logout()

    def login(self, code=None):
        response = self.client.post(
            reverse('student-code-login'), {'code': code or self.code}, content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        return response.json()['token']

    def auth_get(self, name, token, **kwargs):
        return self.client.get(reverse(name, kwargs=kwargs), HTTP_AUTHORIZATION=f'Bearer {token}')

    def auth_post(self, name, token, **kwargs):
        return self.client.post(reverse(name, kwargs=kwargs), HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_library_and_progress_follow_student_across_logins(self):
        token = self.login()
        library = self.auth_get('student-library', token)
        self.assertEqual(library.status_code, 200)
        self.assertEqual([book['title'] for book in library.json()['assigned_books']], ['Asignado'])
        self.assertEqual(library.json()['recent_books'], [])
        self.assertIsNone(library.json()['resume'])

        chapter = self.auth_get('student-book-detail', token, pk=self.assigned_book.id)
        self.assertEqual(chapter.status_code, 200)
        self.assertEqual(chapter.json()['chapters'][0]['text'], 'Leer aquí')
        self.assertFalse(chapter.json()['chapters'][0]['is_completed'])
        self.assertNotIn('glb_model_url', chapter.json()['chapters'][0])

        opened = self.auth_post('student-chapter-progress', token, pk=self.assigned_chapter.id, action='open')
        self.assertEqual(opened.status_code, 200)
        self.assertFalse(opened.json()['is_completed'])

        second_token = self.login()
        self.assertEqual(
            self.auth_get('student-library', second_token).json()['resume']['scene_id'],
            self.assigned_chapter.id,
        )
        completed = self.auth_post('student-chapter-progress', second_token, pk=self.assigned_chapter.id, action='complete')
        self.assertTrue(completed.json()['is_completed'])
        self.assertTrue(self.auth_get('student-book-detail', token, pk=self.assigned_book.id).json()['chapters'][0]['is_completed'])

    def test_published_unassigned_book_is_readable_and_recent(self):
        token = self.login()
        self.assertEqual(self.auth_get('student-book-detail', token, pk=self.other_book.id).status_code, 200)
        self.assertEqual(self.auth_get('student-book-detail', token, pk=self.draft_book.id).status_code, 404)
        self.assertEqual(
            self.auth_post('student-chapter-progress', token, pk=self.draft_chapter.id, action='open').status_code,
            404,
        )
        self.auth_post('student-chapter-progress', token, pk=self.other_chapter.id, action='open')
        library = self.auth_get('student-library', token).json()
        self.assertEqual([book['title'] for book in library['recent_books']], ['Explorado'])

    def test_code_reset_revokes_sessions_and_previous_code(self):
        token = self.login()
        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teacher-student-reset-access-code', kwargs={'pk': self.student_id}))
        self.assertEqual(response.status_code, 200)
        new_code = response.json()['access_code']
        self.assertNotEqual(new_code, self.code)
        self.client.logout()

        self.assertEqual(self.auth_get('student-session', token).status_code, 401)
        old_login = self.client.post(
            reverse('student-code-login'), {'code': self.code}, content_type='application/json',
        )
        self.assertEqual(old_login.status_code, 403)
        self.assertTrue(self.login(new_code))

    def test_anonymous_and_inactive_students_cannot_access_progress(self):
        self.assertEqual(self.client.get(reverse('student-library')).status_code, 401)
        token = self.login()
        self.client.force_login(self.teacher)
        response = self.client.patch(
            reverse('teacher-student-detail', kwargs={'pk': self.student_id}),
            {'is_active': False}, content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assertEqual(self.auth_get('student-library', token).status_code, 401)
        response = self.client.post(
            reverse('student-code-login'), {'code': self.code}, content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        StudentProfile.objects.filter(pk=self.student_id).update(is_active=True)
        self.assertEqual(self.auth_get('student-library', token).status_code, 401)
