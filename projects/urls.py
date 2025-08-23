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
    
    # Messaging system
    path('messaging/', views.messaging_home, name='messaging_home'),
    path('messaging/conversation/<int:user_id>/', views.conversation_view, name='conversation_view'),
    path('messaging/users/', views.user_list, name='user_list'),
    path('messaging/send-request/', views.send_message_request, name='send_message_request'),
    path('messaging/approve-request/<int:request_id>/', views.approve_message_request, name='approve_message_request'),
    path('messaging/reject-request/<int:request_id>/', views.reject_message_request, name='reject_message_request'),
    path('messaging/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('messaging/send-message/', views.send_message, name='send_message'),
    path('messaging/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('messaging/notifications/', views.notifications_list, name='notifications_list'),
    path('messaging/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('messaging/notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Author profile URLs
    path('author/<int:author_id>/', views.author_profile, name='author_profile'),
    path('author/edit/', views.edit_author_profile, name='edit_author_profile'),
    
    # Group messaging URLs
    path('group-messaging/', views.group_messaging_home, name='group_messaging_home'),
    path('group-messaging/create/', views.create_group, name='create_group'),
    path('group-messaging/<int:group_id>/', views.group_chat, name='group_chat'),
    path('group-messaging/<int:group_id>/send/', views.send_group_message, name='send_group_message'),
    path('group-messaging/<int:group_id>/invite/', views.invite_to_group, name='invite_to_group'),
    path('group-messaging/invitation/<int:invitation_id>/accept/', views.accept_group_invitation, name='accept_group_invitation'),
    path('group-messaging/invitation/<int:invitation_id>/decline/', views.decline_group_invitation, name='decline_group_invitation'),

     # Charts & analytics
    path('charts/', views.charts_dashboard, name='charts_dashboard'),
    path('api/publications_per_year/', views.publications_per_year, name='publications_per_year'),
    path('api/top_authors/', views.top_authors, name='top_authors'),
]
