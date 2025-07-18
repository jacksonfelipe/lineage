from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import License, LicenseVerification
from core.admin import BaseModelAdmin


@admin.register(License)
class LicenseAdmin(BaseModelAdmin):
    list_display = [
        'license_key_short', 'license_type', 'domain', 'company_name', 
        'status', 'activated_at', 'expires_at', 'verification_count'
    ]
    list_filter = ['license_type', 'status', 'activated_at', 'expires_at']
    search_fields = ['license_key', 'domain', 'company_name', 'contact_email']
    readonly_fields = [
        'license_key', 'verification_count', 'last_verification', 
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Informações da Licença'), {
            'fields': ('license_key', 'license_type', 'status')
        }),
        (_('Cliente'), {
            'fields': ('domain', 'company_name', 'contact_email', 'contact_phone')
        }),
        (_('Contrato (PDL PRO)'), {
            'fields': ('contract_number', 'support_hours_used', 'support_hours_limit'),
            'classes': ('collapse',)
        }),
        (_('Datas'), {
            'fields': ('activated_at', 'expires_at', 'last_verification'),
            'classes': ('collapse',)
        }),
        (_('Funcionalidades'), {
            'fields': ('features_enabled',),
            'classes': ('collapse',)
        }),
        (_('Estatísticas'), {
            'fields': ('verification_count',),
            'classes': ('collapse',)
        }),
        (_('Observações'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_licenses', 'deactivate_licenses', 'renew_licenses']
    
    def license_key_short(self, obj):
        """Exibe apenas os primeiros caracteres da chave de licença"""
        if obj.license_key:
            return obj.license_key[:12] + "..."
        return "-"
    license_key_short.short_description = _("Chave de Licença")
    
    def activate_licenses(self, request, queryset):
        """Ação para ativar licenças selecionadas"""
        count = 0
        for license in queryset:
            if license.status != 'active':
                license.activate(license.domain)
                count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) ativada(s) com sucesso."
        )
    activate_licenses.short_description = _("Ativar licenças selecionadas")
    
    def deactivate_licenses(self, request, queryset):
        """Ação para desativar licenças selecionadas"""
        count = 0
        for license in queryset:
            if license.status == 'active':
                license.deactivate()
                count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) desativada(s) com sucesso."
        )
    deactivate_licenses.short_description = _("Desativar licenças selecionadas")
    
    def renew_licenses(self, request, queryset):
        """Ação para renovar licenças selecionadas"""
        count = 0
        for license in queryset:
            license.renew(365)  # Renova por 1 ano
            count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) renovada(s) por 365 dias."
        )
    renew_licenses.short_description = _("Renovar licenças por 1 ano")


@admin.register(LicenseVerification)
class LicenseVerificationAdmin(BaseModelAdmin):
    list_display = [
        'license_domain', 'verification_date', 'ip_address', 
        'success', 'response_time'
    ]
    list_filter = ['success', 'verification_date', 'license__license_type']
    search_fields = ['license__domain', 'license__license_key', 'ip_address']
    readonly_fields = [
        'license', 'verification_date', 'ip_address', 'user_agent',
        'success', 'error_message', 'response_time'
    ]
    
    fieldsets = (
        (_('Licença'), {
            'fields': ('license',)
        }),
        (_('Verificação'), {
            'fields': ('verification_date', 'success', 'response_time')
        }),
        (_('Detalhes da Requisição'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Erro (se houver)'), {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def license_domain(self, obj):
        """Exibe o domínio da licença"""
        return obj.license.domain if obj.license else "-"
    license_domain.short_description = _("Domínio")
    
    def has_add_permission(self, request):
        """Não permite adicionar verificações manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Não permite editar verificações"""
        return False
