from django import forms
from conference.models import Attendee
from django.forms import ModelForm

#https://gist.github.com/651080
class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))
        super(EmptyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label,
                                        initial=initial, help_text=help_text, *args, **kwargs)

class AttendeeForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    
    email = forms.EmailField()
    confirm_email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    sex = EmptyChoiceField(choices=Attendee.GENDER, required=False, empty_label='------')
    
    school = forms.CharField(max_length=100)
    size_of_institute = EmptyChoiceField(choices=Attendee.SIZE, required=False, empty_label='------')
    max_degree = forms.CharField(widget=forms.Select(choices=Attendee.DEG), max_length=10)
    attendee_type = forms.CharField(widget=forms.Select(choices=Attendee.STATUS), max_length=7)
    year = EmptyChoiceField(choices=Attendee.YEAR, required=False, empty_label='------')
    
    is_submitting_talk = forms.BooleanField(required=False)
    paper_title = forms.CharField(max_length=100, required=False)
    paper_abstract = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'100',
'rows':'20'}))
    is_submitted_for_best_of_competition = forms.BooleanField(required=False)
    
    dietary_restrictions = forms.CharField(required=False, widget=forms.Textarea)
    requires_housing = forms.BooleanField(required=False)
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
    def clean(self):
        if self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email'):
            msg = u'Email addresses must match!'
            self._errors['email'] = self.error_class([msg])
            self._errors['confirm_email'] = self.error_class([msg])
            del self.cleaned_data['email']
            #del self.cleaned_data['confirm_email']
        if self.cleaned_data.get('is_submitting_talk'):
            if self.cleaned_data.get('paper_title') == '':
                self._errors['paper_title'] = self.error_class([u"You must provide your paper's title if you are submitting a talk."])
            if self.cleaned_data.get('paper_abstract') == '':
                self._errors['paper_abstract'] = self.error_class([u"You must provide your paper's abstract if you are submitting a talk."])
        return self.cleaned_data