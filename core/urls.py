from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # main app start
    path('', include('apps.main.home.urls')),
    
    # apps native
    path('app/message/', include('apps.main.message.urls')),
    path('app/administrator/', include('apps.main.administrator.urls')),
    path('app/news/', include('apps.main.news.urls')),
    path('app/faq/', include('apps.main.faq.urls')),
    path('app/auditor/', include('apps.main.auditor.urls')),
    path('app/notifications/', include('apps.main.notification.urls')),
    path('app/solicitation/', include('apps.main.solicitation.urls')),

    # apps lineage
    path('app/wallet/', include('apps.lineage.wallet.urls')),
    path('app/payment/', include('apps.lineage.payment.urls')),
    path('app/server/', include('apps.lineage.server.urls')),
    path('app/accountancy/', include('apps.lineage.accountancy.urls')),

    # libs externals
    path('', include('serve_files.urls')),
    path('', include('admin_volt.urls')),

    # libs core's
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Static/media routes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'apps.main.home.views.custom_400_view'
handler404 = 'apps.main.home.views.custom_404_view'
handler500 = 'apps.main.home.views.custom_500_view'
