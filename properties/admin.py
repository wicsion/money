from django.contrib import admin
from .models import PropertyType, Property, PropertyImage
from .models import ListingType

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'order')
    ordering = ('order',)



@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    actions = ['approve_properties']
    list_display = ('title', 'price', 'property_type', 'status', 'broker', 'developer', 'is_approved', 'created_at')
    list_filter = ('status', 'property_type', 'is_approved', 'is_premium')
    search_fields = ('title', 'description', 'address', 'broker__username', 'developer__username')
    list_editable = ( 'is_approved', 'status',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'property_type', 'is_approved', 'status')
        }),
        ('Характеристики', {
            'fields': ('price', 'living_area', 'total_area', 'rooms', 'location', 'address')
        }),
        ('Метаданные', {
            'fields': ('broker', 'developer', 'is_premium', 'main_image')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [PropertyImageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('broker', 'developer', 'property_type')

    def approve_properties(self, request, queryset):
        queryset.update(is_approved=True, status='active')

    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data and obj.is_approved:
            obj.status = 'active'
        super().save_model(request, obj, form, change)


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image', 'order')
    list_editable = ('order',)
    list_filter = ('property__status',)
    search_fields = ('property__title',)





@admin.action(description='Одобрить выбранные объекты')
def approve_properties(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')  # Поля для отображения
    search_fields = ('name',)


@admin.register(ListingType)
class ListingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('name', 'description')