from django import forms

from django.forms import ModelForm
from . models import ContentCreationJob
from tinymce.widgets import TinyMCE

class ContentCreationJobForm(ModelForm):
    class Meta:
        model = ContentCreationJob
        fields = ('job_type', 'job_description', 'monthly_pay', 'number_of_creators', )
        widgets = {
            "job_type": forms.Select(attrs={'class': "form-control mb-3", 'id': 'job_type', 'placeholder': 'select job type'}),
            "job_description": TinyMCE(attrs={'class': "form-control mb-3", 'cols': 80, 'rows': 30}),
            "monthly_pay": forms.NumberInput(attrs={'class': "form-control mb-3", 'id': 'monthly_pay', 'placeholder': 'whats your monthly pay for the job'}),
            "number_of_creators": forms.NumberInput(attrs={'class': "form-control mb-3", 'id': 'number_of_creators', 'placeholder': 'How many creators are targeting for this job'}),
        }
