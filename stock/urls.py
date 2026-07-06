from rest_framework.routers import DefaultRouter
from .views import ProductViewset, WarehouseViewset


router = DefaultRouter()
router.register('products',ProductViewset)
router.register ('warehouse',WarehouseViewset)

urlpatterns = router.urls


