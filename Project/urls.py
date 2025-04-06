from django.contrib import admin
from Home_app import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.SignupPage, name='signup'),
    path('login/', views.LoginPage, name='login'),
    path('index/', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
    path('custom_password_reset/', views.custom_password_reset, name='custom_password_reset'),
    path('custom_password_reset_done/', views.custom_password_reset_done, name='custom_password_reset_done'),
    path('custom_password_reset_confirm/<uidb64>/<token>/', views.custom_password_reset_confirm, name='custom_password_reset_confirm'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('emergency/', views.emergency_view, name='emergency'),

# admin side start
    path('api/district-bookings/', views.district_bookings, name='district_bookings'),
    path('api/monthly-bookings/<int:year>/', views.monthly_bookings, name='monthly_bookings'),
    path('api/district-bookings/', views.district_bookings, name='district_bookings'),
    path('dashboard/', views.DashboardPage, name='dashboard'),
    path('monthly_bookings/<int:year>/', views.monthly_bookings, name='monthly_bookings'),
    path('full_users/', views.Full_usersPage, name='full_users'),
    path('full_customers/', views.Full_customersPage, name='full_customers'),
    path('full_workers/', views.Full_workersPage, name='full_workers'),
    path('manage_customers/', views.Manage_Customers, name='manage_customers'),
    path('change_status/<int:user_id>/', views.change_status, name='change_status'),
    path('manage_house_maids/', views.manage_house_maids, name='manage_house_maids'),
    path('edit_house_maid/<int:maid_id>/', views.edit_house_maid, name='edit_house_maid'),
    path('manage_home_nurses/', views.manage_home_nurses, name='manage_home_nurses'),
    path('edit_home_nurse/<int:nurse_id>/', views.edit_home_nurse, name='edit_home_nurse'),
    path('manage_carpenters/', views.manage_carpenters, name='manage_carpenters'),
    path('edit_carpenter/<int:carpenter_id>/', views.edit_carpenter, name='edit_carpenter'),
    path('manage_plumbers/', views.manage_plumbers, name='manage_plumbers'),
    path('edit_plumber/<int:plumber_id>/', views.edit_plumber, name='edit_plumber'),
    path('manage_electricians/', views.manage_electrician, name='manage_electricians'),
    path('edit_electrician/<int:electrician_id>/', views.edit_electrician, name='edit_electrician'),
    path('new-bookings/', views.new_bookings, name='new_bookings'),
    path('change-booking-status/<int:booking_id>/', views.change_booking_status, name='change_booking_status'),
    path('add_plumber/', views.add_plumber, name='add_plumber'),
    path('add_carpenter/', views.add_carpenter, name='add_carpenter'),
    path('add_electrician/', views.add_electrician, name='add_electrician'),
    path('add_home_nurse/', views.add_home_nurse, name='add_home_nurse'),
    path('add_house_maid/', views.add_house_maid, name='add_house_maid'),
    path('new_chat/', views.admin_new_chat, name='admin_new_chat'),
    path('view-chat/<int:user_id>/', views.admin_view_chat, name='admin_view_chat'),
    path('check_user_status/', views.check_user_status, name='check_user_status'),
    path('adm_send_message/<int:user_id>/', views.adm_send_message, name='adm_send_message'),
    path('report-generation/', views.report_generation, name='report_generation'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('download_report/', views.download_report, name='download_report'),

# admin side end

#customer side start  

    path('update_profile/', views.update_profile, name='update_profile'),
    path('view_maids/', views.view_maids, name='view_maids'),
    path('view_plumbers/', views.view_plumbers, name='view_plumbers'),
    path('view_carpenters/', views.view_carpenters, name='view_carpenters'),
    path('view_electricians/', views.view_electricians, name='view_electricians'),
    path('view_nurses/', views.view_nurses, name='view_nurses'),
    path('view_bookings/', views.view_bookings, name='view_bookings'),
    path('book_service/<int:maid_id>/', views.book_service, name='book_service'),
    path('book_nurse/<int:nurse_id>/', views.book_home_nurse, name='book_nurse'),
    path('book-carpenter/<int:carpenter_id>/', views.book_carpenter, name='book_carpenter'),
    path('book_electrician/<int:electrician_id>/', views.book_electrician, name='book_electrician'),
    path('book_plumber/<int:plumber_id>/', views.book_plumber, name='book_plumber'),
    path('services/', views.view_services, name='services'),
    path('profile/', views.customer_profile, name='profile'),
    path('email-search/', views.emailsearch, name='emailsearch'),
    path('users-email-search/', views.usersemailsearch, name='useremailsearch'),
    path('search-book-status/', views.searchbookstatus, name='searchbookstatus'),
    path('update_booking_status/', views.update_booking_status, name='update_booking_status'),
    path('check_booking_updates/', views.check_booking_updates, name='check_booking_updates'),
   
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/', views.get_messages, name='get_messages'),
    

    path('create-payment/<int:booking_id>/', views.create_payment, name='create_payment'),
    # path('verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment_page/<str:payment_id>/', views.payment_page, name='payment_page'),
    path('submit_rating/', views.submit_rating, name='submit_rating'),
    path('download_invoice/<int:booking_id>/', views.download_invoice, name='download_invoice'),
#customer side end

#worker side start

    path('worker_index/', views.worker_index, name='worker_index'),
    path('worker/profile/', views.worker_profile, name='worker_profile'),
    path('worker/bookings/', views.view_my_booking, name='view_my_booking'),
    path('verification/', views.worker_verification, name='worker_verification'),
    path('view-verification/', views.view_verification, name='view_verification'),
    path('update_worker_booking_status/', views.update_worker_booking_status, name='update_worker_booking_status'),

#worker side end

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)