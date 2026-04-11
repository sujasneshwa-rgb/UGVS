from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import random
import re

from .models import CustomUser, StudentProfile, Feedback


# ===============================
# HOME
# ===============================
def home(request):
    return render(request, "home.html")


# ===============================
# REGISTER (USER CREATED AFTER OTP)
# ===============================
def register(request):
    errors = {}

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        mobile = request.POST.get('mobile')
        aadhaar = request.POST.get('aadhaar')
        house_name = request.POST.get('house_name')
        place = request.POST.get('place')
        district = request.POST.get('district')
        pin_code = request.POST.get('pin_code')
        state = request.POST.get('state')
        program = request.POST.get('program')
        year = request.POST.get('year')
        branch = request.POST.get('branch')
        institution = request.POST.get('institution')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Email format validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            errors['email'] = "Enter a valid email address."
        
        
        # Block only verified emails
        existing_user = CustomUser.objects.filter(email=email, is_verified=True).first()
        if existing_user:
            errors['email'] = "Email already exists."

        if password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."


        password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(password_pattern, password):
            errors['password'] = "Password must contain at least 8 characters, 1 capital letter, 1 number and 1 special character."


        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            errors['mobile'] = "Mobile number must be exactly 10 digits."

        if not aadhaar or not aadhaar.isdigit() or len(aadhaar) != 12:
            errors['aadhaar'] = "Aadhaar number must be exactly 12 digits."

        if errors:
            return render(request, "register.html", {
                'errors': errors,
                'form_data': request.POST
            })

        # Generate OTP (user not created yet)
        otp_code = str(random.randint(100000, 999999))

        # Store all data temporarily in session
        request.session['temp_user'] = {
            'name': name,
            'email': email,
            'password': password,
            'gender': gender,
            'dob': dob,
            'mobile': mobile,
            'aadhaar': aadhaar,
            'house_name': house_name,
            'place': place,
            'district': district,
            'pin_code': pin_code,
            'state': state,
            'program': program,
            'year': year,
            'branch': branch,
            'institution': institution,
            'otp': otp_code,
            'otp_time': timezone.now().timestamp()
        }

        # Send OTP email
        send_mail(
            'Email Verification OTP - UGVS',
            f'Your OTP is {otp_code}',
            None,
            [email],
            fail_silently=False,
        )

        print("OTP SENT:", otp_code)

        return redirect('verify_otp', user_id=0)

    return render(request, "register.html", {'errors': {}, 'form_data': {}})


# ===============================
# VERIFY OTP (USER CREATED HERE)
# ===============================
def verify_otp(request, user_id):
    temp_user = request.session.get('temp_user')

    if not temp_user:
        #messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    if request.method == "POST":
        entered_otp = request.POST.get('otp')

        if entered_otp == temp_user['otp']:

            # 🔐 SAFETY CHECK (prevents UNIQUE constraint crash)
            existing_user = CustomUser.objects.filter(email=temp_user['email']).first()

            if existing_user:
                user = existing_user
                user.is_verified = True
                user.save()
            else:
                user = CustomUser.objects.create_user(
                    email=temp_user['email'],
                    password=temp_user['password'],
                    role='student',
                    is_verified=True
                )

                StudentProfile.objects.create(
                    user=user,
                    name=temp_user['name'],
                    gender=temp_user['gender'],
                    dob=temp_user['dob'],
                    mobile=temp_user['mobile'],
                    aadhaar=temp_user['aadhaar'],
                    house_name=temp_user['house_name'],
                    place=temp_user['place'],
                    district=temp_user['district'],
                    pin_code=temp_user['pin_code'],
                    state=temp_user['state'],
                    program=temp_user['program'],
                    year=temp_user['year'],
                    branch=temp_user['branch'],
                    institution=temp_user['institution']
                )

            # clear session
            del request.session['temp_user']

            # messages.success(request, "Email verified! Registration complete.")
            return redirect("login")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "verify.html")


# ===============================
# RESEND OTP
# ===============================
def resend_otp(request, user_id):
    temp_user = request.session.get('temp_user')

    if not temp_user:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    otp_code = str(random.randint(100000, 999999))
    temp_user['otp'] = otp_code
    request.session['temp_user'] = temp_user

    send_mail(
        'New OTP - UGVS',
        f'Your new OTP is {otp_code}',
        None,
        [temp_user['email']],
        fail_silently=False,
    )

    messages.success(request, "New OTP sent to your email.")
    return redirect('verify_otp', user_id=0)


# ===============================
# LOGIN
# ===============================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_verified:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect('verify_otp', user_id=0)

            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


# ===============================
# DASHBOARD
# ===============================
def dashboard(request):
    return render(request, "dashboard.html")


# ===============================
# LOGOUT
# ===============================
def logout_view(request):
    logout(request)
    return redirect("home")


# ===============================
# ABOUT
# ===============================
def about(request):
    return render(request, "about.html")


# ===============================
# FEEDBACK
# ===============================
def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_text = request.POST.get("message")

        if name and email and message_text:
            Feedback.objects.create(
                name=name,
                email=email,
                message=message_text
            )

        return render(request, "feedback.html")

    return render(request, "feedback.html")


# ===============================
# PROFILE
# ===============================
@login_required
def profile_view(request):
    # Only students should view student profile pages.
    if getattr(request.user, "role", None) != "student":
        return redirect("dashboard")
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    # Restrict profile editing to the logged-in student only.
    if getattr(request.user, "role", None) != "student":
        return redirect("dashboard")
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.name = request.POST.get("name")
        profile.dob = request.POST.get("dob")
        profile.gender = request.POST.get("gender")
        profile.mobile = request.POST.get("mobile")
        profile.aadhaar = request.POST.get("aadhaar")
        profile.house_name = request.POST.get("house_name")
        profile.place = request.POST.get("place")
        profile.district = request.POST.get("district")
        profile.pin_code = request.POST.get("pin_code")
        profile.state = request.POST.get("state")
        profile.program = request.POST.get("program")
        profile.year = request.POST.get("year")
        profile.branch = request.POST.get("branch")
        profile.institution = request.POST.get("institution")

        profile.save()
        return redirect("profile")

    return render(request, "edit_profile.html", {"profile": profile})


# ===============================
# PASSWORD RESET - STEP 1 (SEND OTP)
# ===============================
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not registered.")
            return render(request, "password_reset.html")

        otp_code = str(random.randint(100000, 999999))

        request.session['reset_data'] = {
            'email': email,
            'otp': otp_code
        }
        
        # ===============================
# PASSWORD RESET - STEP 1 (SEND OTP)
# ===============================
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not registered.")
            return render(request, "password_reset.html")

        otp_code = str(random.randint(100000, 999999))

        request.session['reset_data'] = {
            'email': email,
            'otp': otp_code
        }
        
        request.session["otp_verified"] = False

        send_mail(
            'Password Reset OTP - UGVS',
            f'Your OTP for password reset is {otp_code}',
            None,
            [email],
            fail_silently=False,
        )

        return redirect("password_reset_verify")

    return render(request, "password_reset_request.html")
        
    

# ===============================
# PASSWORD RESET - STEP 2 (VERIFY OTP)
# ===============================
def password_reset_verify(request):
    reset_data = request.session.get('reset_data')

    if not reset_data:
        messages.error(request, "Session expired. Try again.")
        return redirect("password_reset")

    if request.method == "POST":

        # ✅ ONLY CHECK THIS
        if not request.session.get("otp_verified"):
            messages.error(request, "Please verify OTP first.")
            return render(request, "password_reset_verify.html")

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "password_reset_verify.html")

        user = CustomUser.objects.get(email=reset_data['email'])
        user.set_password(new_password)
        user.save()

        # cleanup
        del request.session['reset_data']
        request.session.pop("otp_verified", None)

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "password_reset_verify.html")


# ===============================
# RESEND RESET OTP
# ===============================
def resend_reset_otp(request):

    reset_data = request.session.get('reset_data')

    if not reset_data:
        messages.error(request, "Session expired. Please start again.")
        return redirect("password_reset_request")

    otp_code = str(random.randint(100000, 999999))

    reset_data['otp'] = otp_code
    request.session['reset_data'] = reset_data
    
    request.session["otp_verified"] = False
    
    send_mail(
        'New Password Reset OTP - UGVS',
        f'Your new OTP is {otp_code}',
        None,
        [reset_data['email']],
        fail_silently=False,
    )

    messages.success(request, "New OTP sent to your email.")

    return redirect("password_reset_verify")



def verify_reset_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        reset_data = request.session.get("reset_data")

        if not reset_data:
            return JsonResponse({"status": "expired"})

        if str(entered_otp) == str(reset_data["otp"]):
            request.session["otp_verified"] = True
            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "invalid"})
