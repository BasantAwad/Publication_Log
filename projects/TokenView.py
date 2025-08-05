from django.shortcuts import render, redirect, get_object_or_404
from .models import UploadToken
from .forms import UploadPublicationForm, fetch_and_save_file_from_url
from .models import Publication

def upload_publication_token_view(request, token):
    token_obj = get_object_or_404(UploadToken, token=token)

    if token_obj.is_used:
        return render(request, 'upload/expired.html')

    if request.method == 'POST':
        form = UploadPublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.project = None  # or link it to a default project if needed
            publication.save()
            form.save_m2m()

            # ✅ Auto-download file if URL is present and file is not uploaded
            if form.cleaned_data.get("url") and not form.cleaned_data.get("file"):
                fetch_and_save_file_from_url(publication, form.cleaned_data['url'])

            token_obj.is_used = True
            token_obj.save()

            return render(request, 'upload/success.html')

    else:
        form = UploadPublicationForm()

    return render(request, 'upload/upload_form.html', {'form': form, 'user': token_obj.user})
