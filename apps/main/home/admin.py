from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import *
from core.admin import BaseModelAdmin, BaseModelAdminAbstratic


class UserAdmin(BaseModelAdmin, DefaultUserAdmin):
    list_display = ('username', 'email', 'display_groups', 'cpf', 'gender', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'uuid')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'uuid')}),
        ('Informações pessoais', {'fields': ('avatar', 'bio', 'cpf', 'gender')}),  # Adicionei o campo gender
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'created_at', 'updated_at', 'created_by', 'updated_by')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'avatar', 'bio', 'cpf', 'gender'),  # Adicionei o campo gender
        }),
    )

    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    display_groups.short_description = "Grupos"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        js = (
            'js/mask-cpf.js',
        )


class AddressAdmin(BaseModelAdmin):
    list_display = ('user', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code')
    search_fields = ('user__username', 'street', 'city', 'state', 'postal_code', 'neighborhood')
    list_filter = ('state', 'neighborhood')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
    

class StateAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'abbreviation')  # Campos a serem exibidos na lista
    search_fields = ('name', 'abbreviation')  # Campos que podem ser pesquisados
    ordering = ('name',)  # Ordenação padrão
    list_filter = ('abbreviation',)  # Filtro para a lista


class CityAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'state')  # Campos a serem exibidos na lista
    search_fields = ('name',)  # Campos que podem ser pesquisados
    ordering = ('name',)  # Ordenação padrão
    list_filter = ('state',)  # Filtro para a lista


admin.site.register(User, UserAdmin)
admin.site.register(AddressUser, AddressAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
