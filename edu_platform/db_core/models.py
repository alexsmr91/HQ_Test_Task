from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4


class UserProfile(AbstractUser):

    USER_ROLE_CHOICES = (
        ("teacher", "Преподаватель"),
        ("student", "Ученик"),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    role = models.CharField(
        max_length=10, choices=USER_ROLE_CHOICES, verbose_name="Роль"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        if self.last_name or self.first_name:
            return f"{self.last_name} {self.first_name}"
        else:
            return f"{self.username}"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, verbose_name="Автор"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    start_datetime = models.DateTimeField(verbose_name="Дата и время начала")
    min_users_per_group = models.PositiveIntegerField(
        default=15, verbose_name="Минимальное количество студентов на группу"
    )
    max_users_per_group = models.PositiveIntegerField(
        default=30, verbose_name="Максимальное количество студентов на группу"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name}"


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        related_name="lessons",
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    name = models.CharField(max_length=255, verbose_name="Название урока")
    video_link = models.URLField(verbose_name="Ссылка на видео")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.name}"


class StudyGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    name = models.CharField(max_length=255, verbose_name="Название группы")
    users = models.ManyToManyField(
        UserProfile, related_name="study_groups", verbose_name="Студенты"
    )

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"

    def __str__(self):
        return f"{self.name}"


class PurchasedProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="Студент",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    purchase_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата покупки"
    )

    class Meta:
        unique_together = ("user", "product")
        verbose_name = "Купленный продукт"
        verbose_name_plural = "Купленные продукты"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
