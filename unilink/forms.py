from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field
from .models import Role, Specialty, JobPosting, StudentApplication, LecturerApplication
import re

User = get_user_model()



class CustomUserCreationForm(UserCreationForm):

    role = forms.ChoiceField(
        choices=[(Role.STUDENT, _('Студент')), (Role.LECTURER, _('Преподавател'))],
        label=_("Искана Роля"),
        widget=forms.RadioSelect
    )
    first_name = forms.CharField(max_length=150, required=True, label=_("Име"))
    last_name = forms.CharField(max_length=150, required=True, label=_("Фамилия"))
    email = forms.EmailField(required=True, label=_("Личен Имейл"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'username')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = False
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):

    username = forms.CharField(
        max_length=254,
        label=_("Идентификатор (Потребителско име)"),
        widget=forms.TextInput(attrs={'autofocus': True})
    )




class StudentApplicationForm(forms.ModelForm):

    specialty_queryset = Specialty.objects.filter(is_active=True)

    specialty_priority_1 = forms.ModelChoiceField(
        queryset=specialty_queryset,
        required=True,
        label=StudentApplication._meta.get_field('specialty_priority_1').verbose_name,
        empty_label=_("Избери първа специалност")
    )
    specialty_priority_2 = forms.ModelChoiceField(
        queryset=specialty_queryset,
        required=False,
        label=StudentApplication._meta.get_field('specialty_priority_2').verbose_name,
        empty_label=_("Избери втора специалност (по избор)")
    )
    specialty_priority_3 = forms.ModelChoiceField(
        queryset=specialty_queryset,
        required=False,
        label=StudentApplication._meta.get_field('specialty_priority_3').verbose_name,
        empty_label=_("Избери трета специалност (по избор)")
    )

    data_verified = forms.BooleanField(
        required=True,
        label=_("Потвърждавам, че всички въведени данни са верни и пълни.")
    )

    class Meta:
        model = StudentApplication
        fields = [
            'egn', 'date_of_birth', 'phone_number', 'address',
            'high_school', 'gpa', 'certificates',
            'specialty_priority_1', 'specialty_priority_2', 'specialty_priority_3', 'motivation',
            'extra_info', 'consent_gdpr',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'motivation': forms.Textarea(attrs={'rows': 4}),
            'extra_info': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Лични и Контактни Данни'),
                'egn',
                'date_of_birth',
                'phone_number',
                'address',
            ),
            Fieldset(
                _('Образователен Профил'),
                'high_school',
                'gpa',
                Field('certificates', rows=3),
            ),
            Fieldset(
                _('Предпочитания за Специалност'),
                'specialty_priority_1',
                'specialty_priority_2',
                'specialty_priority_3',
                Field('motivation', rows=4),
            ),
            Fieldset(
                _('Допълнителна Информация'),
                Field('extra_info', rows=3),
                'consent_gdpr',
                'data_verified'
            ),
            Submit('submit', _('Подай Кандидатура'))
        )

    def clean_egn(self):
        egn = self.cleaned_data.get('egn')
        if egn and not re.match(r'^\d{10}$', egn):
            raise forms.ValidationError(_("ЕГН/ЛНЧ трябва да съдържа точно 10 цифри."))
        return egn

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('specialty_priority_1')
        p2 = cleaned_data.get('specialty_priority_2')
        p3 = cleaned_data.get('specialty_priority_3')

        selected_specialties = [s for s in [p1, p2, p3] if s is not None]

        if len(selected_specialties) != len(set(selected_specialties)):
            raise forms.ValidationError(_("Специалностите в приоритетните желания трябва да бъдат уникални."))

        return cleaned_data


class LecturerApplicationForm(forms.ModelForm):
    applied_job = forms.ModelChoiceField(
        queryset=JobPosting.objects.filter(is_open=True),
        required=True,
        label=LecturerApplication._meta.get_field('applied_job').verbose_name,
        empty_label=_("Избери обява за работа")
    )

    class Meta:
        model = LecturerApplication
        fields = [
            'title', 'department',
            'education_path', 'certifications', 'memberships',
            'teaching_experience', 'courses_taught', 'research_publications',
            'applied_job', 'motivation_goals',
            'document_notes', 'statement_of_truth'
        ]
        widgets = {
            'education_path': forms.Textarea(attrs={'rows': 3}),
            'certifications': forms.Textarea(attrs={'rows': 2}),
            'memberships': forms.Textarea(attrs={'rows': 2}),
            'teaching_experience': forms.Textarea(attrs={'rows': 4}),
            'courses_taught': forms.Textarea(attrs={'rows': 3}),
            'research_publications': forms.Textarea(attrs={'rows': 4}),
            'motivation_goals': forms.Textarea(attrs={'rows': 4}),
            'document_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Основна Информация и Позиция'),
                'title',
                'department',
                'applied_job',
            ),
            Fieldset(
                _('Образование и Квалификации'),
                Field('education_path', rows=3),
                Field('certifications', rows=2),
                Field('memberships', rows=2),
            ),
            Fieldset(
                _('Професионален Опит и Принос'),
                Field('teaching_experience', rows=4),
                Field('courses_taught', rows=3),
                Field('research_publications', rows=4),
                Field('motivation_goals', rows=4),
            ),
            Fieldset(
                _('Документи и Декларации'),
                Field('document_notes', rows=2),
                'statement_of_truth',
            ),
            Submit('submit', _('Подай Кандидатура'))
        )
