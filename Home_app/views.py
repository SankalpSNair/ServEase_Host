from django.conf import settings
from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logouts
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .forms import CustomPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from .models import Users,House_Maid,Skill,Carpenter,Electrician,Plumber,Home_Nurse,Booking,ServiceRate,ChatMessage,Payments

from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Plumber, Users, Skill
from django.core.files.storage import default_storage
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from .import models



# -------------------------  ADMIN SIDE ----------------------------- #

from django.http import JsonResponse
from django.db.models import Count,Avg
from django.db.models.functions import ExtractMonth
from .models import Booking  # Import your Booking model
from django.views.decorators.http import require_GET

@require_GET
def monthly_bookings(request, year):
    bookings = Booking.objects.filter(appointment_date__year=year)
    monthly_data = bookings.annotate(month=ExtractMonth('appointment_date')) \
                           .values('month') \
                           .annotate(count=Count('id')) \
                           .order_by('month')
    
    # Initialize a list with zeros for all 12 months
    data = [0] * 12
    
    # Fill in the actual booking counts
    for item in monthly_data:
        data[item['month'] - 1] = item['count']
    
    return JsonResponse(data, safe=False)

def district_bookings(request):
    district_data = (
        Booking.objects.select_related('customer_id')
        .values('customer_id__district')
        .annotate(count=Count('id'))
        .filter(customer_id__district__isnull=False)
        .order_by('-count')
    )
    
    labels = [item['customer_id__district'] for item in district_data]
    values = [item['count'] for item in district_data]
    
    return JsonResponse({'labels': labels, 'values': values})


from django.db.models import Count, Max
from django.db.models.functions import TruncMonth
from django.utils import timezone

def DashboardPage(request):
    total_users = Users.objects.count()  # Total number of users
    total_customers = Users.objects.filter(usertype='customer').count()  # Total number of customers
    total_workers = Users.objects.exclude(usertype='customer').count()  # Total number of workers
    total_bookings = Booking.objects.count()  # Total number of bookings
    
    # Get the most recent message from each unique sender
    recent_messages = ChatMessage.objects.exclude(sender_id=22).values('sender').annotate(
        max_timestamp=Max('timestamp')
    ).order_by('-max_timestamp')[:5]

    # Fetch the actual message objects
    recent_messages = [
        ChatMessage.objects.filter(sender=item['sender'], timestamp=item['max_timestamp']).first()
        for item in recent_messages
    ]

    # Get monthly bookings data for the current year
    current_year = timezone.now().year
    monthly_bookings = Booking.objects.filter(appointment_date__year=current_year) \
        .annotate(month=TruncMonth('appointment_date')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')
    
    # Create a list of 12 elements (one for each month) with booking counts
    booking_counts = [0] * 12
    for item in monthly_bookings:
        booking_counts[item['month'].month - 1] = item['count']

    # Fetch top-rated workers
    top_rated_workers = WorkerRating.objects.values('worker').annotate(
        average_rating=Avg('rating')
    ).order_by('-average_rating')[:5]  # Get top 5 rated workers

    # Fetch full worker objects for each top-rated worker
    top_rated_workers_full = []
    for worker in top_rated_workers:
        rating_obj = WorkerRating.objects.filter(worker_id=worker['worker']).first()
        if rating_obj and rating_obj.worker:
            top_rated_workers_full.append({
                'worker': rating_obj.worker,
                'average_rating': worker['average_rating']
            })

    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_workers': total_workers,
        'total_bookings': total_bookings,
        'recent_messages': recent_messages,
        'monthly_bookings': booking_counts,
        'top_rated_workers': top_rated_workers_full  # Add this line
    }
    
    return render(request, 'admin_temp/dashboard.html', context)

def Manage_Customers(request):
    customers = Users.objects.filter(usertype='customer')  
    return render(request, 'admin_temp/manage_customers.html',{'customers':customers})

def manage_house_maids(request):
    maids = House_Maid.objects.all()  # Fetch all house maids from the database
    return render(request, 'admin_temp/manage_house_maids.html', {'maids': maids})

def manage_home_nurses(request):
    nurses = Home_Nurse.objects.all()  # Fetch all home nurses from the database
    return render(request, 'admin_temp/manage_home_nurses.html', {'nurses': nurses})

def manage_plumbers(request):
    plumbers = Plumber.objects.all()  # Fetch all plumbers from the database
    return render(request, 'admin_temp/manage_plumbers.html', {'plumbers': plumbers})

def manage_electrician(request):
    electricians = Electrician.objects.all()  # Fetch all electricians from the database
    return render(request, 'admin_temp/manage_electricians.html', {'electricians': electricians})

def manage_carpenters(request):
    carpenters = Carpenter.objects.all()  # Fetch all carpenters from the database
    return render(request, 'admin_temp/manage_carpenters.html', {'carpenters': carpenters})

def edit_house_maid(request, maid_id):
    maid = get_object_or_404(House_Maid, pk=maid_id)
    user = get_object_or_404(Users, user_id=maid.user_id.user_id)

    if request.method == 'POST':
        # Retrieve data from the form
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', '')
        availability = request.POST.get('availability') == '1'  # Convert to boolean

        # Update House_Maid fields
        maid.firstname = firstname
        maid.lastname = lastname
        maid.phone = phone
        maid.experience = experience
        maid.availability = availability
        maid.save()

        # Update Users table fields
        user.firstname = firstname
        user.lastname = lastname
        user.phone = phone
        user.availability = availability
        user.save()

        return redirect('manage_house_maids')

    return render(request, 'admin_temp/edit_house_maid.html', {'maid': maid})

def edit_home_nurse(request, nurse_id):
    nurse = get_object_or_404(Home_Nurse, pk=nurse_id)
    user = get_object_or_404(Users, user_id=nurse.user_id.user_id)

    if request.method == 'POST':
        # Retrieve data from the form
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', '')
        availability = request.POST.get('availability') == '1'  # Convert to boolean

        # Update Home_Nurse fields
        nurse.firstname = firstname
        nurse.lastname = lastname
        nurse.phone = phone
        nurse.experience = experience
        nurse.availability = availability
        nurse.save()

        # Update Users table fields
        user.firstname = firstname
        user.lastname = lastname
        user.phone = phone
        user.availability = availability
        user.save()

        return redirect('manage_home_nurses')  # Redirect to the manage_home_nurses view

    return render(request, 'admin_temp/edit_home_nurses.html', {'nurse': nurse})

def edit_electrician(request, electrician_id):
    electrician = get_object_or_404(Electrician, pk=electrician_id)
    user = get_object_or_404(Users, user_id=electrician.user_id.user_id)

    if request.method == 'POST':
        # Retrieve data from the form
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', '')
        availability = request.POST.get('availability') == '1'  # Convert to boolean

        # Update Electrician fields
        electrician.firstname = firstname
        electrician.lastname = lastname
        electrician.phone = phone
        electrician.experience = experience
        electrician.availability = availability
        electrician.save()

        # Update Users table fields
        user.firstname = firstname
        user.lastname = lastname
        user.phone = phone
        user.availability = availability
        user.save()

        return redirect('manage_electricians')  # Redirect to the manage_electricians view

    return render(request, 'admin_temp/edit_electricians.html', {'electrician': electrician})

def edit_plumber(request, plumber_id):
    plumber = get_object_or_404(Plumber, pk=plumber_id)
    user = get_object_or_404(Users, user_id=plumber.user_id.user_id)

    if request.method == 'POST':
        # Retrieve data from the form
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', '')
        availability = request.POST.get('availability') == '1'  # Convert to boolean

        # Update Plumber fields
        plumber.firstname = firstname
        plumber.lastname = lastname
        plumber.phone = phone
        plumber.experience = experience
        plumber.availability = availability
        plumber.save()

        # Update Users table fields
        user.firstname = firstname
        user.lastname = lastname
        user.phone = phone
        user.availability=availability
        user.save()

        return redirect('manage_plumbers')  # Redirect to the manage_plumbers view

    return render(request, 'admin_temp/edit_plumbers.html', {'plumber': plumber})


def edit_carpenter(request, carpenter_id):
    carpenter = get_object_or_404(Carpenter, pk=carpenter_id)
    user = get_object_or_404(Users, user_id=carpenter.user_id.user_id)

    if request.method == 'POST':
        # Retrieve data from the form
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', '')
        availability = request.POST.get('availability') == '1'  # Convert to boolean

        # Update Carpenter fields
        carpenter.firstname = firstname
        carpenter.lastname = lastname
        carpenter.phone = phone
        carpenter.experience = experience
        carpenter.availability = availability
        carpenter.save()

        # Update Users table fields
        user.firstname = firstname
        user.lastname = lastname
        user.phone = phone
        user.availability = availability
        user.save()

        return redirect('manage_carpenters')  # Redirect to the manage_carpenters view

    return render(request, 'admin_temp/edit_carpenters.html', {'carpenter': carpenter})

def change_status(request, user_id):
    customer = get_object_or_404(Users, user_id=user_id, usertype='customer')
    # Toggle the availability status
    customer.availability = not customer.availability
    customer.save()
    return redirect('manage_customers')

def change_booking_status(request, booking_id):
    # Get the booking instance by id
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Define the status order you want to cycle through
    status_order = ['Pending','Paid', 'Confirmed', 'Completed', 'Cancelled']
    
    # Find the current status index and determine the next status
    current_index = status_order.index(booking.status)
    next_index = (current_index + 1) % len(status_order)
    
    # Update the booking status
    booking.status = status_order[next_index]
    booking.save()
    
    # Redirect back to the page displaying the bookings
    return redirect('new_bookings')  # Change 'new_bookings' to the correct view name

def add_plumber(request):
    if request.method == 'POST':
        print("Received POST request")

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        availability = request.POST.get('availability')
        place = request.POST.get('place')
        district = request.POST.get('district')
        address = request.POST.get('address')
        profilepic = request.FILES.get('profilepic')
        skill_id = request.POST.get('skill_id')

        print(f"Form data received: firstname={firstname}, lastname={lastname}, email={email}, phone={phone}, experience={experience}, availability={availability}, place={place}, district={district}, address={address}, skill_id={skill_id}, profilepic={profilepic}")

        # Basic validation
        if not (firstname and lastname and email and phone and experience and availability and skill_id):
            print("Validation failed: Missing required fields")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        if len(phone) != 10 or not phone.isdigit():
            print("Validation failed: Invalid phone number")
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        if not (1 <= int(experience) <= 35):
            print("Validation failed: Experience out of range")
            messages.error(request, 'Experience must be between 1 and 35 years.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        # Create a new user
        try:
            print("Creating new user")
            user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                district=district,
                place=place,
                address=address,
                password='defaultpassword',  # Use a default password or handle this securely
                usertype='plumber'  # Set appropriate usertype
            )
            print(f"User created with user_id={user.user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'An error occurred while creating the user.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        try:
            skill = Skill.objects.get(skill_id=skill_id)
            print(f"Skill fetched: {skill}")
        except Skill.DoesNotExist:
            print("Validation failed: Skill does not exist")
            messages.error(request, 'Invalid skill selected.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        # Save the new plumber with the created user's user_id as a foreign key
        try:
            print("Creating new plumber entry")
            Plumber.objects.create(
                user_id=user,
                skill_id=skill,
                experience=experience,
                availability=availability,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                place=place,
                district=district,
                address=address,
                profilepic=profilepic
            )
            print("Plumber created successfully")
        except Exception as e:
            print(f"Error creating plumber: {e}")
            messages.error(request, 'An error occurred while creating the plumber.')
            return render(request, 'admin_temp/add_plumber.html', {'skills': Skill.objects.all()})

        messages.success(request, 'Plumber added successfully!')
        return redirect('manage_plumbers')  # Redirect to a relevant page

    else:
        print("Received GET request")
        skills = Skill.objects.all()
        print(f"Skills fetched: {skills}")
        return render(request, 'admin_temp/add_plumber.html', {'skills': skills})

def add_electrician(request):
    if request.method == 'POST':
        print("Received POST request")

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        availability = request.POST.get('availability')
        place = request.POST.get('place')
        district = request.POST.get('district')
        address = request.POST.get('address')
        profilepic = request.FILES.get('profilepic')
        skill_id = request.POST.get('skill_id')

        print(f"Form data received: firstname={firstname}, lastname={lastname}, email={email}, phone={phone}, experience={experience}, availability={availability}, place={place}, district={district}, address={address}, skill_id={skill_id}, profilepic={profilepic}")

        # Basic validation
        if not (firstname and lastname and email and phone and experience and availability and skill_id):
            print("Validation failed: Missing required fields")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        if len(phone) != 10 or not phone.isdigit():
            print("Validation failed: Invalid phone number")
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        if not (1 <= int(experience) <= 35):
            print("Validation failed: Experience out of range")
            messages.error(request, 'Experience must be between 1 and 35 years.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        # Create a new user
        try:
            print("Creating new user")
            user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                district=district,
                place=place,
                address=address,
                password='defaultpassword',  # Use a default password or handle this securely
                usertype='electrician'  # Set appropriate usertype
            )
            print(f"User created with user_id={user.user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'An error occurred while creating the user.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        try:
            skill = Skill.objects.get(skill_id=skill_id)
            print(f"Skill fetched: {skill}")
        except Skill.DoesNotExist:
            print("Validation failed: Skill does not exist")
            messages.error(request, 'Invalid skill selected.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        # Save the new electrician with the created user's user_id as a foreign key
        try:
            print("Creating new electrician entry")
            Electrician.objects.create(
                user_id=user,
                skill_id=skill,
                experience=experience,
                availability=availability,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                place=place,
                district=district,
                address=address,
                profilepic=profilepic
            )
            print("Electrician created successfully")
        except Exception as e:
            print(f"Error creating electrician: {e}")
            messages.error(request, 'An error occurred while creating the electrician.')
            return render(request, 'admin_temp/add_electrician.html', {'skills': Skill.objects.all()})

        messages.success(request, 'Electrician added successfully!')
        return redirect('manage_electricians')  # Redirect to a relevant page

    else:
        print("Received GET request")
        skills = Skill.objects.all()
        print(f"Skills fetched: {skills}")
        return render(request, 'admin_temp/add_electrician.html', {'skills': skills})

def add_house_maid(request):
    if request.method == 'POST':
        print("Received POST request")

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        availability = request.POST.get('availability')
        place = request.POST.get('place')
        district = request.POST.get('district')
        address = request.POST.get('address')
        profilepic = request.FILES.get('profilepic')
        skill_id = request.POST.get('skill_id')

        print(f"Form data received: firstname={firstname}, lastname={lastname}, email={email}, phone={phone}, experience={experience}, availability={availability}, place={place}, district={district}, address={address}, skill_id={skill_id}, profilepic={profilepic}")

        # Basic validation
        if not (firstname and lastname and email and phone and experience and availability and skill_id):
            print("Validation failed: Missing required fields")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        if len(phone) != 10 or not phone.isdigit():
            print("Validation failed: Invalid phone number")
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        if not (1 <= int(experience) <= 35):
            print("Validation failed: Experience out of range")
            messages.error(request, 'Experience must be between 1 and 35 years.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        # Create a new user
        try:
            print("Creating new user")
            user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                district=district,
                place=place,
                address=address,
                password='defaultpassword',  # Use a default password or handle this securely
                usertype='house_maid'  # Set appropriate usertype
            )
            print(f"User created with user_id={user.user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'An error occurred while creating the user.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        # Fetch the skill object using the skill_id
        try:
            skill_id = int(skill_id)  # Ensure skill_id is an integer
            print(f"Skill ID to be fetched: {skill_id}")
            skill = Skill.objects.get(skill_id=skill_id)
            print(f"Skill fetched: {skill}")
        except Skill.DoesNotExist:
            print("Validation failed: Skill does not exist")
            messages.error(request, 'Invalid skill selected.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})
        except ValueError:
            print("Validation failed: Invalid skill_id format")
            messages.error(request, 'Invalid skill ID format.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        # Save the new house maid with the created user's user_id as a foreign key
        try:
            print("Creating new house maid entry")
            House_Maid.objects.create(
                user_id=user,
                skill_id=skill,  # Pass the Skill object
                experience=experience,
                availability=availability,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                place=place,
                district=district,
                address=address,
                profilepic=profilepic
            )
            print("House Maid created successfully")
        except Exception as e:
            print(f"Error creating house maid: {e}")
            messages.error(request, 'An error occurred while creating the house maid.')
            return render(request, 'admin_temp/add_house_maid.html', {'skills': Skill.objects.all()})

        messages.success(request, 'House Maid added successfully!')
        return redirect('manage_house_maids')  # Redirect to a relevant page

    else:
        print("Received GET request")
        skills = Skill.objects.all()
        print(f"Skills fetched: {skills}")
        return render(request, 'admin_temp/add_house_maid.html', {'skills': skills})


def add_home_nurse(request):
    if request.method == 'POST':
        print("Received POST request")

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        availability = request.POST.get('availability')
        place = request.POST.get('place')
        district = request.POST.get('district')
        address = request.POST.get('address')
        profilepic = request.FILES.get('profilepic')
        skill_id = request.POST.get('skill_id')

        print(f"Form data received: firstname={firstname}, lastname={lastname}, email={email}, phone={phone}, experience={experience}, availability={availability}, place={place}, district={district}, address={address}, skill_id={skill_id}, profilepic={profilepic}")

        # Basic validation
        if not (firstname and lastname and email and phone and experience and availability and skill_id):
            print("Validation failed: Missing required fields")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        if len(phone) != 10 or not phone.isdigit():
            print("Validation failed: Invalid phone number")
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        if not (1 <= int(experience) <= 35):
            print("Validation failed: Experience out of range")
            messages.error(request, 'Experience must be between 1 and 35 years.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        # Create a new user
        try:
            print("Creating new user")
            user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                district=district,
                place=place,
                address=address,
                password='defaultpassword',  # Use a default password or handle this securely
                usertype='home_nurse'  # Set appropriate usertype
            )
            print(f"User created with user_id={user.user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'An error occurred while creating the user.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        try:
            skill = Skill.objects.get(skill_id=skill_id)
            print(f"Skill fetched: {skill}")
        except Skill.DoesNotExist:
            print("Validation failed: Skill does not exist")
            messages.error(request, 'Invalid skill selected.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        # Save the new home nurse with the created user's user_id as a foreign key
        try:
            print("Creating new home nurse entry")
            Home_Nurse.objects.create(
                user_id=user,
                skill_id=skill,
                experience=experience,
                availability=availability,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                place=place,
                district=district,
                address=address,
                profilepic=profilepic
            )
            print("Home nurse created successfully")
        except Exception as e:
            print(f"Error creating home nurse: {e}")
            messages.error(request, 'An error occurred while creating the home nurse.')
            return render(request, 'admin_temp/add_home_nurse.html', {'skills': Skill.objects.all()})

        messages.success(request, 'Home nurse added successfully!')
        return redirect('manage_home_nurses')  # Redirect to a relevant page

    else:
        print("Received GET request")
        skills = Skill.objects.all()
        print(f"Skills fetched: {skills}")
        return render(request, 'admin_temp/add_home_nurse.html', {'skills': skills})

def add_carpenter(request):
    if request.method == 'POST':
        print("Received POST request")

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        availability = request.POST.get('availability')
        place = request.POST.get('place')
        district = request.POST.get('district')
        address = request.POST.get('address')
        profilepic = request.FILES.get('profilepic')
        skill_id = request.POST.get('skill_id')

        print(f"Form data received: firstname={firstname}, lastname={lastname}, email={email}, phone={phone}, experience={experience}, availability={availability}, place={place}, district={district}, address={address}, skill_id={skill_id}, profilepic={profilepic}")

        # Basic validation
        if not (firstname and lastname and email and phone and experience and availability and skill_id):
            print("Validation failed: Missing required fields")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        if len(phone) != 10 or not phone.isdigit():
            print("Validation failed: Invalid phone number")
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        if not (1 <= int(experience) <= 35):
            print("Validation failed: Experience out of range")
            messages.error(request, 'Experience must be between 1 and 35 years.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        # Create a new user
        try:
            print("Creating new user")
            user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                district=district,
                place=place,
                address=address,
                password='defaultpassword',  # Use a default password or handle this securely
                usertype='carpenter'  # Set appropriate usertype
            )
            print(f"User created with user_id={user.user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'An error occurred while creating the user.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        try:
            skill = Skill.objects.get(skill_id=skill_id)
            print(f"Skill fetched: {skill}")
        except Skill.DoesNotExist:
            print("Validation failed: Skill does not exist")
            messages.error(request, 'Invalid skill selected.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        # Save the new carpenter with the created user's user_id as a foreign key
        try:
            print("Creating new carpenter entry")
            Carpenter.objects.create(
                user_id=user,
                skill_id=skill,
                experience=experience,
                availability=availability,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone=phone,
                place=place,
                district=district,
                address=address,
                profilepic=profilepic
            )
            print("Carpenter created successfully")
        except Exception as e:
            print(f"Error creating carpenter: {e}")
            messages.error(request, 'An error occurred while creating the carpenter.')
            return render(request, 'admin_temp/add_carpenter.html', {'skills': Skill.objects.all()})

        messages.success(request, 'Carpenter added successfully!')
        return redirect('manage_carpenters')  # Redirect to a relevant page

    else:
        print("Received GET request")
        skills = Skill.objects.all()
        print(f"Skills fetched: {skills}")
        return render(request, 'admin_temp/add_carpenter.html', {'skills': skills})

def Full_usersPage(request):
    users = Users.objects.all() 
    return render(request, 'admin_temp/full_users.html', {'users': users})

def Full_customersPage(request):
    customers = Users.objects.filter(usertype='customer')  
    return render(request, 'admin_temp/full_customers.html', {'customers': customers})

def Full_workersPage(request):
    workers = Users.objects.exclude(usertype='customer') 
    return render(request, 'admin_temp/full_workers.html', {'workers': workers})

def new_bookings(request):
    # Retrieve all bookings
    bookings = Booking.objects.all()
    
    # Pass the bookings to the template
    context = {
        'bookings': bookings
    }
    
    return render(request, 'admin_temp/new_bookings.html', context)


# -------------------------  CUSTOMER SIDE ----------------------------- #

@never_cache
def HomePage(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        if user_id:
            user = Users.objects.get(user_id=user_id)
            
            # Update user information from the form data
            user.firstname = request.POST.get('first_name')
            user.lastname = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
            user.address = request.POST.get('address')
            
            # Handle profile picture update
            if 'profile_pic' in request.FILES:
                user.image = request.FILES['profile_pic']
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('home')

    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            
            # Count pending bookings for notification badge
            pending_booking_count = Booking.objects.filter(
                customer_id=user_id,
                status='Confirmed'  # Show notification for bookings that have been accepted by workers
            ).count()
            
            context = {
                'first_name': user.firstname,
                'last_name': user.lastname,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'profile_picture_url': user.image.url if user.image else '/media/default_profile_pic.png',
                'pending_booking_count': pending_booking_count,
            }
            return render(request, 'index.html', context)
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
    else:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')


def SignupPage(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_pass = request.POST.get('re_pass')

        if password != re_pass:
            return HttpResponse('Passwords do not match')
        else:
            # Hash the password before saving
            hashed_password = make_password(password)
            
            # Create a new User instance with the provided data
            my_user = Users(
                firstname=fname,
                lastname=lname,
                email=email,
                password=hashed_password,
                usertype='customer'  # Set the default usertype (this can be adjusted as needed)
            )
            my_user.save()
            return redirect('login')
        
    return render(request, 'signup.html')


from django.utils import timezone

def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Login attempt: Email={email}")

        # Check if the email belongs to the admin
        try:
            admin = User.objects.get(username=email)
            print(f"Admin found:")

            if check_password(password, admin.password):
                # Admin credentials
                
                request.session['user_email'] = admin.email
                messages.success(request, 'Admin login successful')
                print(f"Admin login successful:")
                return redirect('dashboard')  # Redirect to the admin dashboard or a specific page
            else:
                messages.error(request, 'Invalid Credentials')
                print("Admin login failed: Incorrect password")
        except User.DoesNotExist:
            print("Admin login failed: User does not exist")
            # If admin check fails, check regular users
            try:
                user = Users.objects.get(email=email)
                print(f"User found: User ID={user.user_id}")

                if check_password(password, user.password):
                    # Regular user credentials
                    request.session['user_id'] = user.user_id
                    request.session['user_email'] = user.email
                    
                    # Update active status and last login
                    user.active = True
                    user.last_login = timezone.now()
                    user.save()
                    
                    messages.success(request, 'Login successful')
                    print(f"User login successful: User ID={request.session.get('user_id')}")
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid Credentials')
                    print("User login failed: Incorrect password")
            except Users.DoesNotExist:
                messages.error(request, 'Invalid Credentials')
                print("User login failed: User does not exist")

    # Add this new block for worker login
        # Worker login check
    if request.method == 'POST':
        try:
            user = Users.objects.get(email=email)
            if user.password == password and user.usertype != 'customer':
                # Worker credentials
                request.session['user_id'] = user.user_id
                request.session['user_email'] = user.email
                messages.success(request, 'Worker login successful')
                print(f"Worker login successful: User ID={request.session.get('user_id')}")
                return redirect('worker_index')  # Redirect to the worker index page
        except Users.DoesNotExist:
            pass  # We've already handled this exception above

    return render(request, 'login.html')



def LogoutPage(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            user.active = False
            user.save()
        except Users.DoesNotExist:
            pass  # If user not found, continue with logout process
    
    logouts(request)
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# register, login and logout ends here


@never_cache
def customer_profile(request):
    user_id = request.session.get('user_id')  # Get user_id from session

    if request.method == 'POST':
        if user_id:
            try:
                user = Users.objects.get(user_id=user_id)
                
                # Update user information from the form data
                user.firstname = request.POST.get('first_name')
                user.lastname = request.POST.get('last_name')
                user.email = request.POST.get('email')
                user.phone = request.POST.get('phone')
                user.address = request.POST.get('address')
                
                # Handle profile picture update
                if 'profile_pic' in request.FILES:
                    user.image = request.FILES['profile_pic']
                
                user.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('home')  # Redirect to the home page after updating

            except Users.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('login')
        else:
            messages.warning(request, 'You need to log in first.')
            return redirect('login')

    # Handle GET request
    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            context = {
                'first_name': user.firstname,
                'last_name': user.lastname,
                'email': user.email,
                'phone': user.phone,
                'usertype': user.usertype,
                'address': user.address,
                'profile_picture_url': user.image.url if user.image else '/media/default_profile_pic.png',
            }
            return render(request, 'view_profile.html', context)
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
    else:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

   
@never_cache
def update_profile(request):
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        try:
            # Retrieve the user based on session ID
            user = Users.objects.get(user_id=user_id)
            
            # Update user fields from POST data
            user.firstname = request.POST.get('first_name', user.firstname)
            user.lastname = request.POST.get('last_name', user.lastname)
            user.phone = request.POST.get('phone', user.phone)
            user.address = request.POST.get('address', user.address)

            # Handle profile picture upload
            profile_pic = request.FILES.get('profile_pic', None)
            if profile_pic:
                user.image = profile_pic

            # Save the updated user information
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')

    else:
        # If GET request, render the profile update page with existing user data
        try:
            user = Users.objects.get(user_id=user_id)
            context = {
                'first_name': user.firstname,
                'last_name': user.lastname,
                'usertype': user.usertype,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'profile_picture_url': user.image.url if user.image else None
            }
            return render(request, 'update_profile.html', context)
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
# password reset code starts here 

def custom_password_reset(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Users.objects.get(email=email)
                current_site = get_current_site(request)
                mail_subject = 'Reset your password'
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = reverse('custom_password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
                reset_url = f"http://{current_site.domain}{reset_link}"
                message = render_to_string('registration/password_reset_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uidb64': uidb64,
                    'token': token,
                    'reset_url': reset_url
                })
                email_message = EmailMessage(mail_subject, message, 'webmaster@localhost', [email])
                email_message.content_subtype = 'html'
                email_message.send()
                messages.success(request, 'A link to reset your password has been sent to your email.')
                return redirect('custom_password_reset_done')
            except User.DoesNotExist:
                messages.error(request, 'No user is associated with this email address.')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})

def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Users.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been set. You can now log in with the new password.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('custom_password_reset')

def custom_password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


from datetime import datetime
@never_cache
def view_maids(request):
    districts = House_Maid.objects.values_list('district', flat=True).distinct()
    
    selected_district = request.GET.get('district', '')
    selected_date = request.GET.get('available_date', '')
  
    maids = House_Maid.objects.all()
   
    if selected_district and selected_district != "Search by district":
        maids = maids.filter(district=selected_district)

    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            booked_worker_ids = Booking.objects.filter(
                appointment_date=date_obj,
                worker_type='House Maid'
            ).values_list('worker_id', flat=True)
            
            maids = maids.exclude(user_id__in=booked_worker_ids)
        except ValueError:
            # Handle invalid date format
            pass
    
    context = {
        'maids': maids,
        'districts': districts,
        'selected_district': selected_district,
        'selected_date': selected_date,
    }
    return render(request, 'view_maids.html', context)

@never_cache
def view_plumbers(request):
    # Get all unique districts from the Plumber model
    districts = Plumber.objects.values_list('district', flat=True).distinct()
    
    # Get the selected district from the query parameters
    selected_district = request.GET.get('district', '')
    
    # Filter plumbers based on the selected district
    if selected_district:
        plumbers = Plumber.objects.filter(district=selected_district)
    else:
        plumbers = Plumber.objects.all()
    
    context = {
        'plumbers': plumbers,
        'districts': districts,
        'selected_district': selected_district,
    }
    return render(request, 'view_plumbers.html', context)
    
@never_cache
def view_electricians(request):
    # Get all unique districts from the Electrician model
    districts = Electrician.objects.values_list('district', flat=True).distinct()
    
    # Get the selected district from the query parameters
    selected_district = request.GET.get('district', '')
    
    # Filter electricians based on the selected district
    if selected_district:
        electricians = Electrician.objects.filter(district=selected_district)
    else:
        electricians = Electrician.objects.all()
    
    context = {
        'electricians': electricians,
        'districts': districts,
        'selected_district': selected_district,
    }
    return render(request, 'view_electricians.html', context)

@never_cache
def view_nurses(request):
    # Get all unique districts from the Nurse model
    districts = Home_Nurse.objects.values_list('district', flat=True).distinct()
    
    # Get the selected district from the query parameters
    selected_district = request.GET.get('district', '')
    
    # Filter nurses based on the selected district
    if selected_district:
        nurses = Home_Nurse.objects.filter(district=selected_district)
    else:
        nurses = Home_Nurse.objects.all()
    
    context = {
        'nurses': nurses,
        'districts': districts,
        'selected_district': selected_district,
    }
    return render(request, 'view_nurses.html', context)


from django.db.models import Prefetch
@never_cache
def view_carpenters(request):
    # Get all unique districts from the Carpenter model
    districts = Carpenter.objects.values_list('district', flat=True).distinct()
    
    # Get the selected district from the query parameters
    selected_district = request.GET.get('district', '')
    
    # Filter carpenters based on the selected district
    if selected_district:
        carpenters = Carpenter.objects.filter(district=selected_district)
    else:
        carpenters = Carpenter.objects.all()
    
    # Prefetch related Users to optimize database queries
    carpenters = carpenters.select_related('user_id')
    
    context = {
        'carpenters': carpenters,
        'districts': districts,
        'selected_district': selected_district,
    }
    return render(request, 'view_carpenters.html', context)

@never_cache
def view_bookings(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

    # Fetch all bookings made by the logged-in user
    bookings = Booking.objects.filter(customer_id=user_id)

    # Fetch payment status for each booking
    for booking in bookings:
        payment = Payments.objects.filter(booking_id=booking).first()
        booking.payment_status = payment.status if payment else 'Pending'
        
        # Store the last viewed status in session if not already there
        booking_status_key = f'booking_{booking.id}_status'
        if booking_status_key not in request.session:
            request.session[booking_status_key] = booking.status

    context = {
        'bookings': bookings
    }
    return render(request, 'view_booking.html', context)


@never_cache
def check_booking_updates(request):
    """Check for updates to the user's bookings and return notifications"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return JsonResponse({'has_updates': False})
    
    # Get all bookings for this customer
    bookings = Booking.objects.filter(customer_id=user_id)
    
    has_updates = False
    messages = []
    reload_page = False
    
    # Check each booking for status changes
    for booking in bookings:
        booking_status_key = f'booking_{booking.id}_status'
        last_status = request.session.get(booking_status_key)
        
        if last_status and last_status != booking.status:
            # Status has changed, create a notification
            worker_name = f"{booking.worker_id.firstname} {booking.worker_id.lastname}"
            
            if booking.status == 'Confirmed':
                message = f"Your booking with {worker_name} has been accepted! You can now make payment."
                reload_page = True
            elif booking.status == 'Cancelled':
                message = f"Your booking with {worker_name} has been cancelled by the worker."
                reload_page = True
            elif booking.status == 'Completed':
                message = f"Your booking with {worker_name} has been marked as completed."
            else:
                message = f"Your booking status has changed to {booking.status}."
            
            messages.append(message)
            has_updates = True
            
            # Update the session to reflect the current status
            request.session[booking_status_key] = booking.status
    
    # Combine all messages
    combined_message = "\n".join(messages)
    
    return JsonResponse({
        'has_updates': has_updates,
        'message': combined_message,
        'reload': reload_page
    })
@never_cache
def view_services(request):
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            context = {
                'first_name': user.firstname,
                'last_name': user.lastname,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'profile_picture_url': user.image.url if user.image else '/media/default_profile_pic.png',
            }
            return render(request, 'services.html', context)
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
    else:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

from decimal import Decimal
@never_cache
def book_service(request, maid_id):
    user_id = request.session.get('user_id')
    
    # Fetch the maid or return a 404 error if not found
    maid = get_object_or_404(House_Maid, maid_id=maid_id)
    
    # Check if the user is logged in
    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_start_time = request.POST.get('appointment_start_time')
        address = request.POST.get('address')
        service_type = request.POST.get('service_type')
        phone = request.POST.get('phone')
        description = request.POST.get('description')
        
        # Fixed booking charge instead of hourly calculation
        fixed_booking_charge = Decimal('59.00')
        
        # Fetch the customer (logged-in user) or return an error if not found
        try:
            customer = Users.objects.get(user_id=user_id)
            
            # Create and save the booking
            booking = Booking(
                worker_id=maid.user_id,
                worker_type='House Maid',
                customer_id=customer,
                appointment_date=appointment_date,
                appointment_time=appointment_start_time,
                address=address,
                status='Pending',
                service_type='house_maid',
                hours_booked=1,  # Default to 1 since we're not calculating hours anymore
                description=description,
                pay_amount=fixed_booking_charge  # Set the fixed booking charge directly
            )
            booking.save()
            
            messages.success(request, 'Booking successfully created!')
            return redirect('view_bookings')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_maids')
    
    # Provide the maid object to the template for displaying details
    context = {
        'maid': maid,
        'today_date': datetime.now().date(),
    }
    return render(request, 'registration/book_service.html', context)


@never_cache
def book_home_nurse(request, nurse_id):
    user_id = request.session.get('user_id')
    
    # Fetch the home nurse or return a 404 error if not found
    nurse = get_object_or_404(Home_Nurse, nurse_id=nurse_id)
    
    # Check if the user is logged in
    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        address = request.POST.get('address')
        
        # Fetch the customer (logged-in user) or return an error if not found
        try:
            customer = Users.objects.get(user_id=user_id)
            
            # Create and save the booking
            booking = Booking(
                worker_id=nurse.user_id,  # Use nurse's user_id as the worker
                worker_type='Home Nurse',  # Correct worker type
                customer_id=customer,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                address=address,
                status='Pending'  # Default status
            )
            booking.save()
            
            messages.success(request, 'Booking successfully created!')
            return redirect('view_bookings')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_nurses')
    
    # Provide the nurse object to the template for displaying details
    context = {
        'nurse': nurse
    }
    return render(request, 'registration/book_nurse.html', context)

@never_cache
def book_carpenter(request, carpenter_id):
    user_id = request.session.get('user_id')
    
    # Fetch the carpenter or return a 404 error if not found
    carpenter = get_object_or_404(Carpenter, carpenter_id=carpenter_id)
    
    # Check if the user is logged in
    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        address = request.POST.get('address')
        service_type = request.POST.get('service_type')  # New line
        description = request.POST.get('description')  # New line
        
        # Fetch the customer (logged-in user) or return an error if not found
        try:
            customer = Users.objects.get(user_id=user_id)
            
            # Create and save the booking
            booking = Booking(
                worker_id=carpenter.user_id,  # Use carpenter's user_id as the worker
                worker_type='Carpenter',  # Correct worker type
                customer_id=customer,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                address=address,
                status='Pending',  # Default status
                service_type=service_type,  # New line
                description=description  # New line
            )
            booking.save()
            
            messages.success(request, 'Booking successfully created!')
            return redirect('view_bookings')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_carpenters')
    
    # Provide the carpenter object to the template for displaying details
    context = {
        'carpenter': carpenter
    }
    return render(request, 'registration/book_carpenter.html', context)

@never_cache
def book_plumber(request, plumber_id):
    user_id = request.session.get('user_id')
    
    # Fetch the plumber or return a 404 error if not found
    plumber = get_object_or_404(Plumber, plumber_id=plumber_id)
    
    # Check if the user is logged in
    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        address = request.POST.get('address')
        
        # Fetch the customer (logged-in user) or return an error if not found
        try:
            customer = Users.objects.get(user_id=user_id)
            
            # Create and save the booking
            booking = Booking(
                worker_id=plumber.user_id,  # Use plumber's user_id as the worker
                worker_type='Plumber',  # Correct worker type
                customer_id=customer,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                address=address,
                status='Pending'  # Default status
            )
            booking.save()
            
            messages.success(request, 'Booking successfully created!')
            return redirect('view_bookings')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_plumbers')
    
    # Provide the plumber object to the template for displaying details
    context = {
        'plumber': plumber
    }
    return render(request, 'registration/book_plumber.html', context)

@never_cache
def book_electrician(request, electrician_id):
    user_id = request.session.get('user_id')
    
    # Fetch the electrician or return a 404 error if not found
    electrician = get_object_or_404(Electrician, electrician_id=electrician_id)
    
    # Check if the user is logged in
    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        address = request.POST.get('address')
        
        # Fetch the customer (logged-in user) or return an error if not found
        try:
            customer = Users.objects.get(user_id=user_id)
            
            # Create and save the booking
            booking = Booking(
                worker_id=electrician.user_id,  # Use electrician's user_id as the worker
                worker_type='Electrician',  # Correct worker type
                customer_id=customer,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                address=address,
                status='Pending'  # Default status
            )
            booking.save()
            
            messages.success(request, 'Booking successfully created!')
            return redirect('view_bookings')
        
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_electricians')
    
    # Provide the electrician object to the template for displaying details
    context = {
        'electrician': electrician
    }
    return render(request, 'registration/book_electrician.html', context)

@never_cache
def emailsearch(request):

    # Get the search query from the GET request
    email_query = request.GET.get('email', '')
    
    # Filter workers by email if a search query is provided, otherwise return all workers
    if email_query:
        workers = Users.objects.filter(email__icontains=email_query)
    else:
        workers = Users.objects.all()
    
    # Pass the filtered workers to the template
    context = {
        'workers': workers
    }
    return render(request, 'admin_temp/full_workers.html', context)

@never_cache
def usersemailsearch(request):

    # Get the search query from the GET request
    email_query = request.GET.get('email', '')
    
    # Filter users by email if a search query is provided, otherwise return all users
    if email_query:
        customers = Users.objects.filter(email__icontains=email_query)
    else:
        customers = Users.objects.all()
    
    # Pass the filtered users to the template
    context = {
        'customers': customers
    }
    return render(request, 'admin_temp/full_customers.html', context)

@never_cache
def searchbookstatus(request):
    # Get the status query from the GET request
    status_query = request.GET.get('status', '')

    # Filter bookings by status if a search query is provided, otherwise return all bookings
    if status_query:
        bookings = Booking.objects.filter(status__iexact=status_query.capitalize())
    else:
        bookings = Booking.objects.all()

    # Pass the filtered bookings to the template
    context = {
        'bookings': bookings
    }
    return render(request, 'admin_temp/new_bookings.html', context)


@csrf_exempt
@require_POST
def update_booking_status(request):
    booking_id = request.POST.get('booking_id')
    new_status = request.POST.get('status')
    non_refundable = request.POST.get('non_refundable') == 'true'
    
    # Ensure the new_status is valid
    valid_statuses = ['Pending', 'Paid', 'Confirmed', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # Check if this is a paid booking being cancelled
        if booking.status == 'Paid' and new_status == 'Cancelled':
            # Only allow if non_refundable flag is set
            if not non_refundable:
                return JsonResponse({
                    'success': False, 
                    'error': 'Cannot cancel a paid booking without confirmation.', 
                    'requires_confirmation': True
                })
            # If we get here, user has confirmed non-refundable cancellation
        
        booking.status = new_status
        booking.save()
        return JsonResponse({'success': True})
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})




from django.http import JsonResponse
from .models import Booking
import json


def update_worker_booking_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            new_status = data.get('status')
            print(f"Received booking ID: {booking_id}, New status: {new_status}")  # Log booking ID and status

            booking = Booking.objects.get(id=booking_id)
            
            # Validate that the worker making the request is the assigned worker
            if str(booking.worker_id.user_id) != str(request.session.get('user_id')):
                return JsonResponse({'success': False, 'error': 'Unauthorized to update this booking'})
            
            # For marking as completed, allow if status is Confirmed or Paid
            if new_status == 'Completed' and booking.status in ['Confirmed', 'Paid']:
                booking.status = new_status
                booking.save()
                return JsonResponse({'success': True})
                
            # For accepting/rejecting, only allow if the booking is in Pending state
            elif new_status in ['Confirmed', 'Cancelled'] and booking.status == 'Pending':
                booking.status = new_status
                booking.save()
                
                # Create a notification record for the customer
                try:
                    # You could create a Notification model for this, but for now we'll use session
                    # The actual notification is handled by the check_booking_updates endpoint
                    pass
                except Exception as notification_error:
                    print(f"Error creating notification: {notification_error}")
                    
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status change'})
                
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from .models import WorkerRating



import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import WorkerRating, Users, Booking

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def submit_rating(request):
    logger.debug(f"Received POST data: {request.POST}")
    worker_id = request.POST.get('worker_id')
    customer_id = request.POST.get('customer_id')
    rating_value = request.POST.get('rating')
    comment = request.POST.get('comment')

    logger.debug(f"Parsed data: worker_id={worker_id}, customer_id={customer_id}, rating={rating_value}, comment={comment}")

    if not worker_id or not customer_id:
        logger.error(f"Worker ID or Customer ID is empty or None. worker_id: {worker_id}, customer_id: {customer_id}")
        return JsonResponse({'success': False, 'message': 'Worker ID and Customer ID are required'}, status=400)

    try:
        worker = Users.objects.get(user_id=worker_id)
        customer = Users.objects.get(user_id=customer_id)
        logger.debug(f"Found worker: {worker}, customer: {customer}")
        rating, created = WorkerRating.objects.update_or_create(
            customer=customer,
            worker=worker,
            defaults={
                'rating': rating_value,
                'comment': comment
            }
        )
        logger.info(f"Rating {'created' if created else 'updated'} successfully: {rating}")
        return JsonResponse({'success': True, 'message': 'Rating submitted successfully'})
    except Users.DoesNotExist as e:
        logger.error(f"User does not exist: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error creating/updating rating: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




# ------------------WORKER Views----------------------

@never_cache
def worker_index(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        if user_id:
            user = Users.objects.get(user_id=user_id)
            
            # Update user information from the form data
            user.firstname = request.POST.get('first_name')
            user.lastname = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
            user.address = request.POST.get('address')
            
            # Handle profile picture update
            if 'profile_pic' in request.FILES:
                user.image = request.FILES['profile_pic']
            
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('worker_index')

    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            
            # Get pending bookings for this worker that need acceptance
            pending_bookings = Booking.objects.filter(
                worker_id=user,
                status='Pending'
            ).order_by('-appointment_date', '-appointment_time')
            
            context = {
                'first_name': user.firstname,
                'last_name': user.lastname,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'profile_picture_url': user.image.url if user.image else '/media/default_profile_pic.png',
                'pending_bookings': pending_bookings,
                'pending_bookings_count': pending_bookings.count(),
            }
            return render(request, 'worker_temp/worker_index.html', context)
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
    else:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import Users  # Make sure to import your Users model

from django.db.models import Avg, Count
from .models import WorkerRating, Users
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.cache import never_cache

@never_cache
def worker_profile(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

    try:
        user = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

    if request.method == 'POST':
        # Update user information from the form data
        user.firstname = request.POST.get('first_name')
        user.lastname = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')

        # Handle profile picture update
        if 'profile_pic' in request.FILES:
            user.image = request.FILES['profile_pic']

        try:
            user.save()
            messages.success(request, 'Profile updated successfully.')
        except IntegrityError:
            messages.error(request, 'An error occurred while saving. Please check all fields.')

        # Redirect to the same page to show the updated information
        return redirect('worker_profile')

    # Calculate average rating and total ratings
    worker_ratings = WorkerRating.objects.filter(worker=user)
    average_rating = worker_ratings.aggregate(Avg('rating'))['rating__avg']
    total_ratings = worker_ratings.count()

    if average_rating:
        average_rating = round(average_rating, 1)  # Round to one decimal place

    # Prepare context for both GET and POST (after unsuccessful save) requests
    context = {
        'first_name': user.firstname,
        'last_name': user.lastname,
        'email': user.email,
        'phone': user.phone,
        'usertype': user.usertype,
        'address': user.address,
        'profile_picture_url': user.image.url if user.image else '/media/default_profile_pic.png',
        'average_rating': average_rating,
        'total_ratings': total_ratings,
    }

    return render(request, 'worker_temp/worker_profile.html', context)
    
    
from django.db.models import F

def view_my_booking(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.warning(request, 'You need to log in first.')
        return redirect('login')

    try:
        worker = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

    # Fetch all bookings for the logged-in worker with customer details
    bookings = Booking.objects.filter(
        worker_id=worker.user_id,
        status__in=['Paid', 'Completed', 'Confirmed', 'Pending', 'Cancelled']  # Show all statuses
    ).select_related('customer_id').annotate(
        customer_firstname=F('customer_id__firstname'),
        customer_lastname=F('customer_id__lastname'),
        customer_email=F('customer_id__email'),
        customer_phone=F('customer_id__phone')
    ).order_by('-appointment_date', '-appointment_time')
    
    # Count pending bookings for notification badge
    pending_count = bookings.filter(status='Pending').count()

    context = {
        'bookings': bookings,
        'pending_bookings_count': pending_count
    }

    return render(request, 'worker_temp/view_my_booking.html', context)










from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
# from xhtml2pdf import pisa
from io import BytesIO
from .models import Booking
# from num2words import num2words
from django.utils import timezone
import random
import num2words
from xhtml2pdf import pisa 

def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if the user has permission to download this invoice
    if booking.customer_id.user_id != request.session.get('user_id'):
        return HttpResponse("Unauthorized", status=403)
    
    # Convert amount to words
    amount_in_words = num2words.num2words(float(booking.pay_amount), lang='en_IN', to='currency', currency='INR')
    amount_in_words = amount_in_words.replace(',', ' and').capitalize()
    
    # Generate a random invoice number
    invoice_number = f"INV-{random.randint(100000, 999999)}"
    
    # Prepare context data for the template
    context = {
        'booking': booking,
        'customer': booking.customer_id,
        'worker': booking.worker_id,
        'amount_in_words': amount_in_words,
        'invoice_date': timezone.now().date(),
        'invoice_number': invoice_number,  # Add this line
    }
    
    # Get the template
    template = get_template('invoice_template.html')
    html = template.render(context)
    
    # Create a PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
        return response
    
    return HttpResponse('Error generating PDF', status=400)




import base64
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from deepface import DeepFace
from .models import Users
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import io
from PIL import Image

@csrf_exempt
def worker_verification(request):
    if request.method == 'GET':
        return render(request, 'worker_temp/verification.html')
    
    elif request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'User not logged in'})

        captured_image = request.POST.get('captured_image')
        
        if not captured_image:
            return JsonResponse({'success': False, 'message': 'No image data received'})
        
        try:
            # Remove the data URL prefix
            _, captured_image = captured_image.split(',', 1)
            
            # Convert base64 string to image
            captured_image = base64.b64decode(captured_image)
            captured_image = Image.open(io.BytesIO(captured_image))
            
            # Convert PIL Image to numpy array
            captured_image = np.array(captured_image)
            
            # Get the worker's reference image
            user = get_object_or_404(Users, user_id=user_id)
            if not user.image:
                return JsonResponse({'success': False, 'message': 'No profile image found for this user'})

            reference_image = Image.open(user.image.path)
            reference_image = np.array(reference_image)
            
            # Perform facial verification
            result = DeepFace.verify(captured_image, reference_image, enforce_detection=False)
            
            if result['verified']:
                # Update user's verification status
                user.is_verified = True
                user.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Verification successful',
                    'redirect_url': reverse('worker_index')
                })
            else:
                return JsonResponse({'success': False, 'message': 'Verification failed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


import logging
logger = logging.getLogger(__name__)
@never_cache
@csrf_exempt
def send_message(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'})

    if request.method == 'POST':
        message = request.POST.get('message')
        
        if not message:
            return JsonResponse({'status': 'error', 'message': 'No message provided'})
        
        try:
            sender = get_object_or_404(Users, user_id=user_id)
            
            # Get the admin user (assuming there's only one admin)
            admin_receiver = Users.objects.filter(usertype='admin').first()
            
            if not admin_receiver:
                return JsonResponse({'status': 'error', 'message': 'Admin user not found'})

            chat_message = ChatMessage.objects.create(
                sender=sender,
                receiver=admin_receiver,  # Set the admin as the default receiver
                message=message
            )
            logger.info(f"Message saved: {chat_message}")
            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@never_cache
def get_messages(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'})

    try:
        messages = ChatMessage.objects.all().order_by('timestamp')
        message_list = [{'sender': msg.sender.firstname, 'message': msg.message} for msg in messages]
        return JsonResponse({'status': 'success', 'messages': message_list})
    except Exception as e:
        logger.error(f"Error retrieving messages: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})


from django.db.models import Max, OuterRef, Subquery
def admin_new_chat(request):
    # Subquery to get the latest message ID for each sender
    latest_messages = ChatMessage.objects.filter(
        sender=OuterRef('sender')
    ).order_by('-timestamp').values('id')[:1]

    # Fetch the most recent message from each unique sender
    messages = ChatMessage.objects.filter(
        id=Subquery(latest_messages)
    ).exclude(sender_id=22).select_related('sender').order_by('-timestamp')[:20]
    
    context = {
        'messages': messages,
    }
    return render(request, 'admin_temp/new_chat.html', context)


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ChatMessage, Users

def admin_view_chat(request, user_id):
    print(f"Debugging: user_id received = {user_id}")

    try:
        user = get_object_or_404(Users, user_id=user_id)
        print(f"Debugging: User found - ID: {user.user_id}, Active: {user.active}")

        # Get the admin user (assuming there's only one admin)
        admin_user = Users.objects.filter(usertype='admin').first()

        if not admin_user:
            return HttpResponse("Admin user not found")

        # Fetch all messages between this user and the admin
        chat_messages = ChatMessage.objects.filter(
            Q(sender=user, receiver=admin_user) | Q(sender=admin_user, receiver=user)
        ).order_by('timestamp')
        
        print(f"Debugging: Number of messages found: {chat_messages.count()}")

    except Exception as e:
        print(f"Debugging: Exception occurred - {str(e)}")
        return HttpResponse(f"An error occurred: {str(e)}")
    
    context = {
        'user': user,
        'chat_messages': chat_messages,
        'admin_user': admin_user,
    }
    return render(request, 'admin_temp/view_chat.html', context)

def adm_send_message(request, user_id):
    if request.method == 'POST':
        recipient = get_object_or_404(Users, user_id=user_id)
        message = request.POST.get('message')
        
        if message:
            # Get the admin user (assuming there's only one admin)
            admin_sender = Users.objects.filter(usertype='admin').first()
            
            if admin_sender:
                ChatMessage.objects.create(
                    sender=admin_sender,
                    receiver=recipient,
                    message=message
                )
            else:
                # Handle the case where no admin user is found
                return JsonResponse({'status': 'error', 'message': 'Admin user not found'})
        
        return redirect('admin_view_chat', user_id=user_id)
    
    return redirect('admin_view_chat', user_id=user_id)


from django.views.decorators.http import require_GET
@require_GET
def check_user_status(request):
    user_id = request.GET.get('user_id')
    try:
        user = Users.objects.get(user_id=user_id)
        return JsonResponse({'active': user.active})
    except Users.DoesNotExist:
        return JsonResponse({'active': False})



import razorpay
logger = logging.getLogger(__name__)

from django.shortcuts import redirect  # Ensure you import redirect

import logging
logger = logging.getLogger(__name__)

def create_payment(request, booking_id):
    print(f"Create payment view called with booking ID: {booking_id}")
    logger.debug(f"create_payment called with booking_id: {booking_id}")
    
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        logger.debug(f"Booking retrieved: {booking}")
        
        service_rate = ServiceRate.objects.get(service_type=booking.service_type)
        if booking.pay_amount is None:
            booking.calculate_pay_amount()
        
        amount = booking.pay_amount
        logger.debug(f"Amount to be paid: {amount}")

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        logger.debug("Razorpay client initialized")
        
        order_data = {
            'amount': int(amount * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'
        }
        logger.debug(f"Order data prepared: {order_data}")
        
        order = client.order.create(order_data)
        logger.debug(f"Order created: {order}")
        
        payment = Payments.objects.create(
            booking_id=booking,
            amount=amount,
            order_id=order['id']
        )
        logger.debug(f"Payment created: {payment}")

        return redirect('payment_page', payment_id=payment.payment_id)
    
    except ServiceRate.DoesNotExist:
        logger.error(f"ServiceRate does not exist for service type: {booking.service_type}")
        messages.error(request, 'Service rate not found for the specified service type.')
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay BadRequestError: {str(e)}")
        messages.error(request, 'An error occurred while creating the payment order.')
    except Exception as e:
        logger.error(f"Error in create_payment: {str(e)}")
        messages.error(request, 'An error occurred while creating the payment.')
    
    return redirect('view_bookings')  # Redirect to bookings page if there's an error

@csrf_exempt
def verify_payment(request, payment_id):
    logger.debug(f"verify_payment called with payment_id: {payment_id}")
    payment = get_object_or_404(Payments, payment_id=payment_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

    if request.method == "POST":
        try:
            params_dict = {
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }

            client.utility.verify_payment_signature(params_dict)
            payment.razorpay_id = params_dict['razorpay_payment_id']
            payment.status = 'completed'
            payment.save()

            booking = payment.booking_id
            booking.status = 'Paid'
            booking.save()

            logger.info(f"Payment verified successfully: {payment.payment_id}")
            return redirect('payment_success')

        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Payment signature verification failed: {payment.payment_id}")
            payment.status = 'failed'
            payment.save()
            return redirect('payment_failed')
        except Exception as e:
            logger.error(f"Error in verify_payment: {str(e)}")
            return redirect('payment_failed')

    return render(request, 'payment_failed.html')

@csrf_exempt
def payment_callback(request):
    logger.debug("payment_callback called")
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        
        try:
            params_dict = {
                'razorpay_payment_id': request.POST['razorpay_payment_id'],
                'razorpay_order_id': request.POST['razorpay_order_id'],
                'razorpay_signature': request.POST['razorpay_signature']
            }

            client.utility.verify_payment_signature(params_dict)

            payment = Payments.objects.get(order_id=params_dict['razorpay_order_id'])
            payment.payment_id = params_dict['razorpay_payment_id']
            payment.status = 'completed'
            payment.save()

            booking = payment.booking_id
            booking.status = 'Paid'
            booking.save()

            logger.info(f"Payment callback successful: {payment.payment_id}")
            return redirect('payment_success')

        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Payment callback signature verification failed")
            return redirect('payment_failed')
        except Exception as e:
            logger.error(f"Error in payment_callback: {str(e)}")
            return redirect('payment_failed')
    
    return HttpResponseBadRequest()

def payment_page(request, payment_id):
    logger.debug(f"payment_page called with payment_id: {payment_id}")
    payment = get_object_or_404(Payments, payment_id=payment_id)
    context = {
        'order_id': payment.order_id,
        'razorpay_key': settings.RAZORPAY_API_KEY,
        'amount': payment.amount,
        'booking': payment.booking_id,
        'payment': payment,
        'payment_id': payment.payment_id
    }
    logger.debug(f"Payment page context: {context}")  # Add this line
    return render(request, 'payment_page.html', context)

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import WorkerVerification, Users

def is_admin(user):
    return user.is_authenticated and user.is_staff


def view_verification(request):
    # Fetch all worker verifications, ordered by submission date
    verifications = WorkerVerification.objects.all().order_by('-submitted_at')

    context = {
        'verifications': verifications,
    }

    return render(request, 'admin_temp/worker_verification.html', context)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Users, Booking, WorkerRating, Payments  # Import your models
import json

@csrf_exempt
def generate_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_type = data.get('reportType')
            filters = data.get('filters', {})

            logger.info(f"Generating report for type: {report_type} with filters: {filters}")

            results = []

            if report_type == 'users':
                queryset = Users.objects.all()
                
                if filters.get('userType'):
                    user_type = filters['userType']
                    if user_type == 'worker':
                        queryset = queryset.filter(usertype__in=['house_maid', 'home_nurse', 'carpenter', 'electrician', 'plumber'])
                    else:
                        queryset = queryset.filter(usertype=user_type)
                
                if filters.get('userStatus'):
                    queryset = queryset.filter(active=(filters['userStatus'] == 'active'))

                results = list(queryset.values('user_id', 'firstname', 'lastname', 'email', 'usertype', 'active', 'district', 'phone'))

                # If worker types are selected, add worker-specific information
                if filters.get('userType') == 'worker':
                    worker_types = {
                        'house_maid': House_Maid.objects.all().values('user_id', 'experience'),
                        'home_nurse': Home_Nurse.objects.all().values('user_id', 'experience'),
                        'carpenter': Carpenter.objects.all().values('user_id', 'experience'),
                        'electrician': Electrician.objects.all().values('user_id', 'experience'),
                        'plumber': Plumber.objects.all().values('user_id', 'experience'),
                    }

                    worker_type_dict = {}
                    for worker_type, workers in worker_types.items():
                        for worker in workers:
                            worker_type_dict[worker['user_id']] = {
                                'worker_type': worker_type,
                                'experience': worker['experience']
                            }

                    verifications = WorkerVerification.objects.filter(worker_id__in=[r['user_id'] for r in results])
                    verification_dict = {v.worker_id: v.verification_status for v in verifications}

                    for result in results:
                        worker_info = worker_type_dict.get(result['user_id'], {})
                        result['worker_type'] = worker_info.get('worker_type', result['usertype'])
                        result['experience'] = worker_info.get('experience', 'N/A')
                        result['verification_status'] = verification_dict.get(result['user_id'], 'Not submitted')

            elif report_type == 'bookings':
                queryset = Booking.objects.all()
                if filters.get('bookingStatus'):
                    queryset = queryset.filter(status=filters['bookingStatus'])
                if filters.get('serviceType'):
                    queryset = queryset.filter(worker_type=filters['serviceType'])
                if filters.get('dateFrom'):
                    queryset = queryset.filter(appointment_date__gte=filters['dateFrom'])
                if filters.get('dateTo'):
                    queryset = queryset.filter(appointment_date__lte=filters['dateTo'])

                results = list(queryset.values(
                    'id', 'worker_id__firstname', 'customer_id__firstname', 
                    'worker_type', 'status', 'appointment_date', 'pay_amount'
                ))

            elif report_type == 'workers':
                worker_type = filters.get('workerType')
                
                if worker_type:
                    queryset = Users.objects.filter(usertype=worker_type)
                else:
                    queryset = Users.objects.filter(usertype__in=['house_maid', 'home_nurse', 'carpenter', 'electrician', 'plumber'])
                
                # Fetch all worker types
                worker_models = {
                    'house_maid': House_Maid,
                    'home_nurse': Home_Nurse,
                    'carpenter': Carpenter,
                    'electrician': Electrician,
                    'plumber': Plumber,
                }

                worker_types = {}
                for wt, model in worker_models.items():
                    worker_types[wt] = {w['user_id']: w['experience'] for w in model.objects.all().values('user_id', 'experience')}

                results = list(queryset.values(
                    'user_id', 'firstname', 'lastname', 'email', 'phone', 'district', 'availability', 'usertype'
                ))

                # Add worker type and experience
                for result in results:
                    worker_type = result['usertype']
                    result['worker_type'] = worker_type
                    result['experience'] = worker_types[worker_type].get(result['user_id'], 'N/A')

                # Add verification status
                verifications = WorkerVerification.objects.filter(worker_id__in=[r['user_id'] for r in results])
                verification_dict = {v.worker_id: v.verification_status for v in verifications}
                
                for result in results:
                    result['verification_status'] = verification_dict.get(result['user_id'], 'Not submitted')

            elif report_type == 'financial':
                queryset = Payments.objects.all()
                if filters.get('paymentStatus'):
                    queryset = queryset.filter(status=filters['paymentStatus'])

                results = list(queryset.values(
                    'payment_id',
                    'booking_id__customer_id__firstname',
                    'booking_id__customer_id__lastname',
                    'booking_id__worker_id__firstname',
                    'booking_id__worker_id__lastname',
                    'amount',
                    'status',
                    'created_at'
                ).order_by('-created_at'))  # Most recent payments first

            logger.info(f"Generated results: {results[:5]}...")  # Log first 5 results
            return JsonResponse({'success': True, 'results': results})
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def report_generation(request):
    context = {
        'page_title': 'Report Generation',
    }
    return render(request, 'admin_temp/report_generation.html', context)




import csv
from django.http import HttpResponse

def download_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_type = data.get('reportType')
            filters = data.get('filters', {})

            # Generate the report data (reuse your existing logic)
            results = generate_report_data(report_type, filters)

            # Create a CSV file
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

            writer = csv.writer(response)

            # Write headers
            if results:
                writer.writerow(results[0].keys())

            # Write data rows
            for row in results:
                writer.writerow(row.values())

            return response

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_report_data(report_type, filters):
    # This function should contain the logic from your existing generate_report function
    # but instead of returning a JsonResponse, it should return the results list
    # Copy the relevant parts of your generate_report function here
    # ...
    return results

def emergency_view(request):
    context = {
        'first_name': request.user.first_name if request.user.is_authenticated else ''
    }
    return render(request, 'emergency.html', context)