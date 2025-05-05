from datetime import timezone
from django.contrib import admin
from .models import BrokerProfile, BrokerReview
from properties.models import Property

class BrokerPropertyInline(admin.TabularInline):
    model = Property
    fk_name = 'broker'  # Связь через поле broker в Property
    extra = 0
    fields = ('title', 'price', 'location', 'is_approved', 'status')
    readonly_fields = ('title', 'price', 'location')
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'broker_profile'):
            return qs.filter(broker=request.user)
        return qs.none()

class BrokerReviewInline(admin.TabularInline):
    model = BrokerReview
    extra = 0
    readonly_fields = ('client', 'rating', 'comment', 'created_at')
    show_change_link = True

@admin.register(BrokerProfile)
class BrokerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'rating', 'experience', 'is_approved', 'is_archived')
    list_filter = ('is_approved', 'is_archived', 'specialization')
    search_fields = ('user__username', 'user__email', 'license_number')
    list_editable = ('is_approved', 'is_archived')
    fieldsets = (
        (None, {
            'fields': ('user', 'license_number', 'is_approved')
        }),
        ('Информация', {
            'fields': ('experience', 'specialization', 'about', 'avatar', 'rating')
        }),
        ('Подписка', {
            'fields': ('subscription_expiry', 'is_archived', 'archived_at')
        }),
    )
    readonly_fields = ('rating', 'archived_at')
    inlines = [ BrokerReviewInline]

    def get_inline_instances(self, request, obj=None):
        # Добавляем PropertyInline только при редактировании существующего объекта
        if obj:
            return [BrokerPropertyInline(self.model, self.admin_site)] + super().get_inline_instances(request, obj)
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        if obj.is_archived and not obj.archived_at:
            obj.archived_at = timezone.now()
        elif not obj.is_archived and obj.archived_at:
            obj.archived_at = None
        super().save_model(request, obj, form, change)

@admin.register(BrokerReview)
class BrokerReviewAdmin(admin.ModelAdmin):
    list_display = ('broker', 'client', 'rating', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'rating')
    search_fields = ('broker__user__username', 'client__username', 'comment')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)