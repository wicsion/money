from django.shortcuts import redirect
from django.contrib import messages

from .models import UserActivity, Property


class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                action=f"Посещение страницы: {request.path}"
            )
        return response


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def __call__(self, request):
            if request.user.is_authenticated:
                print(f"Профиль завершен: {request.user.is_profile_complete}")
                print(f"Данные пользователя: {request.user.__dict__}")

        excluded_paths = [
            '/accounts/logout/',
            '/static/',
            '/media/',
            '/accounts/verify-email/',
            '/accounts/invalid-token/',
            '/accounts/login/',
            '/accounts/select-role/',
            '/accounts/dashboard/',
            '/accounts/complete-registration/',
            '/broker/',
            '/api/chat/',
            '/api/typing/'
        ]

        if request.user.is_authenticated:
            if not request.user.is_profile_complete:
                if request.path not in excluded_paths:
                    return redirect('complete_registration')

        return self.get_response(request)


class DeveloperModerationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated
            and request.user.is_developer
            and not request.path.startswith('/admin/')):
            unapproved_count = Property.objects.filter(
                creator=request.user,
                is_approved=False
            ).count()
            if unapproved_count > 0:
                messages.info(request, f"У вас {unapproved_count} объектов на модерации")
        return self.get_response(request)