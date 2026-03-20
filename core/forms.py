from django import forms
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Institution, ContactPerson, SiteAssessment, MonthlyBilling, BANDWIDTH_CHOICES

def new_receipt():
    return f"RCP-{uuid.uuid4().hex[:8].upper()}"

class InstitutionForm(forms.ModelForm):
    class Meta:
        model  = Institution
        fields = ['name','institution_type','county','sub_county','address','phone','email','notes']
        widgets= {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['name','county','sub_county','phone']}
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        for f in self.fields.values():
            if not hasattr(f.widget,'attrs') or 'class' not in f.widget.attrs:
                f.widget.attrs['class']='form-control'
        self.fields['institution_type'].widget.attrs['class']='form-select'
        self.fields['address'].widget = forms.Textarea(attrs={'class':'form-control','rows':3})
        self.fields['notes'].widget   = forms.Textarea(attrs={'class':'form-control','rows':2})

class ContactPersonForm(forms.ModelForm):
    class Meta:
        model  = ContactPerson
        fields = ['title','first_name','last_name','designation','national_id','phone','email','alt_phone']
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        for f in self.fields.values():
            f.widget.attrs['class']='form-control'

class SiteAssessmentForm(forms.ModelForm):
    class Meta:
        model  = SiteAssessment
        fields = ['assessment_date','assessed_by','number_of_users','has_computers','number_of_computers',
                  'has_lan','number_of_lan_nodes','is_ready','pcs_to_purchase','lan_nodes_to_purchase','remarks']
        widgets= {
            'assessment_date':       forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'assessed_by':           forms.TextInput(attrs={'class':'form-control'}),
            'number_of_users':       forms.NumberInput(attrs={'class':'form-control','min':'1'}),
            'has_computers':         forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'number_of_computers':   forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'has_lan':               forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'number_of_lan_nodes':   forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'is_ready':              forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'pcs_to_purchase':       forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'lan_nodes_to_purchase': forms.NumberInput(attrs={'class':'form-control','min':'0','max':'100'}),
            'remarks':               forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class BandwidthSubscriptionForm(forms.Form):
    bandwidth  = forms.ChoiceField(choices=BANDWIDTH_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    start_date = forms.DateField(initial=timezone.now, widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))

    def __init__(self,*a,current_bandwidth=None,**kw):
        super().__init__(*a,**kw)
        self.current_bandwidth = current_bandwidth

    def clean_bandwidth(self):
        bw = int(self.cleaned_data['bandwidth'])
        if self.current_bandwidth and bw <= self.current_bandwidth:
            raise forms.ValidationError("Select a higher bandwidth to upgrade. Contact Azani to downgrade.")
        return bw

class GenerateBillsForm(forms.Form):
    billing_month = forms.DateField(
        label='Billing Month (pick any day in that month)',
        widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))

class SearchForm(forms.Form):
    q    = forms.CharField(required=False,
             widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Search institutions…'}))
    institution_type = forms.ChoiceField(required=False,
             choices=[('','All Types'),('PRIMARY','Primary'),('JUNIOR','Junior'),('SENIOR','Senior'),('COLLEGE','College')],
             widget=forms.Select(attrs={'class':'form-select'}))
    status = forms.ChoiceField(required=False,
             choices=[('','All Statuses'),('PENDING','Pending'),('ASSESSED','Assessed'),('READY','Ready'),
                      ('NEEDS_INFRA','Needs Infra'),('INSTALLED','Installed'),('SUSPENDED','Suspended'),('DISCONNECTED','Disconnected')],
             widget=forms.Select(attrs={'class':'form-select'}))
