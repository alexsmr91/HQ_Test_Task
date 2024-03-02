from db_core.models import Product, Lesson, UserProfile
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import (
    CharField,
    IntegerField,
    ChoiceField,
    UUIDField,
)


class UserSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    password = CharField(
        write_only=True,
        help_text="Оставьте пустым, если не хотите менять",
        style={"input_type": "password", "placeholder": "Пароль"},
    )
    role = ChoiceField(
        choices=UserProfile.USER_ROLE_CHOICES,
        label="Роль",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "role",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = UserProfile.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.role = validated_data.get("role", instance.role)
        new_password = validated_data.get("password", None)
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance


class ProductSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    lesson_count = IntegerField(read_only=True)

    def create(self, validated_data):
        author = self.context["request"].user
        product = Product.objects.create(author=author, **validated_data)
        return product

    class Meta:
        model = Product
        fields = [
            "author",
            "id",
            "name",
            "price",
            "start_datetime",
            "lesson_count",
        ]
        extra_kwargs = {"author": {"read_only": True}}


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name", "video_link"]

    def to_representation(self, instance):
        if self.context.get("view").action == "list":
            return {"id": instance.id, "name": instance.name}
        return {
            "id": instance.id,
            "name": instance.name,
            "video_link": instance.video_link,
        }

    def create(self, validated_data):
        product_pk = self.context["view"].kwargs["product_pk"]
        product = Product.objects.get(pk=product_pk)
        lesson = Lesson.objects.create(product=product, **validated_data)
        return lesson
