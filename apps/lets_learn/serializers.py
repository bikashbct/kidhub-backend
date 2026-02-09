from rest_framework import serializers
from .models import CategoryConfig, LearnItem


class CategorySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = (self.context.get('lang') or 'en').lower()

        if lang == 'ne' and instance.name_ne:
            data['name'] = instance.name_ne
        elif lang == 'hi' and instance.name_hi:
            data['name'] = instance.name_hi

        return data

    class Meta:
        model = CategoryConfig
        fields = ['id', 'name', 'name_ne', 'name_hi', 'slug', 'image']
        read_only_fields = ['slug']

class LearnItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='category',
        queryset=CategoryConfig.objects.all(),
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        object_image = attrs.get('object_image')
        object_color = attrs.get('object_color')

        if object_image and object_color:
            raise serializers.ValidationError(
                "Provide either object_image or object_color, not both."
            )

        return attrs

    class Meta:
        model = LearnItem
        fields = [
            'id',
            'category',
            'name',
            'slug',
            'content_name',
            'object_image',
            'object_color',
            'audio',
            'order',
        ]
        read_only_fields = ['slug']
