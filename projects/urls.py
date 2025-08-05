
from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('add/<int:project_id>/', views.add_publication, name='add_publication'),
    path('', views.publication_list, name='publication_list'),
    path('<int:pk>/', views.publication_detail, name='publication_detail'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

]

