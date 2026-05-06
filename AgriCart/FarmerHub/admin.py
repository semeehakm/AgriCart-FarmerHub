from django.contrib import admin
from .models import *

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    list_display = ('buyer','seller','product','quantity','amount','status','delivery_status')
    ordering = ('buyer',)
    search_fields = ('buyer__user__first_name','seller__user__first_name','product__product_name')

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # 🔥 Only delivery_status editable
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='CargoStaff').exists():
            return [field.name for field in self.model._meta.fields if field.name != 'delivery_status']
        return []

    # 🔥 Show ONLY delivery_status field in form (clean UI)
    def get_fields(self, request, obj=None):
        if request.user.groups.filter(name='CargoStaff').exists():
            return ['delivery_status']
        return super().get_fields(request, obj)
    


class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'is_top_featured']


   
admin.site.register(Register)
admin.site.register(Seller_register)
admin.site.register(Catagories)
admin.site.register(Product_details, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Booking,BookingAdmin)
admin.site.register(CargoTeam)