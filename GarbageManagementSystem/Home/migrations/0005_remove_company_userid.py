# Generated by Django 4.1.1 on 2023-03-11 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0004_company_cemail_company_cpassword'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='userid',
        ),
    ]