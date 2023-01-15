from .models import Subscription
from django import forms


class SubscriptionForm(forms.ModelForm):
    # level_you_teach = forms.MultipleChoiceField(widget=forms.SelectMultiple,choices=Student_level)
    class Meta:
        model = Subscription
        fields = ("user", "plan","price",)
   