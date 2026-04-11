from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):

    username = None  # remove username completely
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class StudentProfile(models.Model):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    PROGRAM_CHOICES = (
        ('BTech', 'BTech'),
        ('MTech', 'MTech'),
        ('MCA', 'MCA'),
        ('BCA', 'BCA'),
    )

    BRANCH_CHOICES = (
        ('CSE', 'CSE'),
        ('Mech', 'Mech'),
        ('ECE', 'ECE'),
        ('EEE', 'EEE'),
        ('IT', 'IT'),
        ('CE', 'CE'),
    )

    

    YEAR_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()

    mobile = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12)

    house_name = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    state = models.CharField(max_length=100) 

   
    program = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    branch = models.CharField(max_length=100, choices=BRANCH_CHOICES)
    institution = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Grievance(models.Model):

    LEVEL_CHOICES = (
        ('college', 'College'),
        ('university', 'University'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='account_grievances'   # ✅ ADD THIS
    )

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    main_category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=50, default="Pending")
    votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.main_category} - {self.level}"


class OTP(models.Model):
    """Model to store OTP codes for email verification"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.email}"

