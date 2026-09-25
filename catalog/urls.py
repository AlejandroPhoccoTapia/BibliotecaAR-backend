from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    StudentBookDetailView,
    StudentChapterProgressView,
    StudentCodeLoginView,
    StudentFaceLoginView,
    StudentLibraryView,
    StudentLogoutView,
    StudentQRProgressView,
    StudentSessionView,
    TeacherLoginView,
    TeacherMobileLoginView,
    TeacherMobileSceneView,
    TeacherLogoutView,
    TeacherRegisterView,
    TeacherSessionView,
    TeacherBookViewSet,
    TeacherSceneViewSet,
    TeacherStudentViewSet,
    UnitySceneDetailView,
)


router = DefaultRouter()
router.register('teacher/books', TeacherBookViewSet, basename='teacher-book')
router.register('teacher/scenes', TeacherSceneViewSet, basename='teacher-scene')
router.register('teacher/students', TeacherStudentViewSet, basename='teacher-student')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/me/', TeacherSessionView.as_view(), name='teacher-session'),
    path('auth/register/', TeacherRegisterView.as_view(), name='teacher-register'),
    path('auth/login/', TeacherLoginView.as_view(), name='teacher-login'),
    path('auth/mobile-login/', TeacherMobileLoginView.as_view(), name='teacher-mobile-login'),
    path('teacher/mobile/scenes/<str:qr_code>/', TeacherMobileSceneView.as_view(), name='teacher-mobile-scene'),
    path('auth/logout/', TeacherLogoutView.as_view(), name='teacher-logout'),
    path('student/face-login/', StudentFaceLoginView.as_view(), name='student-face-login'),
    path('student/code-login/', StudentCodeLoginView.as_view(), name='student-code-login'),
    path('student/me/', StudentSessionView.as_view(), name='student-session'),
    path('student/logout/', StudentLogoutView.as_view(), name='student-logout'),
    path('student/library/', StudentLibraryView.as_view(), name='student-library'),
    path('student/books/<int:pk>/', StudentBookDetailView.as_view(), name='student-book-detail'),
    path('student/chapters/<int:pk>/<str:action>/', StudentChapterProgressView.as_view(), name='student-chapter-progress'),
    path('student/qr/<str:qr_code>/<str:action>/', StudentQRProgressView.as_view(), name='student-qr-progress'),
    path('unity/scenes/<str:qr_code>/', UnitySceneDetailView.as_view(), name='unity-scene-detail'),
]
