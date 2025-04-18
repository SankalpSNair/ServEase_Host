# Generated by Django 5.0.6 on 2024-08-05 18:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home_app', '0008_carpenter_district_electrician_district_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worker_type', models.CharField(choices=[('House Maid', 'House Maid'), ('Carpenter', 'Carpenter'), ('Plumber', 'Plumber'), ('Electrician', 'Electrician'), ('Home Nurse', 'Home Nurse')], max_length=50)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('address', models.TextField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_bookings', to=settings.AUTH_USER_MODEL)),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
