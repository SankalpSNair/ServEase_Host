from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=20,blank=False)
    lastname = models.CharField(max_length=20,blank=False)
    email = models.EmailField(unique=True,blank=False)
    phone = models.CharField(max_length=10,null=True)
    address = models.TextField()
    place=models.CharField(max_length=30, blank=True)
    availability = models.IntegerField(default=0)
    district = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='profile_pic', null=True, blank=True)
    password = models.CharField(max_length=256)
    usertype = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    

class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=50)
    skill_description = models.TextField()

class House_Maid(models.Model):
    maid_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    experience = models.IntegerField()
    availability = models.IntegerField(default=0)
    firstname = models.CharField(max_length=20, blank=False)
    lastname = models.CharField(max_length=20, blank=False)
    email = models.EmailField(unique=True, blank=False)
    place=models.CharField(max_length=30, blank=True)
    district = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=10, null=True)
    profilepic = models.ImageField(upload_to='maid_pic', null=True, blank=True)
    address = models.TextField()

class Home_Nurse(models.Model):
    nurse_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    experience = models.IntegerField()
    availability = models.IntegerField(default=0)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    place=models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    district = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15)
    profilepic = models.ImageField(upload_to='nurse_pic', null=True, blank=True)
    address = models.TextField()

class Carpenter(models.Model):
    carpenter_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    experience = models.IntegerField()
    availability = models.IntegerField(default=0)
    district = models.CharField(max_length=20, blank=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    place=models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    profilepic = models.ImageField(upload_to='carpenter_pic', null=True, blank=True)
    address = models.TextField()

class Electrician(models.Model):
    electrician_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    experience = models.IntegerField()
    availability = models.IntegerField(default=0)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    district = models.CharField(max_length=20, blank=True)
    place=models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    profilepic = models.ImageField(upload_to='electrician_pics', null=True, blank=True)
    address = models.TextField()

class Plumber(models.Model):
    plumber_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    experience = models.IntegerField()
    availability = models.IntegerField(default=0)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    place=models.CharField(max_length=30, blank=True)
    district = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    profilepic = models.ImageField(upload_to='plumber_pics', null=True, blank=True)
    address = models.TextField()


class Booking(models.Model):
    # Foreign key to the Users table for the worker
    worker_id = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='bookings')
    
    # Field to identify the type of worker
    worker_type = models.CharField(max_length=50, choices=[
        ('House Maid', 'House Maid'),
        ('Carpenter', 'Carpenter'),
        ('Plumber', 'Plumber'),
        ('Electrician', 'Electrician'),
        ('Home Nurse', 'Home Nurse'),
    ])
    
    # Foreign key to the Users table for the customer
    customer_id = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='customer_bookings')
    
    # Date and time of the appointment
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    # Address where the service will be provided
    address = models.TextField()
    
    # Status of the booking
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    
    # Fields for service type and description
    service_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    # Additional fields from the first definition
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hours_booked = models.PositiveIntegerField(default=1)

    def calculate_pay_amount(self):
        hourly_rate = ServiceRate.get_rate(self.service_type)
        self.pay_amount = self.hours_booked * hourly_rate
        self.save()

    class Meta:
        app_label = 'Home_app'

class ServiceRate(models.Model):
    SERVICE_TYPES = [
        ('house_maid', 'House Maid'),
        ('nurse', 'Home Nurse'),
        ('plumber', 'Plumber'),
        ('carpenter', 'Carpenter'),
        ('electrician', 'Electrician'),
    ]

    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, unique=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)

    @classmethod
    def get_rate(cls, service_type):
        try:
            return cls.objects.get(service_type=service_type).hourly_rate
        except cls.DoesNotExist:
            return Decimal('200.00')  # Default rate

    def __str__(self):
        return f"{self.get_service_type_display()} - ${self.hourly_rate}/hour"

from django.db.models import Q

class ChatMessage(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        limit_choices_to=Q(usertype='admin'),
        null=True,  # Allow null temporarily
        default=None  # Set default to None
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.firstname}: {self.message[:50]}"

class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    razorpay_id = models.CharField(max_length=100,blank=True,null=True)

    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class WorkerVerification(models.Model):
    worker = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='verification')
    verification_image = models.ImageField(upload_to='verification_images/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.worker.firstname} {self.worker.lastname} - {self.verification_status}"

    @property
    def worker_id(self):
        return self.worker.user_id

class WorkerRating(models.Model):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='ratings_given')
    worker = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='ratings_received')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'worker')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.firstname} rated {self.worker.firstname}: {self.rating}"


