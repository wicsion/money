from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import DeveloperProfile
from properties.models import Property
from .forms import DeveloperProfileForm


class DeveloperListView(ListView):
    model = DeveloperProfile
    template_name = 'developers/developer_list.html'
    context_object_name = 'developers'
    paginate_by = 10

    def get_queryset(self):
        return DeveloperProfile.objects.filter(is_approved=True)


class DeveloperDetailView(DetailView):
    model = DeveloperProfile
    template_name = 'developers/developer_detail.html'
    context_object_name = 'developer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.filter(
            developer=self.object.user,
            status='active',
            is_approved=True
        )[:6]
        return context


class DeveloperProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DeveloperProfile
    form_class = DeveloperProfileForm
    template_name = 'developers/developer_update.html'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse_lazy('developer-detail', kwargs={'pk': self.object.pk})