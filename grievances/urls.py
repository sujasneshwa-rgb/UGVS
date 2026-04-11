from django.urls import path
from . import views

urlpatterns = [
    path('college/', views.college_level, name='college'),
    path('university/', views.university_level, name='university'),
    path('add-grievance/<str:level>/', views.add_grievance, name='add_grievance'),
    path('status/<str:level>/', views.status_view, name='status'),
    path('vote-college/', views.vote_college, name='vote_college'),
    path('vote-university/', views.vote_university, name='vote_university'),
    path('vote/<int:grievance_id>/', views.vote, name='vote'),
    path('admin-grievances/', views.admin_grievance_list, name='admin_grievances'),
    path('admin-resolved-grievances/', views.admin_resolved_grievances, name='admin_resolved_grievances'),
    path('admin-rejected-grievances/', views.admin_rejected_grievances, name='admin_rejected_grievances'),
    path('resolved/college/', views.resolved_college, name='resolved_college'),
    path('resolved/university/', views.resolved_university, name='resolved_university'),
    path('update-status/<int:grievance_id>/<str:new_status>/',
     views.update_status,
     name='update_status'),
]