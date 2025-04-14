from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField

# Create your models here.
class SocialMediaAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=100, help_text='ex. facebook')
    total_follower = models.IntegerField(default=0, help_text='followers or subscribers etc.')
    account_link = models.URLField()

    def __str__(self):
        return f'{self.user.first_name} - {self.platform} - {self.total_follower}'
    
class Creator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number= models.CharField(max_length=25, blank=True, null=True, help_text='whatsapp phone number written in international format withou plus sign ex. 254740562740')
    total_followers = models.IntegerField(default=0, help_text='accross all your social platforms')
    total_points = models.IntegerField(default=0)
    brief_bio = HTMLField(blank=True)
    type_of_content = HTMLField(blank=True)
    social_media_accounts = models.ManyToManyField(SocialMediaAccount, blank=True)
    reffered_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='refferal')
    willing_to_patner = models.BooleanField(default=False, help_text='checking if creator is willing to go in patnership') 
    not_willing_to_patner = models.BooleanField(default=False, help_text='checking if creator is willing to go in patnership') 
    willing_to_work = models.BooleanField(default=False, help_text='checking if creators is willing to create content for businesses on monthly retainor')
    not_willing_to_work = models.BooleanField(default=False, help_text='checking if creators is willing to create content for businesses on monthly retainor') 
    date_joined = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'{self.user.first_name} {self.total_followers}'

class CreatorsSurvey(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='survey')
    question_one = models.TextField(default='Are you open to working for brands to shoot videos, pictures or livestreams?')
    question_one_answer = models.BooleanField(default=True)
    question_two = models.TextField(default='Rate your video creation skills from 1-10?')
    question_two_answer = models.IntegerField(default=1)
    question_three = models.TextField(default='Which video creation tools stack are you currently using?')
    question_three_answer = models.TextField(blank=True)
    question_four = models.TextField(default='Which video creation tools stack you think if you have you can create more awsome videos?')
    question_four_answer = models.TextField(blank=True)
    question_five = models.TextField(default='Which business industries or categories are you passionate to work with? list as many as you can')
    question_five_answer = models.TextField(blank=True)
    question_six = models.TextField(default='Add a youtube or any social media link to a video you created')
    question_six_answer = models.URLField(blank=True, null=True)
    question_seven = models.TextField(default='Add another youtube or any social media link to a video you created')
    question_seven_answer = models.URLField(blank=True, null=True)
    question_eight = models.TextField(default='Add a third youtube or any social media link to a video you created')
    question_eight_answer = models.URLField(blank=True, null=True)
    question_nine = models.TextField(default='Current Country of residence')
    question_nine_answer = models.CharField(max_length=200, default="Kenya")
    question_ten = models.TextField(default='Current County of residence')
    question_ten_answer = models.CharField(max_length=200, blank=True, null=True)
    question_eleven = models.TextField(default='Minimum monthly pay you are open to?')
    question_eleven_answer = models.CharField(max_length=200, blank=True, null=True)
    question_13 = models.TextField(default='Can you do livestream too?')
    question_13_answer = models.CharField(max_length=200, blank=True, null=True, choices=(('yes', 'yes'), ('no', 'no')))

    def __str__(self):
        return self.creator

# this account is to keep the progress of creators account to start getting monetized
# to be monetized you must paticipate in atleast 15 challenges
# and log into ones account for atleast 30 days
class AccountMonetization(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    percentage_login_progress = models.FloatField(default=1.667) #this will hold upto 50 percent everyday log in equals 1.667%
    login_update_date = models.DateField()
    challenge_participation_progress = models.FloatField(default=3.334) #this will hold upto 50 percent every participaion in a challenge equals 3.334%
    challenge_participation_update_date = models.DateField()
    average_percentage_progress = models.IntegerField(default=5)
    monetizable = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.creator} {self.average_percentage_progress} {self.monetizable}'
