from django import forms
from django_roa_client.models import RemotePage, RemotePageWithRelations

class TestForm(forms.Form):
    test_field = forms.CharField()
    remote_page = forms.ModelChoiceField(queryset=RemotePage.objects.all())


class RemotePageForm(forms.ModelForm):
    class Meta:
        model = RemotePage


class RemotePageWithRelationsForm(forms.ModelForm):
    class Meta:
        model = RemotePageWithRelations
