from django import forms
from django_roa_client.models import RemotePageWithRelations

class RemotePageWithRelationsForm(forms.ModelForm):
    class Meta:
        model = RemotePageWithRelations
