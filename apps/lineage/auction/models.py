from django.db import models
from apps.main.home.models import User
from core.models import BaseModel
from apps.lineage.inventory.models import InventoryItem


class Auction(BaseModel):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='auctions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bids')
    end_time = models.DateTimeField()

    def is_active(self):
        from django.utils import timezone
        return self.end_time > timezone.now()

    def __str__(self):
        return f"Auction of {self.item.item_name} by {self.seller.username}"


class Bid(BaseModel):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.auction.item.item_name}"
