from django.shortcuts import render

# Create your views here.
def buy_coins(request):
    return render(request, "payment/buy_coins.html")


def purchase(request):
    return render(request, "payment/purchase.html")
