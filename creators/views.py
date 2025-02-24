from django.shortcuts import render, redirect
from django.conf import settings 
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import date, timedelta
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Creator, SocialMediaAccount
from home.models import RefferralCode

# Create your views here.
@login_required(login_url="/login-user/")
def add_creator(request):
    refferal_code = request.GET.get('refferal_code') or ''
    if Creator.objects.filter(user=request.user).exists():
        messages.success(request, 'You Already Have An Account')
        return redirect('profile')
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        total_followers = request.POST.get('total_followers') or 0
        type_of_content = request.POST.get('type_of_content') or ''
        brief_bio = request.POST.get('brief_bio') or ''
        refferal_code = request.POST.get('refferal_code') or ''
        reffery = None
        if refferal_code != '':
            code = RefferralCode.objects.filter(code=refferal_code).first()
            if code and not code.user == request.user:
                reffery = code.user
        Creator.objects.create(
            user = request.user,
            phone_number = phone_number,
            total_followers=total_followers,
            brief_bio = brief_bio ,
            type_of_content = type_of_content,
            reffered_by=reffery
        )
        messages.success(request, 'Your Account Created Successfully!!!')  
        return redirect('profile')
    context = {
        'refferal_code': refferal_code
    }
    return render(request, 'business/add-creator.html', context)

processed_message_ids = set()

@csrf_exempt
def whatsappWebhook(request):
    if request.method == "GET":
        VERIFY_TOKEN = settings.VERIFY_TOKEN
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('error', status=403)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'object' in data and data['object'] == 'whatsapp_business_account':
            try:
                for entry in data.get('entry', []):
                    changes = entry.get('changes', [])
                    if changes:
                        value = changes[0].get('value', {})
                        metadata = value.get('metadata', {})
                        phoneId = metadata.get('phone_number_id')
                        contacts = value.get('contacts', [])
                        if contacts:
                            profileName = contacts[0].get('profile', {}).get('name')
                            # whatsAppId = contacts[0].get('wa_id')
                        messages = value.get('messages', [])
                        if messages:
                            fromId = messages[0].get('from')
                            text = messages[0].get('text', {}).get('body')
                            message_id = messages[0].get('id')


                            # Check if customer with the phone number exists
                            # customer = Customer.objects.filter(client=client, phone_number=fromId).order_by('id').first()
                            # if not customer:
                            #     customer= Customer.objects.get_or_create(
                            #             client=client,
                            #             phone_number=fromId,
                            #             whatsapp_profile = profileName,
                            #         ) 
                            
                            # Process the message only if it hasn't been processed before
                            if message_id not in processed_message_ids:
                                processed_message_ids.add(message_id)
                                break
                            break

            except Exception as e:
                print(f"Error processing webhook data: {e}")
                return HttpResponse('error', status=500)
        else:
            return HttpResponse('error', status=400)

        return HttpResponse('success', status=200)


