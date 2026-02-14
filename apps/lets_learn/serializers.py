from django.core.exceptions import ValidationError
from rest_framework import serializers

from .services import validate_object_fields
from .models import CategoryConfig, LearnItem


_LANG_FIELD_MAP = {
    "ne": "name_ne",
    "hi": "name_hi",
}


class CategorySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = (self.context.get("lang") or "en").lower()
        field_name = _LANG_FIELD_MAP.get(lang)
        if field_name:
            translated = getattr(instance, field_name)
            if translated:
                data["name"] = translated

        return data

    class Meta:
        model = CategoryConfig
        fields = ["id", "name", "name_ne", "name_hi", "slug", "image"]
        read_only_fields = ["slug"]


def _build_file_url(request, file_field):
    if not file_field:
        return ''
    if request:
        return request.build_absolute_uri(file_field.url)
    return file_field.url


class LearnItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="category",
        queryset=CategoryConfig.objects.all(),
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            validate_object_fields(
                attrs.get('object_image'),
                attrs.get('object_color'),
            )
        except ValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)

        return attrs

    class Meta:
        model = LearnItem
        fields = [
            "id",
            "category",
            "name",
            "slug",
            "content_name",
            "object_image",
            "object_color",
            "audio",
            "order",
        ]
        read_only_fields = ["slug"]


class LearnItemExportSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    object_image_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = LearnItem
        fields = [
            "id",
            "category",
            "name",
            "content_name",
            "object_image_url",
            "object_color",
            "audio_url",
            "order",
        ]

    def get_category(self, instance):
        return instance.category_id

    def get_object_image_url(self, instance):
        return _build_file_url(self.context.get('request'), instance.object_image)

    def get_audio_url(self, instance):
        return _build_file_url(self.context.get('request'), instance.audio)
