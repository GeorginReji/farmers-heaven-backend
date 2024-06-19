from .accounts.viewsets import UserViewSet
from .base.api.routers import FarmersHeavenRouter

restricted_router = FarmersHeavenRouter()

# user
restricted_router.register(r'users', UserViewSet, basename='v1_auth')
