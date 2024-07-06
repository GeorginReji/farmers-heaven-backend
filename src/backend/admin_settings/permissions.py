from ..base.api.permissions import (AllowAny, IsAuthenticated, PermissionComponent, ResourcePermission, IsSuperUser,
                                    AllOnlyGetPerm, AllowAnyGetPerm)


class IsTheSameUser(PermissionComponent):
    def has_permission(self, request, view):
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj=None):
        return request.user.is_authenticated() and request.user.pk == obj.pk


class DynamicSettingsPermissions(ResourcePermission):
    metadata_perms = AllowAny()
    enough_perms = None
    global_perms = None
    retrieve_perms = IsSuperUser() | IsAuthenticated()
    create_perms = IsSuperUser()
    update_perms = IsSuperUser()
    partial_update_perms = IsSuperUser()
    destroy_perms = IsSuperUser()
    list_perms = IsSuperUser() | IsAuthenticated() | AllOnlyGetPerm()
    dropdown_perms = IsSuperUser() | AllOnlyGetPerm()
    country_perms = IsSuperUser() | AllOnlyGetPerm() | AllowAnyGetPerm()
    state_perms = IsSuperUser() | AllOnlyGetPerm() | AllowAnyGetPerm()
    city_perms = IsSuperUser() | AllOnlyGetPerm() | AllowAnyGetPerm()
    products_perms = IsSuperUser() | AllowAnyGetPerm()


class UploadedDocumentPermissions(ResourcePermission):
    metadata_perms = AllowAny()
    enough_perms = None
    global_perms = None
    retrieve_perms = AllowAny()
    create_perms = AllowAny()
    update_perms = IsSuperUser()
    partial_update_perms = IsSuperUser()
    destroy_perms = IsSuperUser()
    list_perms = AllowAny()
    create_with_base64_perms = AllowAny()
    multiple_perms = AllowAny()
    presigned_url_perms = AllowAny()
    onboard_presigned_url_perms = AllowAny()
    download_file_perms = AllowAny()
