from .accounts.viewsets import UserViewSet
from .admin_settings.viewsets import DynamicSettingsViewSet, UploadedDocumentViewSet
from .base.api.routers import FarmersHeavenRouter

restricted_router = FarmersHeavenRouter()

# user
restricted_router.register(r'users', UserViewSet, basename='v1_auth')
restricted_router.register(r'admin', DynamicSettingsViewSet, basename='v1_auth')
restricted_router.register(r'uploads', UploadedDocumentViewSet, basename='v1_auth')
