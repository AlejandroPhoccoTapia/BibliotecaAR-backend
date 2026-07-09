from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    StudentFaceLoginView,
    TeacherLoginView,
    TeacherLogoutView,
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
    path('auth/login/', TeacherLoginView.as_view(), name='teacher-login'),
    path('auth/logout/', TeacherLogoutView.as_view(), name='teacher-logout'),
    path('student/face-login/', StudentFaceLoginView.as_view(), name='student-face-login'),
    path('unity/scenes/<str:qr_code>/', UnitySceneDetailView.as_view(), name='unity-scene-detail'),
]
