from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SocialMediaAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=100, help_text='ex. facebook')
    total_follower = models.IntegerField(default=0, help_text='foolowers or subscribers etc.')
    account_link = models.URLField()

    def __str__(self):
        return f'{self.user.first_name} - {self.platform} - {self.total_follower}'
    
class Creator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number= models.CharField(max_length=25, help_text='whatsapp phone number written in international format withou plus sign ex. 254740562740')
    total_followers = models.IntegerField(default=0, help_text='accross all your social platforms')
    total_points = models.IntegerField(default=0)
    brief_bio = models.TextField(blank=True)
    type_of_content = models.TextField(blank=True)
    social_media_accounts = models.ManyToManyField(SocialMediaAccount, blank=True)
    reffered_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='refferal')
    date_joined = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'{self.user.first_name} {self.total_followers}'