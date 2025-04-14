from django.db import models
from tinymce.models import HTMLField
from django.utils.timezone import now
from datetime import datetime, date , timedelta
from django.contrib.auth.models import User
from creators.models import SocialMediaAccount, Creator
import uuid

# Create your models here.
class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=250, unique=True)
    slug = models.CharField(max_length=250, unique=True)
    phone_number = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    address = models.TextField(max_length=1000)
    description = models.TextField(blank=True, help_text='describe what you do')
    social_media_accounts = models.ManyToManyField(SocialMediaAccount, blank=True)
    subscription_plan = models.CharField(max_length=250, blank=True)
    reffered_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='business_refferal')
    date_joined = models.DateTimeField(auto_now_add = True)


    def __str__(self):
        return self.business_name
    
class  Staff(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='staff')
    business = models.ForeignKey(Business, on_delete= models.CASCADE, related_name='staff')
    date_joined = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'{self.user.first_name} - {self.business.business_name}'

class ContentCreationJob(models.Model): 
    JOB_TYPE_CHOICES= {
    'photo shooting' : 'photo shooting',
    'video creation' : 'video creation',
    'livestreaming'  : 'livestreaming',
    'photo shooting, video creation, livestreaming': 'photo shooting, video creation, livestreaming'
    }
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='jobs')
    job_type = models.CharField(max_length=150, choices=JOB_TYPE_CHOICES)
    job_description =  HTMLField(blank=True)
    monthly_pay = models.IntegerField(default=10000)
    number_of_creators = models.IntegerField(default=4, help_text="number of creators you target to hire")
    creators = models.ManyToManyField(Creator, blank=True)
    position_filled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.business.business_name}  {self.job_type}'

class JobApplication(models.Model):
    job = models.ForeignKey(ContentCreationJob,  on_delete=models.CASCADE, related_name="job_applications")
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    accepted_by_business = models.BooleanField(default=False)
    accepted_by_creator = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.business.business_name}  {self.job_type} {self.creator}'

class Challenge(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='challenges')
    challenge_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=(('challenge', 'challenge'), ('view reward program', 'view reward program')))
    video_url = models.URLField(blank=True, null=True, help_text='if you have video you want creators to recreate their videos from')
    description = models.TextField(blank=True)
    budget = models.IntegerField(default=0)
    challenge_reward = models.IntegerField(default=0, help_text='whats the reward for the challenge')
    target_winners = models.IntegerField(default=7, help_text='how many winners do you want for this challenge')
    pay_per_1000_views = models.IntegerField(default=0, help_text='how much are you paying for 100 views')
    maximum_payout_per_creator =  models.IntegerField(default=0, help_text='setting maximum payout for view reward program helps pay ceators to a certain number of view after which extra views you wont pay for')
    last_day_of_the_challenge = models.DateField(auto_now_add=True)
    participants = models.ManyToManyField(Creator, blank=True, related_name='participants')
    winners = models.ManyToManyField(Creator, blank=True, related_name='winners')
    rules = models.TextField(blank=True)
    instant_reward = models.CharField(max_length=100, blank=True, null=True, help_text="it's the reward you give creator immediately after participating")
    closed = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.challenge_name


class LoyaltyPointsCategory(models.Model):
    category = models.CharField(max_length=100, choices=(('points on purchases made', 'points on purchases made'), ('points on visiting the store', 'points on visiting the store'), ('points on refferal sales', 'points on refferal sales'), ('points on bringing friends to the store', 'points on bringing friends to the store')))
    total_views_for_a_point = models.IntegerField(default=100, help_text=" for purchase made what purchase value equals a point, for visits how many visits eaquals apoint, for refferal sales whats sales value equals a point, and for friends brought to the store how many friends equals a point")
    redemed_at_how_much_per_point = models.FloatField(default=1)
    edited_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.category

class ChallengeResult(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    video_url = models.URLField()
    total_views = models.IntegerField(default=0)
    points_category = models.ForeignKey(LoyaltyPointsCategory, blank=True, null=True, on_delete=models.SET_NULL)
    points_earned = models.IntegerField(default=0)
    added_by = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.creator.user.first_name} {self.creator.user.last_name} points earned: {self.points_earned}'

    
class LoyaltyPointForLogginIn(models.Model): 
    # we award creators 10 points for logging into their accopunt daily, 
    # so we are using this model to track if creators has already been awarded points
    creator = models.ForeignKey(Creator, blank=True, null=True, on_delete=models.SET_NULL)
    last_updated = models.DateField(auto_now=True)

    def __str__(self): 
        return str(self.last_updated)
    
class MonthlyRefferalPointsUpdate(models.Model): 
    # we award creator 10,000 points monthly for reffering other creators
    # so we are using this model to track if creators has already been awarded points
    creator = models.ForeignKey(Creator, blank=True, null=True, on_delete=models.SET_NULL)
    last_updated = models.DateField(auto_now=True)

    def __str__(self): 
        return str(self.last_updated)
