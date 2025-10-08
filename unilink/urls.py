from django.urls import path
from . import views

app_name = 'unilink'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path('application/choice/', views.application_choice, name='application_choice'),
    path('apply/student/', views.StudentApplicationView.as_view(), name='student_apply'),
    path('apply/lecturer/', views.LecturerApplicationView.as_view(), name='lecturer_apply'),
    path('registration/pending/', views.registration_pending, name='registration_pending'),

    path('', views.home, name='home'),             
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
]
