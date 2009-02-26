from django.http import HttpResponse

from django_roa_client.forms import RemotePageWithRelationsForm

def home(request):
    form = RemotePageWithRelationsForm()
    return HttpResponse(form.as_ul())
