from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, StudentProfile, Feedback, Grievance


# ===============================
# 🔒 READ-ONLY USER ADMIN
# ===============================

class ReadOnlyUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'role', 'is_verified', 'is_staff')
    ordering = ('email',)
    search_fields = ('email',)

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return getattr(request.user, "role", None) == "admin"

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return None


# ===============================
# 🔒 READ-ONLY STUDENT PROFILE
# ===============================

class ReadOnlyStudentProfileAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return None


# ===============================
# 🔒 READ-ONLY GRIEVANCE
# ===============================

class ReadOnlyGrievanceAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in Grievance._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return None



# ===============================
# REGISTER MODELS
# ===============================

admin.site.register(CustomUser, ReadOnlyUserAdmin)
admin.site.register(StudentProfile, ReadOnlyStudentProfileAdmin)
#admin.site.register(Grievance, ReadOnlyGrievanceAdmin)
#admin.site.register(Feedback)


