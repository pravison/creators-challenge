from django.conf import settings 
import requests
from .models import Creator
def sendWhatsappMessage(fromId, message):
    whatsapp_url = settings.WHATSAPP_URL
    whatsapp_token = settings.WHATSAPP_TOKEN
    headers = {"Authorization" : whatsapp_token}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type" : "individual",
        "to": fromId,
        "type":"text",
        "text":{"body": message}
        }
    requests.post(whatsapp_url, headers=headers, json=payload)
    return True

def sendChallengeNotificationToCreators(challenge):
    creators = Creator.objects.all()
    challenge_url = f'https:creators-challenge-sigma.vercel.app/business/{challenge.business.slug}/view-store-challenge/'

    message = f'''
    a new Challenge opportunity
    hurry up! 
    submit your creativity
    the earlier you submit more views you earn hence standing great chance to be a chammp
    visit {challenge_url} 
    to learn more about the challenge and submit your creativity
    '''
    for creator in creators:
        fromId=creator.phone_number
        sendWhatsappMessage(fromId, message)
    return True

