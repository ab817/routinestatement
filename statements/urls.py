from django.urls import path
from django.views.generic.base import RedirectView

from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='user_login', permanent=False)),
    path('login/', views.user_login, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path("download/", views.download_statement, name="download_statement"),
    path('logout/', views.user_logout, name='logout'),
]
