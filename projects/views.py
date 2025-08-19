from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages
from .models import Project, Publication
from .forms import PublicationForm
from .forms import UserCreation
from django.contrib.admin.views.decorators import staff_member_required
from projects.models import MatchRequest
from django.views.decorators.http import require_POST
from .email import notify_invalid_publication_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .email import send_welcome_email
from django.contrib.auth import logout
from django.db.models.functions import ExtractYear

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
    publications = Publication.objects.filter(author=user)
    collaborated_projects = Project.objects.filter(team=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your name has been updated.")
            return redirect('user_dashboard')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'registration/user_dashboard.html', {
        'user': user,
        'form': form,
        'publications': publications,
        'collaborated_projects': collaborated_projects
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