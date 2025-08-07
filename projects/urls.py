from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Project-related
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    # Publication-related
    path('', views.publication_list, name='publication_list'),  # now at "/"
    path('<int:pk>/', views.publication_detail, name='publication_detail'),

    # Shared or other
    path('add/<int:project_id>/', views.add_publication, name='add_publication'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('login/', views.custom_login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/accept/<int:pk>/", views.accept_match_request, name="accept_match_request"),

]
