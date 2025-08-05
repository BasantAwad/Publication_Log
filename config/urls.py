"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from projects import views  # for the custom view below

urlpatterns = [
    path('', lambda request: redirect('project_list')),  # Redirect root to project list
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),  # Mount all routes from projects.urls directly
    path("upload/<str:token>/", views.add_publication, name="add_publication"),  # standalone
     path('accounts/', include('django.contrib.auth.urls')),
     path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
     path("admin-dashboard/accept/<int:pk>/", views.accept_match_request, name="accept_match_request"),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

