from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .mixins import XlsxExportImportMixin
from .models import CategoryConfig, LearnItem
from .serializers import (
    CategorySerializer,
    LearnItemExportSerializer,
    LearnItemSerializer,
)

class AdminWriteOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def _download_to_content_file(url: str, fallback_name: str) -> tuple[ContentFile, str]:
    parsed = urlparse(url)
    filename = parsed.path.rsplit("/", 1)[-1] or fallback_name
    if "." not in filename:
        filename = fallback_name
    with urlopen(url) as response:
        content = response.read()
    return ContentFile(content), filename


def _get_category_from_request(request):
    value = request.query_params.get("category")
    if not value:
        return None
    return CategoryConfig.objects.filter(category=value).first()


def _category_filename(category, fallback):
    if not category:
        return fallback
    base = slugify(category.name) or f"category-{category.category}"
    return f"{base}.xlsx"


@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoryConfig.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminWriteOrReadOnly]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = (self.request.query_params.get('lang') or 'en').lower()
        if lang not in ('en', 'ne', 'hi'):
            lang = 'en'
        context['lang'] = lang
        return context


@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class LearnItemViewSet(
    XlsxExportImportMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = LearnItem.objects.all()
    serializer_class = LearnItemSerializer
    export_serializer_class = LearnItemExportSerializer
    filename = "learn_items.xlsx"
    filterset_fields = ['category']
    permission_classes = [AdminWriteOrReadOnly]

    def get_filename(self, request, *args, **kwargs):
        return _category_filename(_get_category_from_request(request), self.filename)

    def get_import_required_headers(self):
        return ["category", "name"]

    def handle_import_row(self, row, header_mapping):
        item_id = self.get_import_row_value(row, header_mapping, "id")
        category_value = self.get_import_row_value(row, header_mapping, "category")
        name = self.get_import_row_value(row, header_mapping, "name")
        content_name = self.get_import_row_value(row, header_mapping, "content_name")
        object_image_url = self.get_import_row_value(
            row, header_mapping, "object_image_url"
        )
        object_color = self.get_import_row_value(row, header_mapping, "object_color")
        order = self.get_import_row_value(row, header_mapping, "order")

        if not category_value or not name:
            return "skipped"

        category = CategoryConfig.objects.filter(
            category=int(category_value)
        ).first()
        if not category:
            return "skipped"

        if item_id:
            item = LearnItem.objects.filter(id=int(item_id)).first()
        else:
            item = None

        if not item:
            item = LearnItem(category=category)
            result = "created"
        else:
            result = "updated"

        item.category = category
        item.name = name
        item.content_name = content_name
        if order is not None:
            item.order = int(order)

        if object_image_url:
            fallback = f"{slugify(name) or 'item'}.png"
            content, filename = _download_to_content_file(
                object_image_url, fallback
            )
            item.object_image.save(filename, content, save=False)
            item.object_color = None
        elif object_color:
            item.object_color = object_color
            item.object_image = None

        item.save()
        return result
