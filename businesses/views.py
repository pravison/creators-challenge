from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from datetime import date, timedelta
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify
from .models import Business, Staff, Challenge, JobApplication,  LoyaltyPointsCategory, ChallengeResult, ContentCreationJob
from .forms import ContentCreationJobForm
from home.models import RefferralCode
from creators.models import Creator, AccountMonetization
from django.contrib.auth.decorators import login_required
from .decorators import team_member_required
from creators.functions import sendChallengeNotificationToCreators

import qrcode
from PIL import Image, ImageDraw, ImageFont


from io import BytesIO
import base64
# Create your views here.

@login_required(login_url="/login-user/")
def add_business(request):
    pricing_plan = request.GET.get('pricing_plan') or ''
    refferal_code = request.GET.get('refferal_code') or ''
    if pricing_plan == '':
        messages.success(request, 'Choose Pricing Plan First')
        return redirect('pricing')
    context = {
         'pricing_plan': pricing_plan,
         'refferal_code': refferal_code
    }
    if request.method == "POST":
        business_name = request.POST.get('business_name')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        address = request.POST.get('address')
        description = request.POST.get('description')
        refferal_code = request.POST.get('refferal_code') or ''

        if Business.objects.filter(business_name=business_name).exists():
            messages.success(request, 'Business Name  already exists.')
            messages.success(request, 'Choose another name or add some letters!')
            return redirect('add_business')

        owner =request.user
        slug=slugify(business_name)
        subscription_plan = pricing_plan
        reffery = None
        if refferal_code != '':
            code = RefferralCode.objects.filter(code=refferal_code).first()
            if code and not code.user == request.user:
                reffery = code.user
        business = Business.objects.create(
            business_name=business_name, 
            slug=slug, 
            phone_number=phone_number, 
            location=location, 
            address=address, 
            description=description, 
            owner=owner, 
            subscription_plan=subscription_plan,
            reffered_by=reffery
            )
        
        # login user
        
        if not Staff.objects.filter(user=request.user, business=business).exists():
                Staff.objects.create(
                    user=request.user,
                    business=business
                )

        messages.success(request, 'Business Account Created Successfuly')  
        return redirect('dashboard', slug)
    
    return render(request, 'business/add-business.html', context)

@login_required(login_url="/login-user/")
def business(request):
    businesses = Business.objects.filter(owner=request.user)
    if not businesses:
        messages.success("You haven't created any business account. create one !!! by clicking create new business")
        return redirect('profile')
    businesses_count = businesses.count()
    business = businesses.first()
    if businesses_count == 1:
        return redirect('dashboard', business.slug)
    
    staff = Staff.objects.filter(user=request.user, business=business).first()

    
    context = {
        'businesses': businesses,
        'business': business,
        'staff': staff,
    }
    return render(request, 'business/business.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def dashboard(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    challenges = Challenge.objects.filter(business=business)
    challenges_resuslts = ChallengeResult.objects.filter(challenge__business=business)
    total_views = challenges_resuslts.aggregate(Sum('total_views'))['total_views__sum'] or 0
    total_challenges = challenges.count()
    total_budget = challenges.aggregate(Sum('budget'))['budget__sum'] or 0
    total_creators = challenges_resuslts.values('creator').distinct().count() or 0
    context={
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'total_challenges' :  total_challenges,
        'total_views': total_views,
        'total_budget':total_budget,
        'total_creators': total_creators
    }
    return render(request, 'business/dashboard.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def add_staff(request, slug):
    url=f'/register-user/?add_staff_to={slug}'
    return redirect(url)

@login_required(login_url="/login-user/")
@team_member_required
def add_content_creation_job(request, slug):
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, business=business).first()
    if staff is None:
        messages.success(request, 'have No permission to list a content creation job')
        return redirect('profile')
    if request.method == 'POST':
        form = ContentCreationJobForm(request.POST)
            # Save the form only if all validations pass
        if form.is_valid():
            instance=form.save(commit=False)
            instance.business =  business
            instance.save()
            messages.success(request, "Job created succesfully ")
            url = f'/creators/?job_id={instance.id}'
            return redirect(url) 
    
    form = ContentCreationJobForm()
    context = {
        'business': business,
        'staff': staff,
        'form': form
    }
    return render(request, 'business/add-content-creation-job.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def content_creation_jobs(request, slug):
    update = request.GET.get('update') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    if business is None:
        messages.success(request, 'Business does not exist')
        return redirect('profile')
    jobs = ContentCreationJob.objects.filter(business=business).order_by('-id')
    staff = Staff.objects.filter(business=business, user=request.user)
    if update != '':
        challenge = Challenge.objects.filter(id=update).first()
        if challenge.closed == False:
            challenge.closed = True
            challenge.save()
        else:
            challenge.closed = False
            challenge.save()
        return redirect('store_challenges', slug)
    context={
        'businesses': businesses,
        'business': business,
        'jobs':jobs,
        'staff': staff
    }
    return render(request, 'business/content-creation-jobs.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def content_creation_jobs_requests(request, slug):
    job_application_id = request.GET.get('job_application_id') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    if business is None:
        messages.success(request, 'Business does not exist')
        return redirect('profile')
    job_requests = JobApplication.objects.filter(business=business).order_by('-id')
    staff = Staff.objects.filter(business=business, user=request.user)
    if job_application_id != '':
        job_request= JobApplication.objects.filter(business=business, id=job_application_id).first()
        if job_request is None:
            messages.success(request, 'job request does not exist')
            return redirect('content_creation_jobs_requests', slug)
        else:
            job_request.accepted_by_business = True
            job_request.save()
            messages.success(request, 'job request approved')
            messages.success(request, 'creator updated')
            messages.success(request, 'encouraged to reach out to the creator using the number above')
        return redirect('content_creation_jobs_requests', slug)
    context={
        'businesses': businesses,
        'business': business,
        'job_requests':job_requests,
        'staff': staff
    }
    return render(request, 'business/jobs-requests.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def create_store_challenge(request, slug):
    challenge_type = request.GET.get('challenge_type') or ''
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, business=business).first()
    if staff is None:
        messages.success(request, 'have No permission to create challenge on behalf of these business ')
        return redirect('profile')
    if request.method == "POST":
        description = request.POST.get('description')
        category = 'challenge'
        if challenge_type == 'view reward program':
            category = 'view reward program'
        challenge_name = request.POST.get('challenge_name')
        pay_per_1000_views = request.POST.get('pay_per_1000_views') or 0
        maximum_payout_per_creator = request.POST.get('maximum_payout_per_creator') or 0
        budget = request.POST.get('budget') or 0
        rules = request.POST.get('rules')
        instant_reward = request.POST.get('instant_reward')
        video_url = request.POST.get('video_url')
        last_day_of_the_challenge = request.POST.get('last_day_of_the_challenge')
        # challenge_reward= pay_per_1000_views #for view reward programme
        # if category == 'challenge':
        challenge_reward = int(int(budget) * 0.90) 
        challenge=Challenge.objects.create(
            business=business,
            category=category,
            budget = budget,
            pay_per_1000_views = pay_per_1000_views,
            maximum_payout_per_creator=maximum_payout_per_creator,
            challenge_name = challenge_name,
            challenge_reward = challenge_reward,
            instant_reward = instant_reward,
            description =description,
            video_url=video_url,
            rules=rules,
            last_day_of_the_challenge = last_day_of_the_challenge,
            created_by=staff
        )
        messages.success(request, 'challenge created successfuly')  
        # sendChallengeNotificationToCreators(challenge)
        return redirect('store_challenges', slug)
    context = {
        'business': business,
        'staff': staff,
        'challenge_type': challenge_type
    }
    return render(request, 'business/create-challenge.html', context)

@login_required(login_url="/login-user/")
@team_member_required
def store_challenges(request, slug):
    update = request.GET.get('update') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    challenges = Challenge.objects.filter(business=business).order_by('-id')
    staff = Staff.objects.filter(business=business, user=request.user)
    if update != '':
        challenge = Challenge.objects.filter(id=update).first()
        if challenge.closed == False:
            challenge.closed = True
            challenge.save()
        else:
            challenge.closed = False
            challenge.save()
        return redirect('store_challenges', slug)
    context={
        'businesses': businesses,
        'business': business,
        'challenges':challenges,
        'staff': staff
    }
    return render(request, 'business/store-challenges.html', context)

# @login_required(login_url="/login-user/")
def view_store_challenge(request, slug):
    challenge_id = request.GET.get('challenge_id')
    business = Business.objects.filter(slug=slug).first()
    businesses = []
    staff = []
    if request.user.is_authenticated:
        businesses = Business.objects.filter(owner=request.user)
        staff = Staff.objects.filter(business=business, user=request.user)
    challenge = Challenge.objects.filter(id=challenge_id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect again')
        return redirect('challenge_opportunities')
    participants = ChallengeResult.objects.filter(challenge=challenge).order_by('-total_views')
    winners = participants
    top_reward = 0
    second_reward = 0
    third_reward = 0
    fourth_reward = 0
    fifth_reward = 0
    sixth_reward = 0
    seventh_reward = 0
    if challenge.category == 'challenge':
        target_winners = challenge.target_winners
        winners = winners[:target_winners]
        top_reward = int(0.49*int(challenge.challenge_reward))
        second_reward = int(0.20*int(challenge.challenge_reward))
        third_reward = int(0.15*int(challenge.challenge_reward))
        fourth_reward = int(0.06*int(challenge.challenge_reward))
        fifth_reward = int(0.05*int(challenge.challenge_reward))
        sixth_reward = int(0.04*int(challenge.challenge_reward))
        seventh_reward = int(0.03*int(challenge.challenge_reward))
    else:
        for obj in winners:
            obj.potential_earning = int(((obj.total_views)/1000) * challenge.pay_per_1000_views)
    qr_url = f"{request.scheme}://{request.get_host()}/business/{slug}/view-store-challenge/?challenge_id={challenge_id}"  # URL to lock the code

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save QR code to memory
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    context={
        'businesses': businesses,
        'staff': staff,
        'business': business,
        'challenge':challenge,
        'participants': participants,
        'winners': winners,
        'qr_code_image': qr_code_image,
        'top_reward': top_reward,
        'second_reward': second_reward,
        'third_reward': third_reward,
        'fourth_reward': fourth_reward,
        'fifth_reward': fifth_reward,
        'sixth_reward': sixth_reward,
        'seventh_reward': seventh_reward
    }
    return render(request, 'business/view-store-challenges.html', context)

@login_required(login_url="/login-user/")
def submit_challenge_video_url(request, id):
    today = date.today()
    challenge = Challenge.objects.filter(id=id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect and try again ')
        return redirect('challenge_opportunities')
    if request.method == "POST":
        video_url = request.POST.get('video_url')

        creator = Creator.objects.filter(user=request.user).first()
        if not creator:
            creator = Creator.objects.create(user=request.user)

        monetization_progress = AccountMonetization.objects.filter(creator=creator).first()
        if monetization_progress is None:
            AccountMonetization.objects.create(
                creator=creator,
                login_update_date = today,
                challenge_participation_update_date = today
                )
        else:
            if creator not in challenge.participants.all():
                monetization_progress.challenge_participation_progress += 3
                if monetization_progress.challenge_participation_progress < 50 :
                    monetization_progress.average_percentage_progress += int(3)
                monetization_progress.challenge_participation_update_date = today
                monetization_progress.save()

        ChallengeResult.objects.create(
            challenge=challenge,
            creator = creator,
            video_url=video_url
        ) 
        challenge.participants.add(creator)
        challenge.save()
        messages.success(request, 'your challenge video submitted successfuly')  
        url = f'/business/{challenge.business.slug}/view-store-challenge/?challenge_id={id}'
        return redirect(url)
    context = {
        'challenge':challenge
    }
    return render(request, 'business/submit-challenge-video-url.html', context)

