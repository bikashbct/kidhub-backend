"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title=os.getenv("SWAGGER_TITLE", ""),
        default_version=os.getenv("SWAGGER_VERSION", ""),
        description=os.getenv("SWAGGER_DESCRIPTION", ""),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/lets-learn/', include('apps.lets_learn.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^api/lets-learn/docs(?P<format>\\.json|\\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('api/lets-learn/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/lets-learn/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

