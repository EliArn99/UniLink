from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import date


class Role(models.TextChoices):
    STUDENT = 'STUDENT', _('Студент')
    LECTURER = 'LECTURER', _('Преподавател')
    ADMIN = 'ADMIN', _('Администратор')



class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Име на специалността"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))

    class Meta:
        verbose_name = _("Специалност")
        verbose_name_plural = _("Специалности")
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    title = models.CharField(max_length=150, verbose_name=_("Заглавие на обявата"))
    description = models.TextField(verbose_name=_("Изисквания/Описание"))
    is_open = models.BooleanField(default=True, verbose_name=_("Отворена за кандидатстване"))

    class Meta:
        verbose_name = _("Обява за Работа")
        verbose_name_plural = _("Обяви за Работа")
        ordering = ['-is_open', 'title']

    def __str__(self):
        return self.title



class StudentApplication(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True, verbose_name=_("Потребител"))
    egn = models.CharField(max_length=10, unique=True, verbose_name=_("ЕГН/ЛНЧ"))
    date_of_birth = models.DateField(verbose_name=_("Дата на раждане"), default=date(2000, 1, 1))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон"))
    address = models.TextField(blank=True, verbose_name=_("Адрес"))

    high_school = models.CharField(max_length=255, verbose_name=_("Завършено средно училище"))
    gpa = models.DecimalField(max_digits=3, decimal_places=2, verbose_name=_("Среден успех (GPA)"))
    certificates = models.TextField(blank=True, verbose_name=_("Сертификати/Езикови удостоверения"))

    specialty_priority_1 = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True,
                                             related_name='applicants_p1', verbose_name=_("Първо желание"))
    specialty_priority_2 = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='applicants_p2', verbose_name=_("Второ желание"))
    specialty_priority_3 = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='applicants_p3', verbose_name=_("Трето желание"))
    motivation = models.TextField(verbose_name=_("Мотивация за избора"))

    extra_info = models.TextField(blank=True, verbose_name=_("Участие в състезания/Доброволчество"))

    consent_gdpr = models.BooleanField(default=False, verbose_name=_("Съгласие за обработка на лични данни"))

    STATUS_CHOICES = [
        ('SUBMITTED', _('Подаден')),
        ('IN_REVIEW', _('В обработка')),
        ('APPROVED', _('Одобрен')),
        ('ACCEPTED', _('Приет')),
        ('REJECTED', _('Отказан')),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED', verbose_name=_("Статус"))

    class Meta:
        verbose_name = _("Студентско Кандидатстване")
        verbose_name_plural = _("Студентски Кандидатствания")

    def __str__(self):
        return f"Кандидатура на {self.user.get_full_name()}"


class LecturerApplication(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True, verbose_name=_("Потребител"))
    title = models.CharField(max_length=50, blank=True, verbose_name=_("Титла/Степен"))
    department = models.CharField(max_length=150, blank=True, verbose_name=_("Факултет/Катедра"))

    education_path = models.TextField(verbose_name=_("Образователен път (Бакалавър, Доктор и т.н.)"))
    certifications = models.TextField(blank=True, verbose_name=_("Специализации и сертифицирани курсове"))
    memberships = models.TextField(blank=True, verbose_name=_("Професионални членства"))

    teaching_experience = models.TextField(verbose_name=_("Преподавателски стаж"))
    courses_taught = models.TextField(verbose_name=_("Ръководени курсове и дисциплини"))
    research_publications = models.TextField(verbose_name=_("Проекти, изследвания, публикации"))

    applied_job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, verbose_name=_("Кандидатства за позиция"))
    motivation_goals = models.TextField(verbose_name=_("Мотивация и цели/Принос"))

    document_notes = models.TextField(blank=True, verbose_name=_("Бележки за прикачени документи (CV, Дипломи)"))

    # Декларации
    statement_of_truth = models.BooleanField(default=False, verbose_name=_("Потвърждение за достоверност на данните"))

    STATUS_CHOICES = [
        ('SUBMITTED', _('Подаден')),
        ('IN_REVIEW', _('На разглеждане')),
        ('INTERVIEW', _('Интервю')),
        ('APPROVED', _('Одобрен')),
        ('REJECTED', _('Отказан')),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED', verbose_name=_("Статус"))

    class Meta:
        verbose_name = _("Преподавателско Кандидатстване")
        verbose_name_plural = _("Преподавателски Кандидатствания")

    def __str__(self):
        return f"Кандидатура на {self.user.get_full_name()} за {self.applied_job.title}"


class User(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_("Роля")
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Одобрен от Администратор"),
        help_text=_('Определя дали потребителят е одобрен от администратор за вход.')
    )

    faculty_number = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Факултетен Номер"),
        help_text=_("Използва се за вход от студенти.")
    )
    applied_specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Кандидатствана Специалност (Осн. Модел)"),
        help_text=_("Избраната специалност по време на кандидатстването.")
    )

    service_email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Служебен Имейл"),
        help_text=_("Използва се за вход от преподаватели/служители.")
    )
    applied_job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Кандидатствана Позиция (Осн. Модел)"),
        help_text=_("Избраната позиция по време на кандидатстването.")
    )

    class Meta:
        verbose_name = _("Потребител")
        verbose_name_plural = _("Потребители")

    def is_student(self):
        return self.role == Role.STUDENT

    def is_lecturer(self):
        return self.role == Role.LECTURER

    def is_admin(self):
        return self.role == Role.ADMIN or self.is_staff

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return self.username
