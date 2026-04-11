from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Grievance, Vote
from .utils import send_grievance_email
from django.db.models import F


# ===============================
# COLLEGE LEVEL
# ===============================
@login_required
def college_level(request):

    institution = request.user.studentprofile.institution

    grievances = Grievance.objects.filter(
        level='college',
        institution=institution,
        status__in=["Pending", "In Progress"]
    ).order_by('-votes')

    return render(request, 'college.html', {'grievances': grievances})


# ===============================
# UNIVERSITY LEVEL
# ===============================
@login_required
def university_level(request):

    grievances = Grievance.objects.filter(
        level='university',
        status__in=["Pending", "In Progress"]
    ).order_by('-votes')

    return render(request, 'university.html', {
        'grievances': grievances
    })


# ===============================
# ADD GRIEVANCE
# ===============================
@login_required
def add_grievance(request, level):

    if request.method == "POST":

        main_category = request.POST.get('main_category')
        sub_category = request.POST.get('sub_category')
        description = request.POST.get('description')

        grievance = Grievance.objects.create(
            student=request.user,   # ✅ FIXED (was user)
            level=level,
            main_category=main_category,
            sub_category=sub_category,
            description=description,
            institution=request.user.studentprofile.institution  # ensure college saved
        )
        
        #messages.success(request, "Grievance Submitted Successfully")

        message = f"""
        Dear Student,

        Your grievance has been successfully submitted.

        Details:
        - Level: {grievance.level}
        - Category: {grievance.main_category}
        - Subcategory: {grievance.sub_category}
        - Description: {grievance.description}

        Current Status: Pending

        Your grievance is now under review.

        Thank you.
        """

        send_grievance_email(
            request.user.email,
            "Grievance Submitted Successfully",
            message
        )
        return redirect(level)

    return render(request, 'add_grievance.html', {'level': level})


# ===============================
# STATUS VIEW (USER'S OWN)
# ===============================
@login_required
def status_view(request, level):

    grievances = Grievance.objects.filter(
        student=request.user,   # ✅ correct field
        level=level
    ).order_by('-votes')

    return render(request, 'status.html', {'grievances': grievances})


# ===============================
# VOTE (SECURE)
# ===============================
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def vote(request, grievance_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    grievance = get_object_or_404(Grievance, id=grievance_id)
    student_institution = request.user.studentprofile.institution.strip().lower()

    # College restriction: only students from same institution can vote.
    if grievance.level == "college":
        grievance_institution = (grievance.institution or "").strip().lower()
        if student_institution != grievance_institution:
            return JsonResponse({"error": "Not allowed"}, status=403)

    # Ensure each user can vote only once (safe against double-click/race).
    vote_obj, created = Vote.objects.get_or_create(
        user=request.user,
        grievance=grievance
    )

    if not created:
        return JsonResponse({
            "status": "already_voted",
            "votes": grievance.votes
        })

    Grievance.objects.filter(id=grievance.id).update(votes=F('votes') + 1)
    grievance.refresh_from_db(fields=["votes"])

    return JsonResponse({
        "status": "voted",
        "votes": grievance.votes
    })



@login_required
def vote_college(request):
    institution = request.user.studentprofile.institution.strip()

    grievances = Grievance.objects.filter(
        level='college',
        institution__iexact=institution,
        status__in=["Pending", "In Progress"]
    ).order_by('-votes')

    voted_ids = Vote.objects.filter(user=request.user)\
                             .values_list('grievance_id', flat=True)

    return render(request, 'vote_college.html', {
        'grievances': grievances,
        'voted_ids': voted_ids
    })




@login_required
def vote_university(request):

    grievances = Grievance.objects.filter(
        level='university',
        status__in=["Pending", "In Progress"]
    ).order_by('-votes')

    voted_ids = Vote.objects.filter(user=request.user)\
                             .values_list('grievance_id', flat=True)

    return render(request, 'vote_university.html', {
        'grievances': grievances,
        'voted_ids': voted_ids
    })


from django.shortcuts import render
from django.db.models import Max
from .models import Grievance


@login_required
def admin_grievance_list(request):
    if getattr(request.user, "role", None) != "admin":
        return redirect("dashboard")
    grievances = Grievance.objects.exclude(
        status__in=["Resolved", "Rejected"]
    ).order_by('-votes')

    highest_vote = grievances.aggregate(Max('votes'))['votes__max']

    return render(request, 'admin_grievances.html', {
        'grievances': grievances,
        'highest_vote': highest_vote
    })


@login_required
def admin_resolved_grievances(request):
    if getattr(request.user, "role", None) != "admin":
        return redirect("dashboard")

    grievances = Grievance.objects.filter(status="Resolved").order_by('-votes')

    return render(request, 'admin_resolved_grievances.html', {
        'grievances': grievances
    })


@login_required
def admin_rejected_grievances(request):
    if getattr(request.user, "role", None) != "admin":
        return redirect("dashboard")

    grievances = Grievance.objects.filter(status="Rejected").order_by('-votes')

    return render(request, 'admin_rejected_grievances.html', {
        'grievances': grievances
    })


@login_required
def resolved_college(request):
    institution = request.user.studentprofile.institution

    grievances = Grievance.objects.filter(
        level='college',
        institution=institution,
        status="Resolved"
    ).order_by('-votes')

    return render(request, 'resolved_college.html', {
        'grievances': grievances
    })


@login_required
def resolved_university(request):
    grievances = Grievance.objects.filter(
        level='university',
        status="Resolved"
    ).order_by('-votes')

    return render(request, 'resolved_university.html', {
        'grievances': grievances
    })

@login_required
def update_status(request, grievance_id, new_status):
    if getattr(request.user, "role", None) != "admin":
        return redirect("dashboard")

    grievance = get_object_or_404(Grievance, id=grievance_id)
    allowed_statuses = {"Pending", "In Progress", "Resolved", "Rejected"}

    if new_status not in allowed_statuses:
        messages.error(request, "Invalid status selected.")
        return redirect('admin_grievances')

    # Once resolved, it is final and cannot be changed to any other status.
    if grievance.status == "Resolved" and new_status != "Resolved":
        messages.error(request, "Resolved grievance status cannot be changed.")
        return redirect('admin_grievances')

    # Once rejected, it is final and cannot be changed to any other status.
    if grievance.status == "Rejected" and new_status != "Rejected":
        messages.error(
            request,
            "Rejected grievance status cannot be changed."
        )
        return redirect('admin_grievances')

    # Update status
    grievance.status = new_status
    grievance.save()
    messages.success(request, f"Status updated to {new_status}.")

    return redirect('admin_grievances')