from django.contrib import admin
from .models import Business, Staff, Challenge,  LoyaltyPointsCategory, ChallengeResult, LoyaltyPointForLogginIn, MonthlyRefferalPointsUpdate

# Register your models here.
admin.site.register(Business)
admin.site.register(Staff)
admin.site.register(Challenge)
admin.site.register(LoyaltyPointsCategory)

from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class ChallengeResultAdmin(admin.ModelAdmin):
    list_display = ['challenge__business', 'challenge__challenge_name', 'creator', 'total_views', 'points_earned', 'challenge__closed', 'challenge__last_day_of_the_challenge', ]
    list_filter = ['challenge__closed', 'challenge__last_day_of_the_challenge', 'challenge__business', 'challenge__challenge_name' ]
    search_fields = ['challenge__business__business_name', 'challenge__challenge_name', 'creator__user__first_name', 'creator__user__last_name', 'creator__phone_number']
    list_display_links= ['challenge__business', 'challenge__challenge_name', 'creator', 'total_views', 'points_earned' ]

    def save_model(self, request, obj, form, change):
        # Always assign the user who created the object
        obj.added_by = f'{request.user.first_name} {request.user.last_name}'

        if change:  
            # We're updating an existing ChallengeResult
            obj.points_earned = obj.total_views
            creator = obj.creator

            if creator:
                creator_total_points = creator.total_points
                creator_challenge_points = obj.points_earned
                current_creator_challenge_points = obj.total_views

                # Ensure we have valid values for calculation
                if obj.total_views > 0:
                    # Recalculate the total points for the creator
                    total_points = creator_total_points - creator_challenge_points + current_creator_challenge_points
                    creator.total_points = total_points

                    # Use a transaction block to ensure data is committed to the database
                    try:
                        with transaction.atomic():  # Use atomic transaction to ensure changes are saved
                            creator.save()  # Save the updated creator's points
                            obj.save()  # Make sure the ChallengeResult is saved as well
                            logger.info(f"Updated total points for creator {creator.id}: {total_points}")
                    except Exception as e:
                        logger.error(f"Error saving creator {creator.id} total points: {e}")
                        raise e  # Re-raise exception to ensure it can be handled in the admin interface
                else:
                    logger.warning("Invalid data for total points calculation: creator_total_points, creator_challenge_points, or current_creator_challenge_points are None")
        else:
            pass  # No action required for new objects

admin.site.register(ChallengeResult, ChallengeResultAdmin)

admin.site.register(LoyaltyPointForLogginIn)
admin.site.register(MonthlyRefferalPointsUpdate)