from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    STUDENT = 'STUDENT', _('Студент')
    LECTURER = 'LECTURER', _('Преподавател')
    ADMIN = 'ADMIN', _('Администратор')


class User(AbstractUser):
    role = models.CharField(
        _('Роля'),
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    faculty_number = models.CharField(
        _('Факултетен Номер'),
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Използва се за вход от студенти.")
    )

    service_email = models.EmailField(
        _('Служебен Имейл'),
        unique=True,
        null=True,
        blank=True,
        help_text=_("Използва се за вход от преподаватели.")
    )

    is_approved = models.BooleanField(
        _('Одобрен'),
        default=False,
        help_text=_('Определя дали потребителят е одобрен от администратор за вход.')
    )

    email = models.EmailField(_('Имейл адрес'), blank=True)

    def __str__(self):
        if self.role == Role.STUDENT and self.faculty_number:
            return f"{self.first_name} {self.last_name} ({self.faculty_number})"
        elif self.role == Role.LECTURER and self.service_email:
            return f"{self.first_name} {self.last_name} ({self.service_email})"
        return self.username

    def save(self, *args, **kwargs):
        if self.role == Role.LECTURER and not self.service_email and self.first_name and self.last_name:
            first = self.first_name.lower().replace(" ", "")
            last = self.last_name.lower().replace(" ", "")
            self.service_email = f"{first}.{last}@unilink.bg"

        super().save(*args, **kwargs)

    def is_student(self):
        return self.role == Role.STUDENT

    def is_lecturer(self):
        return self.role == Role.LECTURER
