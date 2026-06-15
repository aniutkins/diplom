from django import forms
from .models import Item
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'image']
        
class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['phone', 'location', 'avatar']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['username'].initial = user.username
        self.fields['email'].initial = user.email
        
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("Це ім'я вже зайняте")
        return username

    def save(self, user):
      
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()
    
        profile = user.userprofile
        profile.phone = self.cleaned_data['phone']
        profile.location = self.cleaned_data['location']
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']
        profile.save()
    
        return profile