from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("download/", views.download_statement, name="download_statement"),
    path('logout/', views.user_logout, name='logout'),
]
