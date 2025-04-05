"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include('apps.main.home.urls')),
    path('', include('apps.main.message.urls')),
    
    path('app/news/', include('apps.main.news.urls')),
    path('app/faq/', include('apps.main.faq.urls')),
    path("app/auditor/", include('apps.main.auditor.urls', namespace='auditor')),
    path("app/notifications/", include('apps.main.notification.urls')),

    path("", include('serve_files.urls')),
    path("", include('admin_volt.urls')),

    path("admin/", admin.site.urls),
]

# Static/media routes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'apps.main.home.views.custom_400_view'
handler404 = 'apps.main.home.views.custom_404_view'
handler500 = 'apps.main.home.views.custom_500_view'
