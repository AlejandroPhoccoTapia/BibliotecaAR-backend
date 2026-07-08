from django.db.models import Count
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView

from .models import Book, Scene
from .serializers import TeacherBookSerializer, TeacherSceneSerializer, UnitySceneSerializer


class TeacherBookViewSet(ModelViewSet):
    serializer_class = TeacherBookSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Book.objects.annotate(scenes_count=Count('scenes')).order_by('title')


class TeacherSceneViewSet(ModelViewSet):
    serializer_class = TeacherSceneSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Scene.objects.select_related('book').order_by('book__title', 'order', 'id')


class UnitySceneDetailView(RetrieveAPIView):
    serializer_class = UnitySceneSerializer
    lookup_field = 'qr_code'
    lookup_url_kwarg = 'qr_code'

    def get_queryset(self):
        return (
            Scene.objects
            .select_related('book')
            .filter(book__is_published=True)
        )
