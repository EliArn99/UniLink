from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomLoginForm, StudentApplicationForm, LecturerApplicationForm
from .models import Role


def is_student(user):
    return user.is_authenticated and user.role == Role.STUDENT


def is_lecturer(user):
    return user.is_authenticated and user.role == Role.LECTURER


def home(request):
    if request.user.is_authenticated:
        return redirect('unilink:dashboard')

    return render(request, 'unilink/home.html')


def registration_pending(request):
    return render(request, 'unilink/registration_pending.html')


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
        'title': 'Табло на Студента',
        'id_info': request.user.faculty_number or "Няма факултетен номер"
    }
    return render(request, 'unilink/student_dashboard.html', context)


@login_required
@user_passes_test(is_lecturer)
def lecturer_dashboard(request):
    context = {
        'title': 'Табло на Преподавателя',
        'id_info': request.user.service_email or "Няма служебен имейл",
    }
    return render(request, 'unilink/lecturer_dashboard.html', context)


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'unilink/login.html'

    def get_success_url(self):
        return reverse_lazy('unilink:dashboard')

    def form_invalid(self, form):
        error_message = form.errors.get('__all__', ['Невалиден идентификатор или парола.'])[0]
        return render(self.request, self.template_name, {
            'form': form,
            'error': error_message
        })



class BaseApplicationCreateView(CreateView):

    success_url = reverse_lazy('unilink:registration_pending')
    template_name = 'unilink/application_form.html'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = CustomUserCreationForm(self.request.POST if self.request.method == 'POST' else None)
        return context

    def form_valid(self, form):
        user_form = CustomUserCreationForm(self.request.POST)
        if not user_form.is_valid():
            return self.form_invalid(form)

        user = user_form.save(commit=False)
        user.role = self.user_role
        user.is_approved = False  
        user.save()

        self.object = form.save(commit=False)
        self.object.user = user  
        self.object.status = 'SUBMITTED'  
        self.object.save()

        messages.success(self.request,
                         f"Вашето кандидатстване като {user.get_role_display()} е изпратено успешно и очаква одобрение.")

        return super().form_valid(form)


class StudentApplicationView(BaseApplicationCreateView):
    form_class = StudentApplicationForm
    user_role = 'STUDENT'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Кандидатстване за Студент'
        return context


class LecturerApplicationView(BaseApplicationCreateView):
    form_class = LecturerApplicationForm  
    user_role = 'LECTURER'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Кандидатстване за Преподавател'
        return context




def application_choice(request):
    if request.user.is_authenticated:
        return redirect('unilink:dashboard')

    context = {
        'title': 'Избор на Кандидатстване',
    }
    return render(request, 'unilink/application_choice.html', context)


class CustomLogoutView(LogoutView):
    next_page = 'unilink:login'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Успешно излязохте от системата. Очакваме Ви отново!")
        return super().dispatch(request, *args, **kwargs)
