from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback'),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<int:user_id>/', views.resend_otp, name='resend_otp'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-verify/', views.password_reset_verify, name='password_reset_verify'),
    path('resend-reset-otp/', views.resend_reset_otp, name='resend_reset_otp'),
    path("verify-reset-otp/", views.verify_reset_otp, name="verify_reset_otp"),

]

