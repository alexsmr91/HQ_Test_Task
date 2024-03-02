from django.contrib import admin
from db_core.models import StudyGroup, Product, PurchasedProduct, Lesson, UserProfile

admin.site.register(UserProfile)
admin.site.register(StudyGroup)
admin.site.register(Product)
admin.site.register(Lesson)
admin.site.register(PurchasedProduct)
