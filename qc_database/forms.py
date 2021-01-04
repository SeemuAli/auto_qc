from django import forms
from .models import  *
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML
from django.forms import ModelForm
import datetime

class RunAnalysisSignOffForm(forms.Form):
	"""
	Form for signing off a run analysis
	"""
	approval = forms.ChoiceField(choices =(('Pass', 'Pass'), ('Fail', 'Fail')))
	comment = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))

	def __init__(self, *args, **kwargs):
		
		self.run_analysis_id = kwargs.pop('run_analysis_id')
		self.comment = kwargs.pop('comment')
		super(RunAnalysisSignOffForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'run-analysis-signoff-form'
		self.helper.label_class = 'col-lg-2'
		self.fields['comment'].initial = self.comment
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('run-analysis-signoff-form', 'Finalise', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('approval', title=False),
			Field('comment', placeholder='Write a comment if you want.', title=False),
		)


class ResetRunForm(forms.Form):
	"""
	Form for resetting a run analysis
	"""

	def __init__(self, *args, **kwargs):
		
		self.run_analysis_id = kwargs.pop('run_analysis_id')

		super(ResetRunForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'reset-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('reset-form', 'Move To Pending', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
		)


class SensitivityForm(ModelForm):

	class Meta:
		model = RunAnalysis
		fields = ['sensitivity', 'sensitivity_lower_ci', 'sensitivity_higher_ci']


	def __init__(self, *args, **kwargs):
		
		super(SensitivityForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'reset-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('sensitivity-form', 'Submit Sensitivity', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(

		)


class KpiDateForm(forms.Form):
	"""
	Form to input two dates, used to pull KPI data for NGS runs between the dates
	"""
	current_year = datetime.datetime.now().year
	current_month = datetime.datetime.now().month

	# choices for year dropdown box
	YEAR_CHOICES = range(2019, (current_year + 1))

	# default to first and last day of previous month
	INITIAL_START_DATE = datetime.date(current_year, current_month, 1)
	INITIAL_END_DATE = datetime.date(current_year, current_month, 1) - datetime.timedelta(days=1)

	start_date = forms.DateField(
		initial=INITIAL_START_DATE,
		widget=forms.SelectDateWidget(years=YEAR_CHOICES)
	)
	end_date = forms.DateField(
		initial=INITIAL_END_DATE,
		widget=forms.SelectDateWidget(years=YEAR_CHOICES)
	)
