from django.contrib import admin
from .models import Category, Item, Claim

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'date_posted', 'is_moderated')
    list_filter = ('status', 'is_moderated', 'category')
    search_fields = ('title', 'description', 'user__username')
    actions = ['approve_items']
    
    def approve_items(self, request, queryset):
        queryset.update(is_moderated=True)
        self.message_user(request, f"{queryset.count()} объявлений было одобрено")
    approve_items.short_description = "Одобрить выбранные объявления"

admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Claim)