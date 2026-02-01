from rest_framework import serializers
from .models import Category, LearnItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class LearnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnItem
        fields = ['id', 'category', 'name', 'content_name', 'object_image', 'audio', 'order']
