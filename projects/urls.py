from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth & dashboards
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('administrator_dashboard/', views.administrator_dashboard, name='administrator_dashboard'),
    path("accept_match_request/<int:pk>/", views.accept_match_request, name="accept_match_request"),

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
