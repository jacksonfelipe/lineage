from django.shortcuts import render
from .models import FAQ
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required


@login_required
def faq_list(request):
    private_faqs = FAQ.objects.filter(is_public=False)
    context = {
        'segment': 'index',
        'parent': 'faq',
        'private_faqs': private_faqs
    }
    return render(request, 'pages/faq.html', context)
