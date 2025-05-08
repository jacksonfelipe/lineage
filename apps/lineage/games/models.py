from django.db import models
from apps.main.home.models import User
from core.models import BaseModel
from django.templatetags.static import static


class Prize(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='prizes/', null=True, blank=True)
    weight = models.PositiveIntegerField(default=1, help_text="Quanto maior o peso, maior a chance de ser sorteado.")

    def get_image_url(self):
        return self.image.url if self.image else static("roulette/images/default.png")

    def __str__(self):
        return self.name


class SpinHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} won {self.prize.name}'
