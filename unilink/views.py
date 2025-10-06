from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.conf import settings

from .forms import CustomUserCreationForm, CustomLoginForm
from .models import Role

def is_student(user):
    return user.is_authenticated and user.role == Role.STUDENT

def is_lecturer(user):
    return user.is_authenticated and user.role == Role.LECTURER


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'unilink/register.html'
    success_url = reverse_lazy('unilink_register_pending')

    def form_valid(self, form):
        self.object = form.save()
        return redirect(self.request, 'unilink/register_pending.html')

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'unilink/login.html'

    def get_success_url(self):
        return reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        error_message = form.errors.get('__all__', ['Невалиден идентификатор или парола.'])[0]
        return render(self.request, self.template_name, {'form': form, 'error_message': error_message})


@login_required
def dashboard(request):
    if request.user.is_student():
        return redirect('unilink:student_dashboard')
    elif request.user.is_lecturer():
        return redirect('unilink:lecturer_dashboard')
    else:
        return render(request, 'unilink/generic_dashboard.html')


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    context = {
        'title': 'Student Dashboard',
        'id_info': request.user.faculty_number or "Няма факултетен номер"
    }
    return render(request, 'unilink/student_dashboard.html', context)

@login_required
@user_passes_test(is_lecturer)
def lecturer_dashboard(request):
    context = {
        'title': 'Lecturer Dashboard',
        'id_info': request.user.service_email or "Няма служебен имейл",
    }
    return render(request, 'unilink/lecturer_dashboard.html', context)
