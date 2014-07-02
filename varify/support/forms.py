from django import forms


class SupportForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SupportForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Required'}),
        required=False)
    subject = forms.CharField(
        initial='New Support Message',
        widget=forms.TextInput(attrs={'placeholder': 'Required'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Required'}))

    def clean_email(self):
        email = self.cleaned_data['email']

        # is user is authenticated, use their account email address
        if self.user.is_authenticated():
            return self.user.email

        # require is for non-authenticated users
        if not email:
            raise forms.ValidationError, 'This field is required.'

        return email
