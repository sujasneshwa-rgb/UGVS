from django.contrib import admin, messages
from .models import Grievance, ResolvedGrievance

class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('main_category','level','institution','votes','status')
    ordering = ('-votes',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Show only active and rejected grievances in main list.
        return queryset.exclude(status="Resolved")

    def get_readonly_fields(self, request, obj=None):
        field_names = [f.name for f in Grievance._meta.fields]
        # For closed grievances, status is also read-only.
        if obj and obj.status in {"Resolved", "Rejected"}:
            return field_names
        # Otherwise, allow admin to change only `status`.
        return [name for name in field_names if name != "status"]

    def save_model(self, request, obj, form, change):
        # Backend safety: do not allow status change once resolved/rejected.
        if change:
            old_obj = Grievance.objects.get(pk=obj.pk)
            if old_obj.status in {"Resolved", "Rejected"} and obj.status != old_obj.status:
                messages.error(
                    request,
                    f"Status cannot be changed once grievance is {old_obj.status}."
                )
                return
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return getattr(request.user, "role", None) == "admin"

admin.site.register(Grievance, GrievanceAdmin)


@admin.register(ResolvedGrievance)
class ResolvedGrievanceAdmin(GrievanceAdmin):
    def get_queryset(self, request):
        # Bypass parent filter that hides resolved grievances.
        queryset = admin.ModelAdmin.get_queryset(self, request)
        return queryset.filter(status="Resolved")

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in Grievance._meta.fields]
