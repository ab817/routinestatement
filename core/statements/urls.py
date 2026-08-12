from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path("download/", views.download_statement, name="download_statement"),
    path('logout/', views.user_logout, name='logout'),
]
