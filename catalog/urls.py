from django.urls import path

from .views import UnitySceneDetailView


urlpatterns = [
    path('unity/scenes/<str:qr_code>/', UnitySceneDetailView.as_view(), name='unity-scene-detail'),
]
