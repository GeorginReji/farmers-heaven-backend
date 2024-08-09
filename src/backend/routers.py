from .accounts.viewsets import UserViewSet
from .admin_settings.viewsets import DynamicSettingsViewSet, UploadedDocumentViewSet
from .base.api.routers import FarmersHeavenRouter
from .orders.viewsets import OrderViewSet

restricted_router = FarmersHeavenRouter()

# user
restricted_router.register(r'users', UserViewSet, basename='v1_auth')
restricted_router.register(r'admin', DynamicSettingsViewSet, basename='v1_admin')
restricted_router.register(r'uploads', UploadedDocumentViewSet, basename='v1_uploads')
restricted_router.register(r'orders', OrderViewSet, basename='v1_orders')
