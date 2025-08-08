from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth & dashboards
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='Login'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='Admin Dashboard'),

    # Project & publication views
    path('', views.projects_list, name='projects_page'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('publications/', views.publication_list, name='publication_list'),
    path('publications/add/<int:project_id>/', views.add_publication, name='add_publication'),
    path('publications/<int:pk>/', views.publication_detail, name='publication_detail'),
    path('publications/upload/', views.add_publication, name='upload_publication'),

    # Password reset 
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
