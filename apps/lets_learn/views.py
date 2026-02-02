from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import CategoryConfig, LearnItem
from .serializers import CategorySerializer, LearnItemSerializer

class AdminWriteOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoryConfig.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminWriteOrReadOnly]

@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class LearnItemViewSet(viewsets.ModelViewSet):
    queryset = LearnItem.objects.all()
    serializer_class = LearnItemSerializer
    filterset_fields = ['category']
    permission_classes = [AdminWriteOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category=category_id)
        return queryset
