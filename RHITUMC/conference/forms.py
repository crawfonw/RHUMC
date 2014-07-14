"""
    Conference scheduling software for undergraduate institutions.
    Created specifically for the Mathematics department of the
    Rose-Hulman Institute of Technology (http://www.rose-hulman.edu/math.aspx).
    
    Copyright (C) 2013-2014  Nick Crawford <crawfonw -at- gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from django import forms
from conference.models import Attendee, Conference, Contactee
from django.forms.forms import NON_FIELD_ERRORS

from django.utils.safestring import mark_safe

from utils import which

#https://gist.github.com/651080
class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):
        #if not required and empty_label is not None:
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))
        super(EmptyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label,
                                        initial=initial, help_text=help_text, *args, **kwargs)

#http://stackoverflow.com/a/5936347
class NoListRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n<br />' % w for w in self]))

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
    requires_housing = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'Yes'), (False, 'No')), renderer=NoListRadioRenderer), initial=False)
    #requires_housing = forms.TypedChoiceField(widget=forms.RadioSelect(renderer=NoListRadioRenderer), choices=((True, 'Yes'), (False, 'No')), required=True, initial=None, empty_value=None) #'No' gets coerced into True, not sure why
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
    def clean(self):
        if self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email'):
            msg = u'Email addresses must match!'
            self._errors['email'] = self.error_class([msg])
            self._errors['confirm_email'] = self.error_class([msg])
            del self.cleaned_data['email']
            #del self.cleaned_data['confirm_email']
        if self.cleaned_data.get('is_submitting_talk') or self.cleaned_data.get('paper_title') != '' or self.cleaned_data.get('paper_abstract') != '':
            if not self.cleaned_data.get('is_submitting_talk'):
                self._errors['is_submitting_talk'] = self.error_class([u"Make sure to check this if you are submitting a talk!"])
            if self.cleaned_data.get('paper_title') == '':
                self._errors['paper_title'] = self.error_class([u"You must provide your paper's title if you are submitting a talk."])
            if self.cleaned_data.get('paper_abstract') == '':
                self._errors['paper_abstract'] = self.error_class([u"You must provide your paper's abstract if you are submitting a talk."])
        if self.cleaned_data.get('requires_housing') is None:
            self._errors['requires_housing'] = self.error_class([u"Please indicate whether or not you require housing."])
        if not self.is_valid():
            gen_error = u"There was a problem submitting your form. Please correct the errors indicated below."
            self._errors[NON_FIELD_ERRORS] = self.error_class([gen_error])
        return self.cleaned_data
    
class AttendeeEmailerForm(forms.Form):
    conference = forms.ModelChoiceField(queryset = Conference.objects.all())
    host = forms.ModelChoiceField(queryset = Contactee.objects.filter(active_contact=True))
    email_subject = forms.CharField(max_length=100)
    email_body = forms.CharField(widget=forms.Textarea)

class CSVDumpForm(forms.Form):
    conference = forms.ModelChoiceField(queryset = Conference.objects.all())
    csv_fields = forms.CharField(widget=forms.Textarea)

class LaTeXProgramForm(forms.Form):
    action = None
    if which('pdflatex') is not None:
        action = forms.ChoiceField(choices=(('tex', 'LaTeX'), ('pdf', 'PDF'), ('all', 'Both PDF & LaTeX')), required=True)
    conference = forms.ModelChoiceField(queryset = Conference.objects.all())
    file_name = forms.CharField(initial='program', required=True)
    squish = forms.IntegerField(initial=3, required=True)
    display_titles = forms.BooleanField(required=False, initial=True)
    display_schools = forms.BooleanField(required=False)
    convert_unicode = forms.BooleanField(widget=forms.CheckboxInput(), initial=True, required=False)
    escape_latex = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=False)

class LaTeXBadgesForm(forms.Form):
    conference = forms.ModelChoiceField(queryset = Conference.objects.all())
    width = forms.IntegerField(initial=55, required=True)
    height = forms.IntegerField(initial=90, required=True)
    
class BatchUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BatchUpdateForm, self).__init__(*args, **kwargs)
        
        schools = []
        school_tuples = []
        for s in Attendee.objects.all().order_by('school').values('school'):
            if s['school'] not in schools:
                schools.append(s['school'])
                school_tuples.append((s['school'], s['school']))
        
        self.fields['selection'] = forms.ChoiceField(
            choices=school_tuples, label='School String to Replace')
        self.fields['replace'] = forms.CharField(max_length=100, label='New String')
    #selection = forms.ChoiceField(choices = school_tuples, label='School String to Replace')
    #replace = forms.CharField(max_length=100, label='New String')
    
    