from rest_framework.generics import RetrieveAPIView

from .models import Scene
from .serializers import UnitySceneSerializer


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
