from rest_framework.permissions import BasePermission
from db_core.models import PurchasedProduct, Lesson, Product
from functools import reduce


def any_of(*perm_classes):
    class Or(BasePermission):
        def has_permission(*args):
            allowed = [p.has_permission(*args) for p in perm_classes]
            return reduce(lambda x, y: x or y, allowed)

        def has_object_permission(*args):
            allowed = [p.has_object_permission(*args) for p in perm_classes]
            return reduce(lambda x, y: x or y, allowed)

    return Or


class MixedPermission:
    permission_classes_by_action = {}

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:

            return [permission() for permission in self.permission_classes]


class IsPurchased(BasePermission):

    def has_permission(self, request, view):
        from rest_app.views import LessonViewSet

        if isinstance(view, LessonViewSet):
            pk_key = "product_pk"
        else:
            pk_key = "pk"
        if bool(request.user and request.user.is_authenticated):
            try:
                product_pk = request.parser_context["kwargs"][pk_key]
            except KeyError as err:
                return False
            else:
                return PurchasedProduct.objects.filter(
                    user=request.user, product_id=product_pk
                ).exists()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if bool(request.user and request.user.is_authenticated):
            if isinstance(obj, Product):
                return PurchasedProduct.objects.filter(
                    user=request.user, product=obj
                ).exists()

            elif isinstance(obj, Lesson):
                return PurchasedProduct.objects.filter(
                    user=request.user, product=obj.product
                ).exists()
        else:
            return False


class IsAuthor(BasePermission):

    def has_permission(self, request, view):
        from rest_app.views import LessonViewSet

        if isinstance(view, LessonViewSet):
            pk_key = "product_pk"
        else:
            pk_key = "pk"
        if bool(request.user and request.user.is_authenticated):
            try:
                product_pk = request.parser_context["kwargs"][pk_key]
            except KeyError as err:
                return False
            else:
                return Product.objects.filter(
                    author=request.user, pk=product_pk
                ).exists()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if bool(request.user and request.user.is_authenticated):
            if isinstance(obj, Product):
                return obj.author == request.user
            elif isinstance(obj, Lesson):
                return obj.product.author == request.user
        else:
            return False


class IsCurrentUser(BasePermission):
    def has_permission(self, request, view):
        user_pk = request.parser_context["kwargs"]["pk"]
        return str(request.user.id) == user_pk

    def has_object_permission(self, request, view, obj):
        if bool(request.user and request.user.is_authenticated):
            return obj == request.user
        else:
            return False


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            return request.user.role == "teacher"
        else:
            return False
