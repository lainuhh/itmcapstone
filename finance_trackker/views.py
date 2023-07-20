from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, User, Expense, ExpensePayment, UserProfile
from .forms import EventForm, ExpenseForm, ExpenseFormSet
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Q, Sum


# Create your views here.


@login_required
def kadashboard_index(request):
    user = request.user
    events = Event.objects.all()

    context = {
        'event_list': events,
    }

    return render(request, "finance_trackker/kadashboard_index.html", context)


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['login_password']

        # Authenticate the user
        user = authenticate(username=email, password=password)

        if user is not None:
            print("Authenticated User:", user.username)
            login(request, user)
            return redirect('index')
        else:
            # Display an error message using the messages framework
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html')  # Render the login page with the login form


def register_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        first_name = request.POST['reg_first_name']
        last_name = request.POST['reg_last_name']
        password = request.POST['register_password']
        username = request.POST['reg_last_name']

        # Check if the user with the provided email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'login.html', {'error': 'User with this email already exists.'})

        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password)
        user_profile = UserProfile(user=user)
        user_profile.save()
        return redirect('personal_dashboard_index')
    else:
        return render(request, 'login.html')  # Render the login page with the registration form


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()

            # Process the members input and add users to the event
            members_input = request.POST.get('members')
            members_list = [member.strip() for member in members_input.split(',') if
                            member.strip()] if members_input else []

            for member in members_list:
                # Check if the member is an existing user by searching for their email
                user = User.objects.filter(email=member).first()
                if not user:
                    # If the member is not an existing user, create a new user with the provided first name
                    user = User.objects.create_user(username=member.split()[0], email=member)

                event.members.add(user)

            return redirect('event_detail', event_slug=event.slug)
    else:
        form = EventForm()

    return render(request, 'finance_trackker/create_event.html', {'form': form})


@login_required
def event_detail(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    expense_list = Expense.objects.filter(event=event)
    members = event.members.all()
    event_members = {}

    for member in members:
        total_amount_spent = ExpensePayment.objects.filter(user=member, expense__event=event).aggregate(Sum('portion'))
        event_members[member.username] = total_amount_spent['portion__sum']

    if request.method == 'POST':
        expense_formset = ExpenseFormSet(request.POST, queryset=expense_list)
        if expense_formset.is_valid():
            expense_formset.save()
            messages.success(request, 'Expense-related edits were saved successfully.')
            return redirect('event_detail', event_slug=event.slug)
    else:
        expense_formset = ExpenseFormSet(queryset=expense_list)

    context = {
        'event': event,
        'expense_list': expense_list,
        'expense_formset': expense_formset,
        'event_members': event_members,
    }

    return render(request, 'personal_dashboard/event_detail.html', context)


def create_expense(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)

    if request.method == 'POST':
        form = ExpenseForm(event=event, data=request.POST)
        if form.is_valid():
            expense = form.save()
            expense.event = event
            expense.save()

            users_and_portions = request.POST.get('users_and_portions')
            user_portion_list = users_and_portions.split(',')

            messages.success(request, 'Expense created successfully!')
            return redirect('event_detail', event_slug=event_slug)
    else:
        form = ExpenseForm(event=event)

    return render(request, 'finance_trackker/create_expense.html', {'form': form, 'event': event,
                                                                    'event_slug': event_slug})


def edit_expense(request, event_slug, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, event__slug=event_slug)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Expense updated successfully.')
            return redirect('event_detail', event_slug=event_slug)
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'finance_trackker/edit_expense.html', {'form': form, 'event_slug': event_slug, 'expense_id': expense_id})


def save_and_redirect_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            event_slug = form.cleaned_data['event_slug']
            return redirect('event_detail', event_slug=event_slug)
    else:
        form = ExpenseForm()

    return render(request, 'finance_trackker/create_expense.html', {'form': form})


def personal_dashboard_index(request):
    user = request.user
    recent_expenses = ExpensePayment.objects.filter(user=user)
    context = {"recent_expenses": recent_expenses}
    return render(request, "finance_trackker/personal_dashboard_index.html", context)


@login_required
def account(request):
    user_form = UserChangeForm(instance=request.user)

    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            # Optionally add a success message
            # messages.success(request, 'Account details updated successfully.')
            return redirect('account')

    return render(request, 'account.html', {'user_form': user_form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)  # Optionally log the user out after deleting their account
        # Optionally add a success message
        # messages.success(request, 'Account deleted successfully.')
        return redirect('home')  # Redirect to the home page after account deletion
    return render(request, 'account_delete.html')


@login_required
def update_account(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Optionally add a success message
            # messages.success(request, 'Account updated successfully.')
            return redirect('account')  # Replace 'account_page' with the URL name of your account page
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'update_account.html', {'form': form})