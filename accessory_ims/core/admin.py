from django.contrib import admin
from .models import Product, Category, Sale, StockReconciliation, StoreSettings, UserProfile

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Sale)
admin.site.register(StockReconciliation)
admin.site.register(StoreSettings)
admin.site.register(UserProfile)
