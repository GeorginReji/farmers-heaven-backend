"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.urls import re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenBlacklistView

from .routers import restricted_router
from .base.api.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Farmers Heaven API",
        default_version='v1',
        description="Farmers Heaven APIs",
        terms_of_service="https://www.farmersheaven.com",
        contact=openapi.Contact(email="jyothisbenny75@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fh-api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fh-api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('fh-api/v1/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('fh-api/v1/', include(restricted_router.urls)),
]

if settings.DEBUG:
    swagger_url = [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
    urlpatterns = urlpatterns + swagger_url
