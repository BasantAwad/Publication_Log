from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages
from .models import Project, Publication
from .forms import PublicationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from projects.models import MatchRequest
from django.views.decorators.http import require_POST
from .email import notify_invalid_publication_url


def project_list(request):
    projects = Project.objects.all()

    search_query = request.GET.get('search', '').lower()
    domain = request.GET.get('domain', '')
    year = request.GET.get('year', '')
    sort = request.GET.get('sort', '')

    if search_query:
        projects = projects.filter(title__icontains=search_query)

    if domain:
        projects = projects.filter(domain=domain)

    if year:
        projects = projects.filter(created__year=year)

    if sort == 'newest':
        projects = projects.order_by('-created')
    elif sort == 'oldest':
        projects = projects.order_by('created')

    context = {
        'projects': projects,
        'search_query': search_query,
        'selected_domain': domain,
        'selected_year': year,
        'selected_sort': sort,
    }
    return render(request, 'projects_page.html', context)



def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    publications = project.publications.prefetch_related('collaborators')
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'publications': publications
    })

@login_required
def add_publication(request, token):
    project = get_object_or_404(Project, id=token)

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, project=project)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.project = project
            publication.save()
            form.save_m2m()

            # ✅ Check for URL validity and trigger email if needed
            if publication.url:
                notify_invalid_publication_url(publication)

            return redirect('project_detail', pk=project.id)
    else:
        form = PublicationForm(project=project)

    return render(request, 'publications/add_publication.html', {'form': form, 'project': project})


def publication_list(request):
    publications = Publication.objects.all()
    return render(request, 'publications/publication_list.html', {
        'publications': publications
    })
def publication_detail(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    return render(request, 'publications/publication_detail.html', {
        'publication': publication
    })

@login_required
def user_dashboard(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your name has been updated.")
            return redirect('user_dashboard')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'projects/dashboard.html', {
        'user': user,
        'form': form
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('project_list')  # or any landing page
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@staff_member_required
def admin_dashboard(request):
    pending_requests = MatchRequest.objects.filter(reviewed=False).order_by("-created_at")
    return render(request, "admin_dashboard.html", {"match_requests": pending_requests})

@require_POST
@staff_member_required
def accept_match_request(request, pk):
    match = get_object_or_404(MatchRequest, pk=pk)
    decision = request.POST.get("decision")
    match.reviewed = True
    match.accepted = decision == "yes"
    match.save()
    return redirect("admin_dashboard")
