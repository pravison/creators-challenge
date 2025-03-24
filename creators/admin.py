from django.contrib import admin
from .models import Creator, SocialMediaAccount, CreatorsSurvey, AccountMonetization
# Register your models here.
admin.site.register(Creator)
admin.site.register(SocialMediaAccount)
admin.site.register(CreatorsSurvey)
admin.site.register(AccountMonetization)