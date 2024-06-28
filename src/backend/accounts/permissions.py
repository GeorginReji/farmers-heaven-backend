from ..base.api.permissions import (AllowAny, PermissionComponent, ResourcePermission, IsSuperUser)


class IsTheSameUser(PermissionComponent):
    def has_permission(self, request, view):
        if not request.user.pk:
            return False
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj=None):
        if not request.user.pk:
            return False
        return request.user.is_authenticated() and request.user.pk == obj.pk


class UserPermissions(ResourcePermission):
    metadata_perms = AllowAny()
    enough_perms = None
    global_perms = None
    retrieve_perms = IsSuperUser()
    create_perms = IsSuperUser()
    update_perms = IsSuperUser()
    partial_update_perms = IsSuperUser()
    destroy_perms = IsSuperUser()
    list_perms = IsSuperUser()
    oauth_start_perms = AllowAny()
    oauth_callback_perms = AllowAny()
    login_perms = AllowAny()
    customer_login_perms = AllowAny()
    correct_perms = AllowAny()
    user_clone_perms = AllowAny()
    password_change_perms = AllowAny()
    user_reset_mail_perms = AllowAny()
    reset_password_perms = AllowAny()
    send_otp_perms = AllowAny()
    resend_otp_perms = AllowAny()
    verify_otp_perms = AllowAny()
