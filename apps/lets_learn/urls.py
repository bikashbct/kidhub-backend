from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, LearnItemViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'items', LearnItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
