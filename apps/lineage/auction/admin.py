from django.contrib import admin
from .models import Auction, Bid
from core.admin import BaseModelAdmin


@admin.register(Auction)
class AuctionAdmin(BaseModelAdmin):
    list_display = ('item_name', 'seller', 'starting_bid', 'current_bid', 'highest_bidder', 'end_time', 'is_active')
    list_filter = ('seller', 'end_time')
    search_fields = ('item_name', 'seller__username', 'highest_bidder__username')  # Usando item_name diretamente
    readonly_fields = ('current_bid', 'highest_bidder')
    
    def is_active(self, obj):
        from django.utils import timezone
        return obj.end_time > timezone.now()
    is_active.boolean = True
    is_active.short_description = "Ativo"


@admin.register(Bid)
class BidAdmin(BaseModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'created_at')
    list_filter = ('bidder', 'created_at')
    search_fields = ('auction__item_name', 'bidder__username')  # Usando item_name diretamente
