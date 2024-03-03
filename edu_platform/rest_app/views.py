from django.db.models import Count
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from db_core.models import Product, Lesson, PurchasedProduct, UserProfile
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from .utils import (
    MixedPermission,
    IsCurrentUser,
    IsAuthor,
    IsTeacher,
    IsPurchased,
    any_of,
)
from .serializers import (
    ProductSerializer,
    UserSerializer,
    LessonSerializer,
)


class ProductViewSet(MixedPermission, ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "retrieve": [any_of(IsPurchased, IsAuthor, IsAdminUser)],
        "create": [any_of(IsAdminUser, IsTeacher)],
        "update": [any_of(IsAdminUser, IsAuthor)],
        "partial_update": [any_of(IsAdminUser, IsAuthor)],
        "destroy": [IsAdminUser],
    }

    def get_queryset(self):
        return (
            Product.objects.filter()
            .annotate(lesson_count=Count("lessons"))
            .order_by("start_datetime")
        )


class AvailableProductViewSet(MixedPermission, ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "retrieve": [any_of(IsPurchased, IsAuthor, IsAdminUser)],
        "create": [any_of(IsAdminUser, IsTeacher)],
        "update": [any_of(IsAdminUser, IsAuthor)],
        "partial_update": [any_of(IsAdminUser, IsAuthor)],
        "destroy": [IsAdminUser],
    }

    def get_queryset(self):
        return (
            Product.objects.exclude(
                purchasedproduct__user=self.request.user,
            )
            .annotate(lesson_count=Count("lessons"))
            .order_by("start_datetime")
        )


class BuyProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Продукт не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        if PurchasedProduct.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"error": "Продукт уже куплен"}, status=status.HTTP_400_BAD_REQUEST
            )
        PurchasedProduct.objects.create(product=product, user=request.user)
        product_detail_url = reverse("product-detail", kwargs={"pk": product_id})
        return redirect(product_detail_url)


class UserViewSet(MixedPermission, ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {
        "list": [IsAdminUser],
        "retrieve": [IsAuthenticated],
        "create": [AllowAny],
        "update": [any_of(IsCurrentUser, IsAdminUser, IsAdminUser)],
        "partial_update": [any_of(IsAdminUser, IsCurrentUser, IsAdminUser)],
        "destroy": [IsAdminUser],
    }


class LessonViewSet(MixedPermission, ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes_by_action = {
        "list": [any_of(IsPurchased, IsAuthor, IsAdminUser)],
        "retrieve": [any_of(IsPurchased, IsAuthor, IsAdminUser)],
        "create": [any_of(IsAdminUser, IsTeacher)],
        "update": [any_of(IsAdminUser, IsAuthor)],
        "partial_update": [any_of(IsAdminUser, IsAuthor)],
        "destroy": [IsAdminUser],
    }

    def get_queryset(self):
        if self.kwargs.get("product_pk"):
            product_pk = self.kwargs.get("product_pk")
            return Lesson.objects.filter(product=product_pk)
        else:
            return super(LessonViewSet, self).get_queryset()
