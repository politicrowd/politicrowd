from django import forms
from registration.forms import RegistrationForm
from accounts.models import UserProfile
from registration.models import RegistrationProfile

attrs_dict = { 'class': 'required' }

class RegistrationFormZ(RegistrationForm):
	zip_code = forms.IntegerField(widget=forms.TextInput(attrs=attrs_dict))
	
	def save(self, profile_callback=None):
		new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'], password=self.cleaned_data['password1'], email=self.cleaned_data['email'])	
		new_profile = UserProfile(user=new_user, zip_code=self.cleaned_data['zip_code'])
		new_profile.save()
		return new_user