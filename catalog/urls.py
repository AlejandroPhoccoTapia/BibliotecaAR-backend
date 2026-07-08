from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TeacherBookViewSet, TeacherSceneViewSet, UnitySceneDetailView


router = DefaultRouter()
router.register('teacher/books', TeacherBookViewSet, basename='teacher-book')
router.register('teacher/scenes', TeacherSceneViewSet, basename='teacher-scene')


urlpatterns = [
    path('', include(router.urls)),
    path('unity/scenes/<str:qr_code>/', UnitySceneDetailView.as_view(), name='unity-scene-detail'),
]
