# Generated by Django 4.1.1 on 2023-04-02 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0015_driver_job_application_review_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='service_booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(default='', max_length=150)),
                ('time', models.CharField(default='4:00pm', max_length=30)),
                ('date', models.CharField(default='', max_length=50)),
                ('status', models.BooleanField(default='1')),
                ('companyid', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='Home.company')),
                ('userid', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='Home.customer')),
            ],
        ),
    ]