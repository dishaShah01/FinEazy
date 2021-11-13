from django.db import models
from django.contrib.auth.models import User,AbstractUser


class Stocks(models.Model):
    user = models.ForeignKey(User, default='', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dob = models.DateField(auto_now_add=True)
    total_coins_bought = models.PositiveIntegerField()
    total_money_invested = models.PositiveIntegerField()
    total_money_now = models.PositiveIntegerField()

#class Profile(models.Model):
    #user = models.OneToOneField(User,default='', on_delete=models.CASCADE)

