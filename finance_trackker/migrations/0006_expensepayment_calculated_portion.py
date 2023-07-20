# Generated by Django 4.2.2 on 2023-07-19 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_trackker', '0005_remove_expense_new_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensepayment',
            name='calculated_portion',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='The calculated amount each user has to pay.', max_digits=6, null=True),
        ),
    ]