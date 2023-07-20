from django.db import models
from django.contrib.auth.models import User, Permission
from django.utils.text import slugify
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, through='Membership')
    admins = models.ManyToManyField(User, related_name='event_admins', blank=True)
    slug = models.SlugField(unique=True, default=uuid.uuid4)  # Add a default value for the slug

    def save(self, *args, **kwargs):
        # Generate a unique slug for the event based on the name if the slug is empty
        if not self.slug:
            self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def total_expense_amount(self):
        return sum(expense.amount for expense in self.expense_set.all())


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_purchased = models.DateTimeField(auto_now_add=True)


    PORTION_CHOICES = [
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ]
    portion_type = models.CharField(
        max_length=10,
        choices=PORTION_CHOICES,
        default='amount',
    )

    def __str__(self):
        user_list = ", ".join(expense_payment.user.username for expense_payment in self.expensepayment_set.all())
        return f"{self.date_purchased} - {self.event} - {self.name} - {self.amount} - {self.category} - Users: {user_list}"

    def calculate_actual_portion(self, user, portion):
        if self.portion_type == ExpensePayment.PaymentType.AMOUNT:
            return portion
        elif self.portion_type == ExpensePayment.PaymentType.PERCENTAGE:
            return portion * self.amount / 100
        else:
            return 0  # Handle invalid or missing portion type gracefully


class ExpensePayment(models.Model):
    class PaymentType(models.TextChoices):
        AMOUNT = 'amount', 'Amount'
        PERCENTAGE = 'percentage', 'Percentage'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    portion_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.AMOUNT,
    )
    portion = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Enter either an amount or a percentage.",
    )

    calculated_portion = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="The calculated amount each user has to pay.",
    )

    def __str__(self):
        return f"{self.user.username} - {self.expense.name} - {self.portion}"

    def calculate_actual_portion(self):
        if self.portion_type == self.PaymentType.AMOUNT:
            return self.portion
        elif self.portion_type == self.PaymentType.PERCENTAGE:
            return self.portion * self.expense.amount / 100
        else:
            return 0  # Handle invalid or missing portion type gracefully


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def generate_slug(self):
        if not self.slug:
            self.slug = slugify(self.user.username)

    def save(self, *args, **kwargs):
        self.generate_slug()
        super(UserProfile, self).save(*args, **kwargs)
