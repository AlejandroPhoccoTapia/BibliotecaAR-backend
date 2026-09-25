from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import TestCase, override_settings

from .models import Book, Scene, StudentProfile
from .tests import face_image_upload


class MediaLifecycleTests(TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.enterContext(override_settings(MEDIA_ROOT=folder.name))

    def make_scene(self):
        book = Book.objects.create(title='Demo', cover=face_image_upload('cover.png'))
        return Scene.objects.create(book=book, text='Demo', prefab_key='Demo',
            audio=SimpleUploadedFile('voice.mp3', b'audio'),
            glb_model=SimpleUploadedFile('model.glb', b'model'))

    def test_cascade_removes_all_book_and_scene_files_after_commit(self):
        scene = self.make_scene()
        paths = [Path(file.path) for file in [scene.book.cover, scene.audio, scene.glb_model, scene.qr_image]]
        with self.captureOnCommitCallbacks(execute=True):
            scene.book.delete()
            self.assertTrue(all(path.exists() for path in paths))
        self.assertTrue(all(not path.exists() for path in paths))

    def test_queryset_delete_removes_student_photo(self):
        student = StudentProfile.objects.create(full_name='Demo', photo=face_image_upload('photo.png'))
        path = Path(student.photo.path)
        with self.captureOnCommitCallbacks(execute=True):
            StudentProfile.objects.filter(pk=student.pk).delete()
        self.assertFalse(path.exists())

    def test_rollback_preserves_files_and_rows(self):
        scene = self.make_scene()
        pk = scene.pk
        path = Path(scene.glb_model.path)
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    scene.book.delete()
                    raise RuntimeError('Rollback')
        self.assertTrue(Scene.objects.filter(pk=pk).exists())
        self.assertTrue(path.exists())

    def test_shared_file_is_preserved_until_last_reference_deleted(self):
        first = StudentProfile.objects.create(full_name='One', photo=face_image_upload('shared.png'))
        second = StudentProfile.objects.create(full_name='Two', photo=first.photo.name)
        path = Path(first.photo.path)
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.assertTrue(path.exists())
        with self.captureOnCommitCallbacks(execute=True):
            second.delete()
        self.assertFalse(path.exists())

    def test_partial_save_does_not_delete_persisted_file(self):
        book = self.make_scene().book
        path = Path(book.cover.path)
        book.cover = None
        book.title = 'Changed'
        with self.captureOnCommitCallbacks(execute=True):
            book.save(update_fields=['title'])
        book.refresh_from_db()
        self.assertTrue(book.cover)
        self.assertTrue(path.exists())

    def test_replacement_removes_previous_cover(self):
        book = self.make_scene().book
        path = Path(book.cover.path)
        with self.captureOnCommitCallbacks(execute=True):
            book.cover = face_image_upload('new.png')
            book.save()
        self.assertFalse(path.exists())
        self.assertTrue(Path(book.cover.path).exists())

    def test_storage_failure_does_not_fail_committed_delete(self):
        student = StudentProfile.objects.create(full_name='Demo', photo=face_image_upload('photo.png'))
        with patch.object(student.photo.storage, 'delete', side_effect=OSError('offline')):
            with self.assertLogs(level='ERROR'):
                with self.captureOnCommitCallbacks(execute=True):
                    student.delete()
        self.assertEqual(StudentProfile.objects.count(), 0)
