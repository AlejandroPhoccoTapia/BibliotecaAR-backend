from django.db.models import Count, Prefetch
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView

from .face_recognition import FaceRecognitionError, build_face_signature, compare_signatures
from .models import Book, Scene, StudentProfile, StudentReadingProgress
from .serializers import (
    StudentAssignedBookSerializer,
    StudentChapterSerializer,
    StudentFaceLoginResultSerializer,
    StudentFaceLoginSerializer,
    StudentPublicSerializer,
    TeacherBookSerializer,
    TeacherRegisterSerializer,
    TeacherSceneSerializer,
    TeacherStudentSerializer,
    UnitySceneSerializer,
)
from .student_auth import (
    IsStudent,
    StudentBearerAuthentication,
    authenticate_student_code,
    issue_student_token,
    reset_student_access_code,
)


def teacher_auth_payload(request, user=None):
    user = user or request.user
    payload = {'csrf_token': get_token(request)}

    if not user.is_authenticated:
        payload['is_authenticated'] = False
        return payload

    payload.update({
        'is_authenticated': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    })
    return payload


@method_decorator(ensure_csrf_cookie, name='dispatch')
class TeacherSessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(teacher_auth_payload(request))


@method_decorator(csrf_protect, name='dispatch')
class TeacherLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'teacher_login'
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Ingresa usuario y contrasena.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if not user or not user.is_staff:
            return Response(
                {'detail': 'Credenciales invalidas o usuario sin permisos de docente.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)
        return Response(teacher_auth_payload(request, user))


@method_decorator(csrf_protect, name='dispatch')
class TeacherRegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'teacher_register'
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        serializer = TeacherRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if not request.user.is_authenticated:
            login(request, user)
        payload = teacher_auth_payload(request)
        payload['created_user'] = {'id': user.id, 'username': user.username}
        return Response(
            payload,
            status=status.HTTP_201_CREATED,
        )


class TeacherLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(teacher_auth_payload(request))


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
        return StudentProfile.objects.prefetch_related(
            Prefetch('assigned_books', queryset=Book.objects.annotate(scenes_count=Count('scenes'))),
        ).order_by('full_name', 'id')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        code = reset_student_access_code(student)
        data = dict(serializer.data)
        data['access_code'] = code
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='reset-access-code')
    def reset_access_code(self, request, pk=None):
        student = self.get_object()
        code = reset_student_access_code(student)
        return Response({'access_code': code})


class StudentFaceLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'student_face'
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
        token, expires_at = issue_student_token(match['student'])
        return Response({**result_serializer.data, 'token': token, 'expires_at': expires_at})

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


class StudentCodeLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'student_code'
    parser_classes = [JSONParser]

    def post(self, request):
        student = authenticate_student_code(request.data.get('code'))
        if student is None:
            return Response({'detail': 'Código inválido o cuenta inactiva.'}, status=status.HTTP_403_FORBIDDEN)
        token, expires_at = issue_student_token(student)
        return Response({
            'token': token,
            'expires_at': expires_at,
            'student': StudentPublicSerializer(student, context={'request': request}).data,
        })


class StudentAuthenticatedView(APIView):
    authentication_classes = [StudentBearerAuthentication]
    permission_classes = [IsStudent]


class StudentSessionView(StudentAuthenticatedView):
    def get(self, request):
        return Response({'student': StudentPublicSerializer(request.user, context={'request': request}).data})


class StudentLogoutView(StudentAuthenticatedView):
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentLibraryView(StudentAuthenticatedView):
    def get(self, request):
        assigned = list(request.user.assigned_books.filter(is_published=True).order_by('title'))
        assigned_ids = {book.id for book in assigned}
        progress = list(
            StudentReadingProgress.objects
            .filter(student=request.user, last_opened_at__isnull=False, scene__book__is_published=True)
            .select_related('scene__book')
            .order_by('-last_opened_at', '-id')
        )
        recent = []
        recent_ids = set()
        for item in progress:
            book = item.scene.book
            if book.id not in assigned_ids and book.id not in recent_ids:
                recent.append(book)
                recent_ids.add(book.id)

        resume = None
        if progress:
            latest = progress[0]
            resume = {
                'book_id': latest.scene.book_id,
                'book_title': latest.scene.book.title,
                'scene_id': latest.scene_id,
                'scene_title': latest.scene.title or f'Capítulo {latest.scene.order}',
                'is_completed': bool(latest.completed_at),
            }

        context = {'request': request}
        return Response({
            'student': StudentPublicSerializer(request.user, context=context).data,
            'assigned_books': StudentAssignedBookSerializer(assigned, many=True, context=context).data,
            'recent_books': StudentAssignedBookSerializer(recent, many=True, context=context).data,
            'resume': resume,
        })


class StudentBookDetailView(StudentAuthenticatedView):
    def get(self, request, pk):
        book = get_object_or_404(Book.objects.filter(is_published=True), pk=pk)
        chapters = list(book.scenes.order_by('order', 'id'))
        progress_by_scene = {
            item.scene_id: item for item in StudentReadingProgress.objects.filter(
                student=request.user, scene_id__in=[chapter.id for chapter in chapters],
            )
        }
        context = {'request': request, 'progress_by_scene': progress_by_scene}
        return Response({
            'book': StudentAssignedBookSerializer(book, context=context).data,
            'chapters': StudentChapterSerializer(chapters, many=True, context=context).data,
        })


class StudentChapterProgressView(StudentAuthenticatedView):
    def post(self, request, pk, action):
        chapter = get_object_or_404(Scene.objects.filter(book__is_published=True), pk=pk)
        return save_student_progress(request.user, chapter, action)


class StudentQRProgressView(StudentAuthenticatedView):
    def post(self, request, qr_code, action):
        chapter = get_object_or_404(Scene.objects.filter(book__is_published=True), qr_code=qr_code)
        return save_student_progress(request.user, chapter, action)


def save_student_progress(student, chapter, action):
    if action not in ('open', 'complete'):
        return Response({'detail': 'Acción desconocida.'}, status=status.HTTP_400_BAD_REQUEST)
    now = timezone.now()
    progress, _ = StudentReadingProgress.objects.get_or_create(student=student, scene=chapter)
    progress.last_opened_at = now
    fields = ['last_opened_at']
    if action == 'complete':
        progress.completed_at = now
        fields.append('completed_at')
    progress.save(update_fields=fields)
    return Response({
        'scene_id': chapter.id,
        'last_opened_at': progress.last_opened_at,
        'completed_at': progress.completed_at,
        'is_completed': bool(progress.completed_at),
    })


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
