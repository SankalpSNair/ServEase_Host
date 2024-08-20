# Generated by Django 5.0.6 on 2024-08-20 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home_app', '0016_booking_description_booking_service_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]