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
from .models import Creator, SocialMediaAccount, AccountMonetization, CreatorsSurvey
from businesses.models import ChallengeResult, JobApplication, ContentCreationJob

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
            phone_number = int(phone_number),
            total_followers= int(total_followers),
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

def edit_profile(request, id):
    creator = Creator.objects.filter(id=id).first()
    social_media_link = request.GET.get('social_media_link') or ''

    if creator is None:
        messages.success(request, 'Creator account not found')
        return redirect('profile')

    social_media_accounts = SocialMediaAccount.objects.filter(user=request.user) or None

    if creator.user == request.user:
        if request.method == "POST":
            phone_number = request.POST.get('phone_number')
            total_followers = request.POST.get('total_followers', 0)
            type_of_content = request.POST.get('type_of_content')
            brief_bio = request.POST.get('brief_bio')

            creator.phone_number = int(phone_number)
            creator.total_followers = int(total_followers)
            creator.type_of_content = type_of_content
            creator.brief_bio = brief_bio
            creator.save()
            messages.success(request, 'Your information has been saved succesfully')
            return redirect('profile')
    
    context = {
       'creator': creator,
       'social_media_accounts':social_media_accounts
    }
    return render(request, 'business/edit-profile.html', context)


def creators_survey_for_work(request, id):
    creator = Creator.objects.filter(id=id).first()

    if creator is None:
        messages.success(request, 'Creator account not found')
        return redirect('profile')
    creator_survey = CreatorsSurvey.objects.filter(creator=creator).first()
    if creator_survey is None:
        creator_survey = CreatorsSurvey.objects.create(creator=creator)

    if request.method == "POST":
        question_two_answer = request.POST.get('question_two_answer')
        question_13_answer = request.POST.get('question_13_answer')
        question_three_answer = request.POST.get('question_three_answer')
        question_four_answer = request.POST.get('question_four_answer')
        question_five_answer = request.POST.get('question_five_answer')
        question_six_answer = request.POST.get('question_six_answer')
        question_seven_answer = request.POST.get('question_seven_answer')
        question_eight_answer = request.POST.get('question_eight_answer')
        question_nine_answer = request.POST.get('question_nine_answer')
        question_ten_answer = request.POST.get('question_ten_answer')
        question_eleven_answer = request.POST.get('question_eleven_answer')

        creator_survey.question_two_answer = int(question_two_answer)
        creator_survey.question_13_answer = question_13_answer
        creator_survey.question_three_answer = question_three_answer
        creator_survey.question_four_answer = question_four_answer
        creator_survey.question_five_answer = question_five_answer
        creator_survey.question_six_answer  = question_six_answer 
        creator_survey.question_seven_answer = question_seven_answer
        creator_survey.question_eight_answer = question_eight_answer
        creator_survey.question_nine_answer = question_nine_answer
        creator_survey.question_ten_answer = question_ten_answer
        creator_survey.question_eleven_answer = question_eleven_answer
        creator_survey.save()
        messages.success(request, 'Your information has been saved succesfully')
        return redirect('profile')


    context = {
       'creator_survey': creator_survey,
       'creator': creator
    }
    return render(request, 'business/creators-survey-for-work.html', context)

def creator_profile(request, id):
    job_id = request.GET.get('job_id') or ''
    creator_id = request.GET.get('creator_id', '')
    creators_with_surveys = Creator.objects.prefetch_related('survey').all()
    creator = creators_with_surveys.filter(id=id).first()
    challenges = ChallengeResult.objects.filter(creator=creator).all()
    if creator is None:
        messages.success(request, 'Creator account not found')
        return redirect('profile')

    if job_id != '' and creator_id != '':
        job = ContentCreationJob.objects.filter(id=job_id, position_filled=False).first()
        if job is None:
            messages.success(request, "Job applied is unavailable")
        if JobApplication.objects.filter(job=job, creator=creator).exists():
            messages.success(request, "Request Already send")
        else:
            JobApplication.objects.create(
                job=job,
                business = job.business, 
                creator=creator,
                accepted_by_creator = True
                )
            messages.success(request, "Congratulations your hiring request has been successfully send to the creator")
     
    if creator_id != '' and not job_id != '' :
        messages.success(request, "Visit your business dashboard select the job you want to hire the creator first and you will be redirected to this page")
        
    context = {
       'job_id': job_id,
       'creator': creator,
       'challenges': challenges
    }
    return render(request, 'business/creator-profile.html', context)

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


