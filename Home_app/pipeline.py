from .models import Users  # Replace 'yourapp' with the actual app name
from django.contrib.auth.hashers import make_password

def create_or_update_user(strategy, details, response, *args, **kwargs):
    """Create or update user based on details from social auth."""
    user = None
    email = details.get('email')
    
    if email:
        try:
            # Check if the user already exists
            user = Users.objects.get(email=email)
            # Update user details if needed
            user.firstname = details.get('first_name', user.firstname)
            user.lastname = details.get('last_name', user.lastname)
            user.save()
        except Users.DoesNotExist:
            # Create a new user if not exists
            user = Users.objects.create(
                firstname=details.get('first_name'),
                lastname=details.get('last_name'),
                email=email,
                password='',  # Set a default password or handle accordingly
                usertype='customer',  # Adjust this as needed
            )
    
    return {'user': user}

