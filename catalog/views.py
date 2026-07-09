from django.db.models import Count
from django.conf import settings
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView

from .face_recognition import FaceRecognitionError, build_face_signature, compare_signatures
from .models import Book, Scene, StudentProfile
from .serializers import (
    StudentFaceLoginResultSerializer,
    StudentFaceLoginSerializer,
    TeacherBookSerializer,
    TeacherSceneSerializer,
    TeacherStudentSerializer,
    UnitySceneSerializer,
)


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


class TeacherStudentViewSet(ModelViewSet):
    serializer_class = TeacherStudentSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return StudentProfile.objects.prefetch_related('assigned_books').order_by('full_name')


class StudentFaceLoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = StudentFaceLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            candidate_signature = build_face_signature(serializer.validated_data['image'])
        except FaceRecognitionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        match = self._find_best_match(candidate_signature)
        if not match:
            return Response(
                {'detail': 'No se reconocio ningun estudiante registrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        result_serializer = StudentFaceLoginResultSerializer(match, context={'request': request})
        return Response(result_serializer.data)

    def _find_best_match(self, candidate_signature):
        threshold = getattr(settings, 'FACE_RECOGNITION_DISTANCE_THRESHOLD', 0.45)
        students = (
            StudentProfile.objects
            .filter(is_active=True, face_signature__isnull=False)
            .prefetch_related('assigned_books')
        )

        best_match = None
        for student in students:
            try:
                distance = compare_signatures(candidate_signature, student.face_signature)
            except FaceRecognitionError:
                continue

            if distance <= threshold and (
                best_match is None or distance < best_match['distance']
            ):
                best_match = {
                    'student': student,
                    'distance': round(distance, 6),
                    'confidence': round(max(0, 1 - (distance / threshold)), 4),
                }

        return best_match


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
