from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Count, Max
from django.utils import timezone
from datetime import timedelta
import json

from projects.models import MatchRequest, AVATAR_CHOICES

from .email import notify_invalid_publication_url,send_welcome_email
from .forms import (
    MessageForm,
    MessageRequestForm,
    PublicationForm,
    UserCreation,
    UserUpdateForm,
)
from .models import Message, MessageRequest, Notification, Project, Publication, UserProfile

# ========================
# Project Views
# ========================

def projects_list(request):
    """
    Display a list of all projects with optional filtering by search, domain, year, and sorting.
    - Allows searching by project title, filtering by domain and year, and sorting by creation date.
    - Also provides lists of available domains and years for filter dropdowns.
    """
    projects = Project.objects.all()

    search_query = request.GET.get('search', '')
    domain = request.GET.get('domain', '')
    year = request.GET.get('year', '')
    sort = request.GET.get('sort', '')

    if search_query:
        projects = projects.filter(title__istartswith=search_query)

    if domain:
        projects = projects.filter(domain=domain)
    if year:
        projects = projects.filter(created__year=year)
    if sort == 'newest':
        projects = projects.order_by('-created')
    elif sort == 'oldest':
        projects = projects.order_by('created')

    # Get all distinct domains and years for filters
    domains = Project.objects.values_list('domain', flat=True).distinct()
    years = Project.objects.annotate(year=ExtractYear('created')).values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'projects': projects,
        'search_query': search_query,
        'selected_domain': domain,
        'selected_year': year,
        'selected_sort': sort,
        'domains': domains,
        'years': years,
    }
    return render(request, 'projects/projects_page.html', context)

def project_detail(request, pk):
    """
    Show details of a single project, including its related publications and collaborators.
    """
    project = get_object_or_404(Project, pk=pk)
    publications = project.publications.all().prefetch_related('collaborators')
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'publications': publications
    })

@login_required
def add_publication(request, project_id):
    """
    Allow logged-in users to add a publication to a specified project.
    - Handles file upload, validation, and triggers email notification for invalid URLs.
    """
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, project=project)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.project = project
            publication.save()
            form.save_m2m()

            # Check publication URL validity and send notification if needed
            if publication.url:
                notify_invalid_publication_url(publication)

            return redirect('project_detail', pk=project.id)
    else:
        form = PublicationForm(project=project)

    return render(request, 'publications/add_publication.html', {'form': form, 'project': project})

# ========================
# Publication Views
# ========================

def publication_detail(request, pk):
    """
    Show details of a single publication.
    """
    publication = get_object_or_404(Publication, pk=pk)
    return render(request, 'publications/publication_detail.html', {'publication': publication})

def publication_list(request):
    """
    Display a list of all publications with filters for search, domain, year, type, and sorting.
    - Allows filtering by publication type, domain, and year.
    - Provides dropdowns for available domains, years, and types.
    """
    publications = Publication.objects.all()

    search_query = request.GET.get('search', '').strip()
    selected_domain = request.GET.get('domain', '')
    selected_year = request.GET.get('year', '')
    selected_type = request.GET.get('type', '')   # Publication type filter
    selected_sort = request.GET.get('sort', 'newest')

    if search_query:
        publications = publications.filter(title__icontains=search_query)

    if selected_domain:
        publications = publications.filter(project__domain=selected_domain)

    if selected_year:
        try:
            year_int = int(selected_year)
            publications = publications.filter(year=year_int)
        except ValueError:
            pass  # Ignore filtering if year is not numeric

    if selected_type:
        publications = publications.filter(type=selected_type)

    if selected_sort == 'newest':
        publications = publications.order_by('-year', '-id')
    else:
        publications = publications.order_by('year', 'id')

    # Prepare lists for filters
    domains = Project.objects.values_list('domain', flat=True).distinct()
    years = Publication.objects.values_list('year', flat=True).distinct().order_by('-year')
    types = [choice[0] for choice in Publication._meta.get_field('type').choices]  # All publication types

    context = {
        'publications': publications,
        'search_query': search_query,
        'selected_domain': selected_domain,
        'selected_year': selected_year,
        'selected_type': selected_type,
        'selected_sort': selected_sort,
        'domains': domains,
        'years': years,
        'types': types,
    }

    return render(request, 'publications/publication_list.html', context)

# ========================
# User Dashboard & Auth Views
# ========================

@login_required
def user_dashboard(request):
    """
    Display the dashboard for the logged-in user.
    - Shows user's own publications and projects they collaborate on.
    - Allows updating user profile information.
    """
    user = request.user
    # Get publications where user is primary author or collaborator
    publications = Publication.objects.filter(
        models.Q(primary_author__email=user.email) | 
        models.Q(collaborators__email=user.email)
    ).distinct()
    collaborated_projects = Project.objects.filter(team__icontains=user.username)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('user_dashboard')
    else:
        form = UserUpdateForm(instance=user)

    notifications = Notification.objects.filter(user=user, is_read=False)
    notif_count = notifications.count()

    return render(request, 'registration/user_dashboard.html', {
        'user': user,
        'form': form,
        'publications': publications,
        'collaborated_projects': collaborated_projects,
        'profile': profile,
        'avatar_choices': AVATAR_CHOICES,
        'notifications': notifications,
        'notif_count': notif_count,
    })

def administrator_dashboard(request):
    """
    Display the dashboard for administrators.
    - Shows all pending match requests that have not been reviewed.
    """
    pending_requests = MatchRequest.objects.filter(approved__isnull=True).order_by("-id")
    return render(request, "registration/administrator_dashboard.html", {"match_requests": pending_requests})

def login(request):
    """
    Show login page and authenticate users.
    - Redirects staff/superusers to administrator dashboard, others to user dashboard.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('administrator_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Log out the user and redirect to login page.
    """
    logout(request)
    return redirect('login')

def signup(request):
    """
    Show the sign-up page and handle user registration.
    - Sends welcome email after successful registration.
    """
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            send_welcome_email(request ,user)
            return redirect('user_dashboard')  
    else:
        form = UserCreation()

    return render(request, 'registration/signup.html', {'form': form})

# ========================
# Administrator Actions
# ========================

@require_POST
def accept_match_request(request, pk):
    """
    Process administrator's decision to accept or reject a match request.
    - Sets the 'approved' field on the MatchRequest object.
    """
    match = get_object_or_404(MatchRequest, pk=pk)
    decision = request.POST.get("decision")

    if decision in ["yes", "no"]:
        match.approved = (decision == "yes")
        match.save()
    
    return redirect("administrator_dashboard")

@login_required
def messaging(request):
    requests_pending = MessageRequest.objects.filter(recipient=request.user, status='pending')
    conversations = MessageRequest.objects.filter(Q(sender=request.user) | Q(recipient=request.user), status='approved').order_by('-sent_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notif_count = notifications.count()
    return render(request, 'messaging.html', {
        'requests_pending': requests_pending,
        'conversations': conversations,
        'notifications': notifications,
        'notif_count': notif_count,
    })

@login_required
def message_request(request, user_id):
    recipient = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        MessageRequest.objects.get_or_create(sender=request.user, recipient=recipient, status='pending')
        return redirect('messaging')
    return render(request, 'message_request.html', {'recipient': recipient})

@login_required
def message_approve(request, request_id):
    msg_req = get_object_or_404(MessageRequest, pk=request_id, recipient=request.user)
    if request.method == "POST":
        msg_req.status = 'approved'
        msg_req.save()
        return redirect('messaging')
    return render(request, 'message_approve.html', {'msg_req': msg_req})

@login_required
def conversation(request, request_id):
    msg_req = get_object_or_404(MessageRequest, pk=request_id, status='approved')
    messages_ = Message.objects.filter(request=msg_req).order_by('sent_at')
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            msg = Message.objects.create(
                sender=request.user,
                recipient=msg_req.recipient if msg_req.sender == request.user else msg_req.sender,
                content=content,
                request=msg_req
            )
            Notification.objects.create(user=msg.recipient, message=msg, notification_type="unread_message")
            send_mail(
                'New Message Received',
                f'You have received a new message from {msg.sender.username}: "{msg.content[:100]}"',
                'noreply@yourdomain.com',
                [msg.recipient.email],
                fail_silently=True,
            )
        return redirect('conversation', request_id=msg_req.id)
    Message.objects.filter(request=msg_req, recipient=request.user, is_read=False).update(is_read=True)
    Notification.objects.filter(user=request.user, message__request=msg_req, is_read=False).update(is_read=True)
    return render(request, 'conversation.html', {
        'messages': messages_,
        'msg_req': msg_req,
    })

@login_required
def notifications_api(request):
    notifs = Notification.objects.filter(user=request.user, is_read=False)
    notif_list = [{
        'id': n.id,
        'text': f'New message from {n.message.sender.username}' if n.message else 'Notification',
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        'message_url': f'/conversation/{n.message.request.id}/' if n.message else ''
    } for n in notifs]
    return JsonResponse({'notifications': notif_list, 'count': notifs.count()})

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, pk=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})

@login_required
def messaging_home(request):
    """Main messaging page with user list and conversation view"""
    # Get all users the current user has interacted with (sent/received messages or requests)
    user_interactions = get_user_interactions(request.user)
    
    # Get pending message requests
    pending_requests = MessageRequest.objects.filter(
        recipient=request.user,
        status='pending'
    ).select_related('sender')
    
    # Get unread notifications count
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'user_interactions': user_interactions,
        'pending_requests': pending_requests,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'messaging/messaging_home.html', context)

@login_required
def conversation_view(request, user_id):
    """View conversation with a specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if there's an approved request between users
    approved_request = MessageRequest.objects.filter(
        ((Q(sender=request.user, recipient=other_user) |
          Q(sender=other_user, recipient=request.user)) &
         Q(status='approved'))
    ).first()
    
    if not approved_request:
        messages.error(request, "You need an approved message request to view this conversation.")
        return redirect('messaging_home')
    
    # Get messages between users
    messages_list = Message.objects.filter(
        ((Q(sender=request.user, recipient=other_user) |
          Q(sender=other_user, recipient=request.user)))
    ).order_by('sent_at')
    
    # Mark messages as read
    messages_list.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
        'approved_request': approved_request,
    }
    
    return render(request, 'messaging/conversation.html', context)

@login_required
def user_list(request):
    """Get list of users for messaging"""
    # Get all users except current user
    users = User.objects.exclude(id=request.user.id).select_related('userprofile')
    
    # Get interaction status for each user
    user_list_data = []
    for user in users:
        interaction_status = get_interaction_status(request.user, user)
        user_list_data.append({
            'user': user,
            'interaction_status': interaction_status,
        })
    
    return JsonResponse({'users': user_list_data})

@login_required
def send_message_request(request):
    """Send a message request to another user"""
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        message_text = data.get('message', '')
        
        if not recipient_id:
            return JsonResponse({'error': 'Recipient ID is required'}, status=400)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Check if request already exists
        existing_request = MessageRequest.objects.filter(
            Q(sender=request.user, recipient=recipient) |
            Q(sender=recipient, recipient=request.user)
        ).first()
        
        if existing_request:
            return JsonResponse({'error': 'A message request already exists with this user'}, status=400)
        
        # Create message request
        message_request = MessageRequest.objects.create(
            sender=request.user,
            recipient=recipient,
            initial_message=message_text
        )
        
        # Create notification
        Notification.objects.create(
            user=recipient,
            message_request=message_request,
            notification_type='message_request',
            title=f"Message request from {request.user.username}",
            content=f"{request.user.username} wants to start a conversation with you"
        )
        
        return JsonResponse({
            'success': True,
            'request_id': message_request.id,
            'message': 'Message request sent successfully'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def approve_message_request(request, request_id):
    """Approve a message request"""
    message_request = get_object_or_404(MessageRequest, id=request_id, recipient=request.user)
    
    if message_request.status != 'pending':
        return JsonResponse({'error': 'Request is not pending'}, status=400)
    
    message_request.status = 'approved'
    message_request.save()
    
    # Create notification for sender
    Notification.objects.create(
        user=message_request.sender,
        message_request=message_request,
        notification_type='request_approved',
        title=f"Message request approved by {request.user.username}",
        content=f"{request.user.username} approved your message request"
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Message request approved'
    })

@login_required
def reject_message_request(request, request_id):
    """Reject a message request"""
    message_request = get_object_or_404(MessageRequest, id=request_id, recipient=request.user)
    
    if message_request.status != 'pending':
        return JsonResponse({'error': 'Request is not pending'}, status=400)
    
    message_request.status = 'rejected'
    message_request.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Message request rejected'
    })

@login_required
def get_messages(request, user_id):
    """Get messages between current user and another user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if there's an approved request
    approved_request = MessageRequest.objects.filter(
        ((Q(sender=request.user, recipient=other_user) |
          Q(sender=other_user, recipient=request.user)) &
         Q(status='approved'))
    ).first()
    
    if not approved_request:
        return JsonResponse({'error': 'No approved message request found'}, status=403)
    
    # Get messages
    messages_list = Message.objects.filter(
        ((Q(sender=request.user, recipient=other_user) |
          Q(sender=other_user, recipient=request.user)))
    ).order_by('sent_at')
    
    # Mark messages as read
    messages_list.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    messages_data = []
    for msg in messages_list:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'content': msg.content,
            'sent_at': msg.sent_at.isoformat(),
            'is_read': msg.is_read,
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
def send_message(request):
    """Send a message to another user"""
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        
        if not recipient_id or not content:
            return JsonResponse({'error': 'Recipient ID and content are required'}, status=400)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Check if there's an approved request
        approved_request = MessageRequest.objects.filter(
            ((Q(sender=request.user, recipient=recipient) |
              Q(sender=recipient, recipient=request.user)) &
             Q(status='approved'))
        ).first()
        
        if not approved_request:
            return JsonResponse({'error': 'You need an approved message request to send messages'}, status=403)
        
        # Create message
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            request=approved_request
        )
        
        # Create notification
        Notification.objects.create(
            user=recipient,
            message=message,
            notification_type='message_received',
            title=f"New message from {request.user.username}",
            content=f"You received a new message from {request.user.username}"
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'message': 'Message sent successfully'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.mark_as_read()
    
    return JsonResponse({'success': True})

@login_required
def notifications_list(request):
    """Get user's notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'content': notification.content,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
        })
    
    return JsonResponse({'notifications': notifications_data})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({'success': True})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({'success': True})

# Helper functions
def get_user_interactions(user):
    """Get all users the current user has interacted with"""
    # Get users from message requests
    request_users = User.objects.filter(
        Q(sent_requests__recipient=user) | Q(received_requests__sender=user)
    ).distinct()
    
    # Get users from messages
    message_users = User.objects.filter(
        Q(messages_sent__recipient=user) | Q(messages_received__sender=user)
    ).distinct()
    
    # Combine and get unique users
    all_users = list(request_users) + list(message_users)
    unique_users = list({user.id: user for user in all_users}.values())
    
    # Add interaction status for each user
    user_interactions = []
    for other_user in unique_users:
        if other_user.id != user.id:
            interaction_status = get_interaction_status(user, other_user)
            user_interactions.append({
                'user': other_user,
                'interaction_status': interaction_status,
            })
    
    return user_interactions

def get_interaction_status(user1, user2):
    """Get the interaction status between two users"""
    # Check for message request
    request = MessageRequest.objects.filter(
        Q(sender=user1, recipient=user2) | Q(sender=user2, recipient=user1)
    ).first()
    
    if request:
        if request.status == 'pending':
            if request.sender == user1:
                return 'request_sent'
            else:
                return 'request_received'
        elif request.status == 'approved':
            return 'approved'
        elif request.status == 'rejected':
            return 'rejected'
    
    return 'no_interaction'

# ========================
# AUTHOR PROFILE VIEWS
# ========================

@login_required
def author_profile(request, author_id):
    """View author profile with their publications and information"""
    author = get_object_or_404(Author, id=author_id)
    
    # Get author's publications
    publications = Publication.objects.filter(
        Q(primary_author=author) | Q(collaborators=author)
    ).distinct().order_by('-year')
    
    # Check if current user can message this author
    can_message = False
    if hasattr(author, 'user') and author.user:
        can_message = author.user != request.user
    
    # Get interaction status if author has a user account
    interaction_status = None
    if hasattr(author, 'user') and author.user:
        interaction_status = get_interaction_status(request.user, author.user)
    
    context = {
        'author': author,
        'publications': publications,
        'can_message': can_message,
        'interaction_status': interaction_status,
    }
    
    return render(request, 'authors/author_profile.html', context)

@login_required
def edit_author_profile(request):
    """Edit current user's author profile"""
    try:
        author = Author.objects.get(email=request.user.email)
    except Author.DoesNotExist:
        # Create author profile if it doesn't exist
        author = Author.objects.create(
            name=request.user.username,
            email=request.user.email
        )
    
    if request.method == 'POST':
        # Handle profile update
        author.name = request.POST.get('name', author.name)
        author.research_interests = request.POST.get('research_interests', author.research_interests)
        author.institution = request.POST.get('institution', author.institution)
        author.department = request.POST.get('department', author.department)
        author.orcid_id = request.POST.get('orcid_id', author.orcid_id)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            author.profile_picture = request.FILES['profile_picture']
        
        author.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('author_profile', author_id=author.id)
    
    context = {
        'author': author,
    }
    
    return render(request, 'authors/edit_author_profile.html', context)

# ========================
# GROUP MESSAGING VIEWS
# ========================

@login_required
def group_messaging_home(request):
    """Main group messaging page"""
    # Get user's groups
    user_groups = GroupChat.objects.filter(members=request.user, is_active=True)
    
    # Get pending group invitations
    pending_invitations = GroupInvitation.objects.filter(
        invitee=request.user,
        status='pending'
    ).select_related('group', 'inviter')
    
    context = {
        'user_groups': user_groups,
        'pending_invitations': pending_invitations,
    }
    
    return render(request, 'messaging/group_messaging_home.html', context)

@login_required
def create_group(request):
    """Create a new group chat"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        member_ids = request.POST.getlist('members')
        
        if name:
            group = GroupChat.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            
            # Add creator as member
            group.members.add(request.user)
            
            # Add selected members
            if member_ids:
                members = User.objects.filter(id__in=member_ids)
                group.members.add(*members)
            
            messages.success(request, f'Group "{name}" created successfully!')
            return redirect('group_chat', group_id=group.id)
    
    # Get all users for member selection
    users = User.objects.exclude(id=request.user.id)
    
    context = {
        'users': users,
    }
    
    return render(request, 'messaging/create_group.html', context)

@login_required
def group_chat(request, group_id):
    """View group chat"""
    group = get_object_or_404(GroupChat, id=group_id, members=request.user)
    
    # Get group messages
    messages = GroupMessage.objects.filter(group=group).order_by('sent_at')
    
    # Mark messages as read by current user
    for message in messages:
        if message.sender != request.user:
            message.mark_as_read_by(request.user)
    
    context = {
        'group': group,
        'messages': messages,
    }
    
    return render(request, 'messaging/group_chat.html', context)

@login_required
def send_group_message(request, group_id):
    """Send a message to group"""
    if request.method == 'POST':
        group = get_object_or_404(GroupChat, id=group_id, members=request.user)
        content = request.POST.get('content')
        
        if content:
            message = GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=content
            )
            
            # Send email notifications to offline members
            offline_members = group.members.exclude(id=request.user.id).filter(
                userprofile__is_online=False
            )
            
            if offline_members.exists():
                from .email import send_group_message_notification_email
                send_group_message_notification_email(
                    offline_members, request.user, group.name, content
                )
            
            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'sender_name': request.user.username,
                'sent_at': message.sent_at.isoformat()
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def invite_to_group(request, group_id):
    """Invite user to group"""
    if request.method == 'POST':
        group = get_object_or_404(GroupChat, id=group_id, created_by=request.user)
        invitee_id = request.POST.get('invitee_id')
        message = request.POST.get('message', '')
        
        if invitee_id:
            invitee = get_object_or_404(User, id=invitee_id)
            
            # Check if invitation already exists
            invitation, created = GroupInvitation.objects.get_or_create(
                group=group,
                invitee=invitee,
                defaults={
                    'inviter': request.user,
                    'message': message
                }
            )
            
            if created:
                messages.success(request, f'Invitation sent to {invitee.username}')
            else:
                messages.info(request, f'{invitee.username} already has an invitation')
            
            return redirect('group_chat', group_id=group.id)
    
    # Get users not in the group
    group = get_object_or_404(GroupChat, id=group_id, created_by=request.user)
    available_users = User.objects.exclude(
        Q(id__in=group.members.values_list('id', flat=True)) |
        Q(id=request.user.id)
    )
    
    context = {
        'group': group,
        'available_users': available_users,
    }
    
    return render(request, 'messaging/invite_to_group.html', context)

@login_required
def accept_group_invitation(request, invitation_id):
    """Accept group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id, invitee=request.user)
    
    if invitation.status == 'pending':
        invitation.status = 'accepted'
        invitation.save()
        
        # Add user to group
        invitation.group.members.add(request.user)
        
        messages.success(request, f'You joined "{invitation.group.name}"')
        return redirect('group_chat', group_id=invitation.group.id)
    
    return redirect('group_messaging_home')

@login_required
def decline_group_invitation(request, invitation_id):
    """Decline group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id, invitee=request.user)
    
    if invitation.status == 'pending':
        invitation.status = 'declined'
        invitation.save()
        
        messages.info(request, f'You declined the invitation to "{invitation.group.name}"')
    
    return redirect('group_messaging_home')