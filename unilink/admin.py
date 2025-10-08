from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
import random
import string
from .models import Specialty, JobPosting, StudentApplication, LecturerApplication

User = get_user_model()


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_open')
    list_filter = ('is_open',)
    search_fields = ('title',)


@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_username', 'get_priority_1', 'status')
    list_filter = ('status', 'specialty_priority_1')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'egn')

    # Групиране на полетата във формуляра за редактиране
    fieldsets = (
        (_('Основна Информация и Статус'), {
            'fields': ('user', 'status', 'egn', 'date_of_birth', 'phone_number', 'address')
        }),
        (_('Академичен Профил'), {
            'fields': ('high_school', 'gpa', 'certificates')
        }),
        (_('Желани Специалности'), {
            'fields': ('specialty_priority_1', 'specialty_priority_2', 'specialty_priority_3', 'motivation')
        }),
        (_('Допълнителна Информация и Декларации'), {
            'fields': ('extra_info', 'consent_gdpr')
        }),
    )

    readonly_fields = ('consent_gdpr',)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _("Кандидат")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = _("Потребителско Име")

    def get_priority_1(self, obj):
        return obj.specialty_priority_1
    get_priority_1.short_description = _("Първо Желание")


@admin.register(LecturerApplication)
class LecturerApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'applied_job', 'department', 'status')
    list_filter = ('status', 'applied_job')
    search_fields = ('user__first_name', 'user__last_name', 'applied_job__title', 'department')

    fieldsets = (
        (_('Основна Информация и Статус'), {
            'fields': ('user', 'status', 'applied_job', 'title', 'department')
        }),
        (_('Образование и Квалификации'), {
            'fields': ('education_path', 'certifications', 'memberships')
        }),
        (_('Професионален Опит и Принос'), {
            'fields': ('teaching_experience', 'courses_taught', 'research_publications', 'motivation_goals')
        }),
        (_('Документи и Декларации'), {
            'fields': ('document_notes', 'statement_of_truth')
        }),
    )
    readonly_fields = ('statement_of_truth',)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _("Кандидат")



class UserChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    @admin.action(description=_('Одобряване на избрани потребители и генериране на нова парола'))
    def generate_password_action(self, request, queryset):
        updated_count = 0

        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password_length = 12

        for user in queryset:
            new_password = ''.join(random.choice(characters) for i in range(password_length))
            user.set_password(new_password)

            user.is_approved = True
            user.save()

            updated_count += 1

        self.message_user(request, _(f'{updated_count} потребители бяха одобрени и получиха нова парола.'))

    actions = [generate_password_action]

    def colored_is_approved(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', _('Одобрен'))
        return format_html('<span style="color: red; font-weight: bold;">{}</span>', _('Чака Одобрение'))

    colored_is_approved.short_description = _('Статус')
    colored_is_approved.admin_order_field = 'is_approved'
    colored_is_approved.boolean = False

    def colored_role(self, obj):
        color_map = {
            'STUDENT': '#1d4ed8',
            'LECTURER': '#ca8a04',
            'ADMIN': '#9333ea',
        }
        role_display = obj.get_role_display()
        color = color_map.get(obj.role, 'gray')
        return format_html('<span style="color: {}; font-weight: 500;">{}</span>', color, role_display)

    colored_role.short_description = _('Роля')

    list_display = (
        'username',
        'colored_role',
        'first_name',
        'last_name',
        'colored_is_approved',
        'is_active',
        'is_staff'
    )

    list_filter = (
        'is_approved',
        'role',
        'is_staff',
        'is_active',
        'is_superuser'
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'service_email',
        'faculty_number'
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Персонална информация'),
            {'fields': ('first_name', 'last_name', 'email', 'role')}
        ),
        (
            _('UniLink Идентификация и Кандидатстване (Основни FK)'),
            {'fields': (
                'is_approved',
                'faculty_number',
                'applied_specialty',
                'service_email',
                'applied_job_posting'
            )}
        ),
        (
            _('Разрешения'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
        (_('Важни дати'), {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('last_login', 'date_joined')

    ordering = ('-date_joined',)
