from django import forms
from django.forms import modelformset_factory
from .models import Event, Expense, Category, User
from django.shortcuts import redirect, reverse
from django.core.validators import validate_email
from django_select2.forms import Select2MultipleWidget, Select2Widget


class EventForm(forms.ModelForm):
    new_member_first_name = forms.CharField(label='New Member First Name', required=False)
    new_member_email = forms.EmailField(required=False, label='New Member Email')
    members_emails = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter email addresses separated by commas'}),
        label='Existing Member Emails'
    )

    class Meta:
        model = Event
        fields = ['name', 'description', 'members']
        widgets = {
            'members': forms.SelectMultiple(attrs={'class': 'select2'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Event Name'

    # Override the save method to handle the members selection and new member creation
    def save(self, commit=True):
        event = super().save(commit=commit)

        if commit:
            event.save()

        members_input = self.cleaned_data.get('members_emails')
        members_list = [email.strip() for email in members_input.split(',') if email.strip()] if members_input else []

        for email in members_list:
            try:
                validate_email(email)
            except forms.ValidationError:
                continue

            # Check if the member is an existing user by searching for their email
            user = User.objects.filter(email=email).first()
            if not user:
                # If the member is not an existing user, create a new user with the provided email
                first_name = self.cleaned_data.get('new_member_first_name')
                user = User.objects.create_user(username=email, email=email, first_name=first_name)

            event.members.add(user)

        return event

    members = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                           widget=forms.SelectMultiple(attrs={'class': 'select2'}))


class ExpenseForm(forms.ModelForm):
    new_category = forms.CharField(required=False)

    class Meta:
        model = Expense
        fields = ['name', 'amount', 'users', 'category']
        widgets = {
            'users': forms.SelectMultiple(attrs={'class': 'select2'}),
            'category': forms.Select(attrs={'class': 'select2'}),
        }
        labels = {
            'name': 'Expense Name:',
            'category': 'Select an existing category:',
            'amount': 'Expense Amount:',
            'users': 'People responsible for paying for the expense:',
            'portion_type': 'Portion Type:',
        }

    portion_type = forms.ChoiceField(
        choices=[('amount', 'Amount'), ('percentage', 'Percentage')],
        initial='amount',
        widget=forms.RadioSelect(attrs={'class': 'portion-toggle'})
    )

    def __init__(self, event=None, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.event = self.event
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            new_category, _ = Category.objects.get_or_create(name=new_category_name)
            instance.category = new_category
        if commit:
            instance.save()

            return instance

    def save_and_redirect(self):
        instance = self.save(commit=True)
        return reverse('event_detail', args=[instance.event.slug])

    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                           widget=forms.SelectMultiple(attrs={'class': 'select2'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'class': 'select2'}))


ExpenseFormSet = modelformset_factory(Expense, form=ExpenseForm, extra=1)
