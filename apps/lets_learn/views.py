from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .mixins import OpenpyxlXlsxMixin
from .models import CategoryConfig, LearnItem
from .serializers import CategorySerializer, LearnItemSerializer

class AdminWriteOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """

    def get_queryset(self):
        if self.queryset is None:
            raise AssertionError(
                "CreateListRetrieveViewSet requires `.queryset` to be set."
            )
        return super().get_queryset()

    def get_serializer_class(self):
        if self.serializer_class is None:
            raise AssertionError(
                "CreateListRetrieveViewSet requires `.serializer_class` to be set."
            )
        return super().get_serializer_class()


def _download_to_content_file(url: str, fallback_name: str) -> tuple[ContentFile, str]:
    parsed = urlparse(url)
    filename = parsed.path.rsplit("/", 1)[-1] or fallback_name
    if "." not in filename:
        filename = fallback_name
    with urlopen(url) as response:
        content = response.read()
    return ContentFile(content), filename


@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class CategoryViewSet(OpenpyxlXlsxMixin, viewsets.ReadOnlyModelViewSet):
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

    def get_export_sheet_title(self):
        return "Categories"

    def get_export_filename(self):
        return "categories.xlsx"

    def get_export_headers(self):
        return ["category", "name", "slug", "image_url"]

    def get_export_rows(self, request):
        for category in self.get_queryset():
            image_url = (
                request.build_absolute_uri(category.image.url)
                if category.image
                else ""
            )
            yield [
                category.category,
                category.name,
                category.slug,
                image_url,
            ]

    def get_import_required_headers(self):
        return ["category"]

    def handle_import_row(self, row, header_mapping):
        category_value = self.get_import_row_value(row, header_mapping, "category")
        name = self.get_import_row_value(row, header_mapping, "name")
        image_url = self.get_import_row_value(row, header_mapping, "image_url")

        if not category_value:
            return "skipped"

        category_id = int(category_value)
        category, was_created = CategoryConfig.objects.get_or_create(
            category=category_id,
            defaults={"name": name or f"Category {category_id}"},
        )

        if name:
            category.name = name

        if image_url:
            fallback = f"category_{slugify(category.name) or category_id}.png"
            content, filename = _download_to_content_file(image_url, fallback)
            category.image.save(filename, content, save=False)

        category.save()
        return "created" if was_created else "updated"

@method_decorator(cache_page(settings.CACHE_TTL), name="list")
@method_decorator(cache_page(settings.CACHE_TTL), name="retrieve")
class LearnItemViewSet(OpenpyxlXlsxMixin, CreateListRetrieveViewSet):
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

    def get_export_sheet_title(self):
        return "LearnItems"

    def get_export_filename(self):
        return "learn_items.xlsx"

    def get_export_headers(self):
        return [
            "id",
            "category",
            "name",
            "content_name",
            "object_image_url",
            "object_color",
            "audio_url",
            "order",
        ]

    def get_export_rows(self, request):
        for item in self.get_queryset():
            image_url = (
                request.build_absolute_uri(item.object_image.url)
                if item.object_image
                else ""
            )
            audio_url = (
                request.build_absolute_uri(item.audio.url)
                if item.audio
                else ""
            )
            yield [
                item.id,
                item.category_id,
                item.name,
                item.content_name,
                image_url,
                item.object_color,
                audio_url,
                item.order,
            ]

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
