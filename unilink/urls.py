from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'unilink'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='unilink:login'), name='logout'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('registration/pending/', lambda r: r, name='registration_pending'),

    path('', views.dashboard, name='dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
]

