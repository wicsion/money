from django.contrib import admin
from .models import DeveloperProfile
from properties.models import Property

class DeveloperPropertyInline(admin.TabularInline):
    model = Property
    fk_name = 'developer'  # Связь через поле developer в Property
    extra = 0
    fields = ('title', 'price', 'location', 'is_approved', 'status')
    readonly_fields = ('title', 'price', 'location')
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'developer_profile'):
            return qs.filter(developer=request.user)
        return qs.none()

@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'year_founded', 'projects_completed', 'is_approved')
    list_filter = ('is_approved', 'year_founded')
    search_fields = ('company_name', 'user__username', 'user__email')
    list_editable = ('is_approved',)
    fieldsets = (
        (None, {
            'fields': ('user', 'company_name', 'is_approved')
        }),
        ('Информация о компании', {
            'fields': ('description', 'year_founded', 'projects_completed', 'logo')
        }),
    )
    def get_inline_instances(self, request, obj=None):
        # Добавляем PropertyInline только при редактировании существующего объекта
        if obj:
            return [DeveloperPropertyInline(self.model, self.admin_site)] + super().get_inline_instances(request, obj)
        return super().get_inline_instances(request, obj)