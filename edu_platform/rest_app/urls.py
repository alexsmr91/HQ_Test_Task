from django.urls import include, path
from rest_framework_nested import routers
from rest_app.views import (
    AvailableProductViewSet,
    UserViewSet,
    LessonViewSet,
    ProductViewSet,
    BuyProductAPIView,
)

router = routers.DefaultRouter()
router.register(
    r"available_product", AvailableProductViewSet, basename="available-product"
)
router.register(r"product", ProductViewSet, basename="product")
router.register(r"user", UserViewSet, basename="user")
lesson_router = routers.NestedSimpleRouter(router, r"product", lookup="product")
lesson_router.register(r"lesson", LessonViewSet, basename="product-lesson")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(lesson_router.urls)),
    path(
        "buy_product/<uuid:product_id>/",
        BuyProductAPIView.as_view(),
        name="buy_product",
    ),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]
