from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
import random
import string

User = get_user_model()


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
    colored_is_approved.boolean = True

    def colored_role(self, obj):
        color_map = {
            'STUDENT': 'blue',
            'LECTURER': 'darkorange',
            'ADMIN': 'purple',
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
            _('UniLink Идентификация'),
            {'fields': ('is_approved', 'faculty_number', 'service_email')}
        ),
        (
            _('Разрешения'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
        (_('Важни дати'), {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('last_login', 'date_joined')

    ordering = ('-date_joined',)
