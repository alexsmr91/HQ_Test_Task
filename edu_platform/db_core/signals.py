from random import randint
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PurchasedProduct, StudyGroup, UserProfile, Product


@receiver(post_save, sender=UserProfile)
def new_user(sender, instance, created, **kwargs):
    if created:
        instance.role = "student"


@receiver(post_save, sender=PurchasedProduct)
def redistribute_users(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        distribute_users_to_groups(product.id, product.start_datetime)


def distribute_users_to_groups(product_id, start_datetime):
    # Загружаем параметры
    max_students_per_group = Product.objects.get(id=product_id).max_users_per_group
    users = UserProfile.objects.filter(purchasedproduct__product=product_id).distinct()
    u_count = users.count()
    groups = StudyGroup.objects.filter(product_id=product_id)
    current_group_count = groups.count()
    # Считаем целевое количество групп и учеников на группу
    target_group_count = u_count // max_students_per_group
    if u_count % max_students_per_group > 0:
        target_group_count += 1
    target_users_count_per_gr = u_count // target_group_count
    # Проверка начался курс или нет
    # Опоздавших студентов будем зачислять в уже сформированные
    # группы несмотря на ограничение максимального количества студентов
    if start_datetime > timezone.now():
        # Если целевое количество групп увеличилось
        if target_group_count != current_group_count:
            # Добавляем пустые группы
            for _ in range(target_group_count - current_group_count):
                StudyGroup.objects.create(
                    product_id=product_id, name=f"Группа {randint(0,9999)}"
                )
            # Высвобождаем лишних учеников из старых групп в соответствии с целевым количеством учеников на группу
            for group in groups:
                excess_users = group.users.count() - target_users_count_per_gr
                if excess_users > 0:
                    group.users.remove(*group.users.all()[:excess_users])
    # Подгружаем из базы группы и не распределенных студентов
    groups = StudyGroup.objects.filter(product_id=product_id).annotate(
        users_count=Count("users")
    )
    group_user_counts = {group: group.users_count for group in groups}
    users_in_groups = UserProfile.objects.filter(
        purchasedproduct__product=product_id,
        study_groups__product=product_id,
    ).distinct()
    new_users = users.exclude(id__in=users_in_groups.values_list("id", flat=True))
    # Заполняем группы
    for user in new_users:
        group = min(group_user_counts, key=group_user_counts.get)
        group.users.add(user)
        group_user_counts[group] += 1
