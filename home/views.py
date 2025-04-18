from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import date
from businesses.models import Business, Staff, Challenge, ChallengeResult, JobApplication, LoyaltyPointForLogginIn, ContentCreationJob, MonthlyRefferalPointsUpdate
from creators.models import Creator, AccountMonetization, CreatorsSurvey
# Create your views here.
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import PasswordResetCode, RefferralCode
from .forms import RequestResetCodeForm, PasswordResetCodeForm
import uuid

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def business_landing_page(request):
    business = 'business'
    print(business)
    context = {
       'business':business
    }
    return render(request, 'home/business.html', context)
def business_landing_page_2(request):
    # landing page for businesses 
    # selling bussiness to encourage their customer to create video for them 
    business = 'business'
    print(business)
    context = {
       'business':business
    }
    return render(request, 'home/business-customers.html', context)


def pricing(request):
    return render(request, 'home/pricing.html')

def generate_unique_refferal_code():
    while True:
        code = uuid.uuid4().hex[:4]
        if not RefferralCode.objects.filter(code=code).exists():
            return code


@login_required(login_url="/login-user/")
def challenge_opportunities(request):
    creator = Creator.objects.filter(user=request.user).first()
    challenges = Challenge.objects.filter(closed=False)

    if creator is None:
        return redirect('profile')

    
    context = {
        'challenges' : challenges,
        'creator': creator,
    }
    return render(request, 'home/challenge-opportunities.html', context)

    
@login_required(login_url="/login-user/")
def profile(request):
    today = date.today()
    create_refferal_code=request.GET.get('create_refferal_code') or ''
    patner=request.GET.get('patner') or ''
    work=request.GET.get('work') or ''
    creator = Creator.objects.filter(user=request.user).first()
    staff_businesses = Staff.objects.filter(user=request.user)
    challenges = Challenge.objects.filter(closed=False)
    
    businesses_reffered = Business.objects.filter(reffered_by=request.user)
    creators_reffered = Creator.objects.filter(reffered_by=request.user)
    refferal_code = RefferralCode.objects.filter(user=request.user).first()
    challenge_participated_in = None
    job_requests = None
    challenges_count = 0
    businesses = []
    monetization_progress = None
    days_remaining = 29
    challenges_remaining=14
    if creator:
        challenge_participated_in = ChallengeResult.objects.filter(creator=creator)
        job_requests =JobApplication.objects.filter(creator=creator, accepted_by_business=False).count()
        businesses = Business.objects.filter(challenges__participants=creator).distinct().prefetch_related("challenges") #business user has participated in their challange
        challenges_count = Challenge.objects.filter(closed=False, participants=creator).count()

        monetization_progress = AccountMonetization.objects.filter(creator=creator).first()
        if monetization_progress is None:
            AccountMonetization.objects.create(
                creator=creator,
                login_update_date = today,
                challenge_participation_update_date = today
                )
        else:
            if monetization_progress.login_update_date < today and not monetization_progress.monetizable:
                monetization_progress.percentage_login_progress += 2
                if monetization_progress.percentage_login_progress < 50 :
                    monetization_progress.average_percentage_progress += int(2)
                monetization_progress.login_update_date = today
                monetization_progress.save()
            
            days_remaining = int((50-monetization_progress.percentage_login_progress)/2)
            if monetization_progress.percentage_login_progress >= 50:
                days_remaining =0
            challenges_remaining=int((50-monetization_progress.challenge_participation_progress)/3)
            if monetization_progress.challenge_participation_progress >= 50:
                challenges_remaining =0

            if not monetization_progress.monetizable and   monetization_progress.average_percentage_progress > 100:
                monetization_progress.average_percentage_progress = 100
                monetization_progress.monetizable = True
                monetization_progress.save()
                

        if LoyaltyPointForLogginIn.objects.filter(creator = creator).exists():
            last_update_instance = LoyaltyPointForLogginIn.objects.filter(creator = creator).first()
            if last_update_instance.last_updated < today:
                creator.total_points +=10
                creator.save()
                last_update_instance.save()
            else:
                pass
        else:
            last_update_instance = LoyaltyPointForLogginIn.objects.create(creator = creator)
            creator.total_points += 10
            creator.save()
            last_update_instance.save()

        if MonthlyRefferalPointsUpdate.objects.filter(creator = creator).exists():
            last_update_instance = MonthlyRefferalPointsUpdate.objects.filter(creator=creator).order_by('id').last()
            if last_update_instance.last_updated < today - timedelta(days=30):
                total_creators_you_reffered = Creator.objects.filter(reffered_by=request.user).count()
                total_points_earned = total_creators_you_reffered* 10000 # points earned from all creators you reffered
                total_brands_you_reffered = Business.objects.filter(reffered_by=request.user).count()
                total_points_earned_from_brands = total_brands_you_reffered * 1000000 # points earned from all creators you reffered, assuming 1000 points equals 10ksh
                total_points = total_points_earned + total_points_earned_from_brands
                creator.total_points += total_points
                creator.save()
                last_update_instance.save()
            else:
                pass
        else:
            last_update_instance = MonthlyRefferalPointsUpdate.objects.create(creator = creator)
            total_creators_you_reffered = Creator.objects.filter(reffered_by=request.user).count()
            total_points_earned = total_creators_you_reffered* 10000 # points earned from all creators you reffered
            total_brands_you_reffered = Business.objects.filter(reffered_by=request.user).count()
            total_points_earned_from_brands = total_brands_you_reffered * 1000000 # points earned from all creators you reffered, assuming 1000 points equals 10ksh
            total_points = total_points_earned + total_points_earned_from_brands
            creator.total_points += total_points
            creator.save()
            last_update_instance.save()

        if patner !='':
            if patner == 'yes':
                creator.willing_to_patner = True
                messages.success(request, 'Great Choice! Now Business looking to patner with content creators will reach out to you')
                creator.save()
                return redirect('profile')
            else:
                creator.willing_to_patner = False
                creator.not_willing_to_patner = True
                messages.success(request, 'Your option has been updated successfully')
                creator.save()
                return redirect('profile')

        if work !='':
            if work == 'yes':
                creator.willing_to_work = True
                messages.success(request, 'Great Choice! Now Business looking for content creators to create content for them will reach out to you')
                creator.save()
                return redirect('creators_survey_for_work', creator.id)
            else:
                creator.willing_to_work = False
                creator.not_willing_to_work = True
                messages.success(request, 'Your option has been updated successfully')
                creator.save()
                return redirect('profile')
    
    if create_refferal_code != '':
        if not RefferralCode.objects.filter(user=request.user).exists():
            refferal_code = RefferralCode.objects.create(
            user=request.user,
            code = generate_unique_refferal_code()
            )
            messages.success(request, 'Refferal Code Generated Succesfully!!! ')
            messages.success(request, f'your refferal code is {refferal_code.code}!!! ') 
        else:
            messages.success(request, 'already have a refferal code!!! ')


    
    context = {
        'challenges' : challenges,
        'staff_businesses':staff_businesses,
        'businesses': businesses,
        'creator': creator,
        'challenges_count': challenges_count,
        'challenge_participated_in': challenge_participated_in,
        'businesses_reffered': businesses_reffered,
        'creators_reffered': creators_reffered,
        'refferal_code': refferal_code,
        'monetization_progress':monetization_progress,
        'days_remaining': days_remaining,
        'challenges_remaining': challenges_remaining,
        'job_requests': job_requests
    }
    return render(request, 'home/profile.html', context)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm

def request_reset_code(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)      
            # Generate or update the reset code
            reset_code, created = PasswordResetCode.objects.get_or_create(user=user)
            reset_code.code = str(uuid.uuid4().hex[:6])
            reset_code.is_valid = True
            reset_code.save()
            
            # Send email
            send_mail(
                'Challenge  Password Reset Code',
                f'Your reset code is: {reset_code.code}',
                'noreply@example.com',
                [email],
            )
            messages.success(request, 'A reset code has been sent to your email and expires in ten minutes.')
            return redirect('verify_reset_code')
        except User.DoesNotExist:
            messages.success(request, 'No account found with this email.')
            messages.success(request, 'Create an account.')
            return redirect('register_user')
    form = RequestResetCodeForm()
    return render(request, 'home/request_reset_code.html')


def verify_reset_code(request):
    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Error assessing your data counter check and try again')
            return redirect('verify_reset_code')
        code = form.cleaned_data['code']
        try:
            reset_code = PasswordResetCode.objects.filter(code=code, is_valid=True).order_by('created_at').first()
            if reset_code is None:
                messages.error(request, 'Counter check your code seems its incorrect')
                return redirect('verify_reset_code')
            if reset_code.is_expired():
                reset_code.is_valid = False
                reset_code.save()
                messages.error(request, 'This code has expired.')
                return redirect('request_reset_code')
            else:
                # Invalidate the code
                reset_code.is_valid = False
                reset_code.save()
                # Redirect to password reset form
                request.session['password_reset_user_id'] = reset_code.user.id
                return redirect('reset_password')
        except PasswordResetCode.DoesNotExist:
            messages.error(request, 'Counter check your code seems its incorrect')
            return redirect('verify_reset_code')
    form = PasswordResetCodeForm()
    return render(request, 'home/verify_reset_code.html', {'form': form} )

def reset_password(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        messages.error(request, 'There was an error proccessing your application, try again')
        return redirect('request_reset_code')
    
    user = User.objects.get(id=user_id)
    try:
        reset_code = PasswordResetCode.objects.filter(user=user).order_by('-created_at').first()
        if reset_code is None:
            messages.error(request, 'There was an error proccessing your application, try again')
            return redirect('request_reset_code')
        if reset_code.is_expired():
            # If the code is expired or invalid, redirect to request a new one
            reset_code.is_valid = False
            reset_code.save()
            messages.error(request, 'Your reset code has expired. Please request a new code.')
            return redirect('request_reset_code')
    except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
        # If the user or reset code is not found, redirect to the request page
        messages.error(request, 'Invalid reset request. Please try again.')
        return redirect('request_reset_code')
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully reset.')
            return redirect('login_user')
    else:
        form = SetPasswordForm(user)
    return render(request, 'home/reset_password.html', {'form': form})


# Create your views here.
def register_user(request):
    pricing_plan = request.GET.get('pricing_plan') or ''
    add_staff_to = request.GET.get('add_staff_to') or ''
    add_creator = request.GET.get('add_creator') or ''  # Corrected this line
    refferal_code = request.GET.get('refferal_code') or ''
    next = request.GET.get('next') or ''
    context = {
        'add_staff_to': add_staff_to,
        'add_creator': add_creator,
        'pricing_plan': pricing_plan,
        'refferal_code': refferal_code,
        'next': next,
    }

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.success(request, 'Email already exists.')
            messages.success(request, 'If you have never registered using this email, please reach out to our tech team.')
            return render(request, 'home/register.html', context)
        
        # Create user
        username = str(email)
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        
        
        if pricing_plan != '':
            user = authenticate(username=username, password=password)
            login(request, user)
            url = f'/business/add-business/?pricing_plan={pricing_plan}&refferal_code={refferal_code}'
            return redirect(url)

        # Add staff logic
        if add_staff_to != '':
            business = Business.objects.filter(slug=add_staff_to).first()
            if business:
                if not Staff.objects.filter(user=user, business=business).exists():
                    Staff.objects.create(user=user, business=business)
                    messages.success(request, 'Staff added successfully')
                    messages.success(request, 'Share email and password for them to log in')
                
            
            return redirect('dashboard', add_staff_to)
        # print(add_staff_to)

        # Add customer logic
        if add_creator != '':
            user = authenticate(username=username, password=password)
            login(request, user)
            url = f'/creators/add_creator/?refferal_code={refferal_code}'
            return redirect(url)
                
        # Handle redirect for "next" parameter
        if next != '':
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(next)

        # Default redirect after registration
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('profile')

    return render(request, 'home/register.html', context)

def login_user(request):
    next = request.GET.get('next') or ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            messages.success(request, "You Have Been Logged In!")
            if next != '':
                return redirect(next)
            return redirect('challenge_opportunities')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('login_user')
    else:
        return render(request, 'home/login.html', {'next':next})

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('login_user')

    
def jobs(request):
    job_id = request.GET.get('job_id', '')
    jobs = ContentCreationJob.objects.filter(position_filled=False).annotate(total_applications=Count('job_applications'))
    
    if job_id != '':
        job = jobs.filter(id=job_id, position_filled=False).first()
        if job is None:
            messages.success(request, "Job applied is unavailable")
        creator = Creator.objects.filter(user=request.user).first()
        if creator is None:
            messages.success(request, "Register first as creator to be able to apply")
            messages.success(request, "visit your profile and click become creators")
        if JobApplication.objects.filter(job=job, creator=creator).exists():
            messages.success(request, "You've already applied for this job")
        else:
            JobApplication.objects.create(
                job=job,
                business = job.business, 
                creator=creator,
                accepted_by_creator = True
                )
            messages.success(request, "Congratulations Your Application Request has Been Successfully Send")

    context = {
        'jobs': jobs,
    }
    return render(request, 'home/jobs.html', context)

    
def creators(request):
    job_id = request.GET.get('job_id', '')
    creator_id = request.GET.get('creator_id', '')
    creators_with_surveys = Creator.objects.filter(willing_to_work=True).prefetch_related('survey').all()

    if creator_id != '':
        if job_id != '':
            job = ContentCreationJob.objects.filter(id=job_id, position_filled=False).first()
            if job is None:
                messages.success(request, "Job applied is unavailable")
            creator = Creator.objects.filter(id=creator_id).first()
            if creator is None:
                messages.success(request, "Creator could not be found")
                messages.success(request, " try applying again")
            if JobApplication.objects.filter(job=job, creator=creator).exists():
                messages.success(request, "Request Already send")
            else:
                JobApplication.objects.create(
                    job=job,
                    business = job.business, 
                    creator=creator
                    )
                messages.success(request, "Congratulations your hiring request has been successfully send to the creator")
            return redirect('creators')
        else:
            request.session['creator_id'] = creator_id
            messages.success(request, "Select The business that wants to hire creator")
            return redirect('hire_creator')
    

    context = {
        'creators_with_surveys': creators_with_surveys,
        'job_id': job_id
    }
    return render(request, 'home/creators.html', context)

@login_required(login_url="/login-user/")
def job_requests(request):
    job_application_id = request.GET.get('job_application_id', '')
    creator = Creator.objects.filter(user=request.user).first()
    if creator is None:
        messages.success(request, "Register first as creator to be able to see Job requests you have")
        messages.success(request, "visit your profile and click become creators")
        return redirect('profile')
    jobs = JobApplication.objects.filter(creator=creator).order_by('-id')
    
    if job_application_id != '':
        job_application = JobApplication.objects.filter(id=job_application_id, creator=creator).first()
        if job_application is None:
            messages.success(request, "Job application does not exists")
        else:
            job_application.accepted_by_creator = True
            job_application.save()
            messages.success(request, "Congratulations Your Application Acceptance has Been Successfully Send")
            messages.success(request, "awaiting business approval")
            return redirect('job_requests')
    context = {
        'jobs': jobs,
        'creator':creator
    }
    return render(request, 'home/job-requests.html', context)  

@login_required(login_url="/login-user/")
def hire_creator(request):
    staff_businesses = Staff.objects.filter(user=request.user)
    selected_staff_business = None
    jobs_available = None
    selected_id = request.GET.get('selected_id') or ''
    job_id = request.GET.get('job_id') or ''
    creator_id = request.session.get('creator_id') or ''
    if creator_id == '':
        messages.success(request, "There was an error proccessing your request!")
        messages.success(request, "please reselect creator!")
        return redirect('creators') 
    creator = Creator.objects.filter(id=creator_id).first()
    if creator is None:
        messages.success(request, "There was an error proccessing your request!")
        messages.success(request, "please reselect creator!")
        return redirect('creators')

    if staff_businesses is None:
        messages.success(request, "You must create  a business account to be able to hire a creator!")
        messages.success(request, "to create a business account click create business account on your navigation menu!")
        return redirect('profile')
    if selected_id !='':
        selected_staff_business = staff_businesses.filter(id=selected_id).first()
        if selected_staff_business is None:
            messages.success(request, "There was an error processing your request!")
            messages.success(request, "please retry!")
            return redirect('hire_creator')
        jobs_available = ContentCreationJob.objects.filter(business=selected_staff_business.business, position_filled=False) 
        if not jobs_available:
            messages.success(request, "No open positions!")
            messages.success(request, "please create new job positions!")
            return redirect('dashboard', selected_staff_business.business.slug)
    if creator and job_id !='':
        job = ContentCreationJob.objects.filter(id=job_id, position_filled=False).first()
        if job is None:
            messages.success(request, "Job applied is unavailable")
            messages.success(request, "pleease repeat the proceess")
            return redirect('hire_creator')
        else:
            if JobApplication.objects.filter(job=job, creator=creator).exists():
                messages.success(request, "Request Already send")
            else:
                JobApplication.objects.create(
                    job=job,
                    business = job.business, 
                    creator=creator
                    )
                messages.success(request, "Congratulations your hiring request has been successfully send to the creator")

        return redirect('creators')

    context = {
        'staff_businesses': staff_businesses,
        'selected_staff_business': selected_staff_business,
        'jobs_available': jobs_available,
        'creator':creator
    }
    return render(request, 'home/hire-creator.html', context)   
