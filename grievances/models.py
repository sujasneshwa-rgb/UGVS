from django.db import models
from django.conf import settings
from .utils import send_grievance_email


class Grievance(models.Model):

    LEVEL_CHOICES = (
        ('college', 'College'),
        ('university', 'University'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grievances'
    )

    main_category = models.CharField(max_length=255)
    sub_category = models.CharField(max_length=255)
    description = models.TextField()

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    institution = models.CharField(max_length=255)

    evidence = models.FileField(upload_to='evidence/', blank=True, null=True)

    votes = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-votes']

    def __str__(self):
        return f"{self.main_category} ({self.level})"


    # ===============================
    # 🔥 EMAIL TRIGGER (SAFE VERSION)
    # ===============================
    def save(self, *args, **kwargs):

        send_email = False
        subject = None
        message = None

        # Check if updating existing record
        if self.pk:
            old = Grievance.objects.get(pk=self.pk)

            # Trigger only if status changed
            if old.status != self.status:

                send_email = True

                if self.status == "In Progress":
                    subject = "Your Grievance is Under Process"

                    message = f"""Dear Student,

Your grievance is now being processed by the concerned authority.

Details:
- Level: {self.level}
- Category: {self.main_category}
- Subcategory: {self.sub_category}
- Description: {self.description}

Necessary actions are being taken.

Thank you.
"""

                elif self.status == "Resolved":
                    subject = "Grievance Resolved"

                    message = f"""Dear Student,

Your grievance has been successfully resolved.

Details:
- Level: {self.level}
- Category: {self.main_category}
- Subcategory: {self.sub_category}
- Description: {self.description}

The issue has been addressed.

Thank you.
"""

                elif self.status == "Rejected":
                    subject = "Grievance Rejected"

                    message = f"""Dear Student,

Your grievance has been rejected.

Details:
- Level: {self.level}
- Category: {self.main_category}
- Subcategory: {self.sub_category}
- Description: {self.description}

Reason: Invalid or inappropriate grievance.

Thank you.
"""

        # ✅ FIRST save to database
        super().save(*args, **kwargs)

        # ✅ THEN send email (prevents DB lock)
        if send_email and subject:
            try:
                send_grievance_email(
                    self.student.email,
                    subject,
                    message
                )
            except Exception as e:
                print("Email sending failed:", e)


class Vote(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE
    )

    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'grievance')

    def __str__(self):
        return f"{self.user.email} voted for {self.grievance.main_category}"


class ResolvedGrievance(Grievance):
    class Meta:
        proxy = True
        verbose_name = "Resolved Grievance"
        verbose_name_plural = "Resolved Grievances"