from rest_framework import serializers
from .models import CategoryConfig, LearnItem


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='category', read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = CategoryConfig
        fields = ['id', 'name', 'slug', 'image']

class LearnItemSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
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
