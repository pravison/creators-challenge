from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import date
from businesses.models import Business, Staff, Challenge, ChallengeResult, LoyaltyPointForLogginIn, MonthlyRefferalPointsUpdate
from creators.models import Creator
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

def pricing(request):
    return render(request, 'home/pricing.html')

def generate_unique_refferal_code():
    while True:
        code = uuid.uuid4().hex[:4]
        if not RefferralCode.objects.filter(code=code).exists():
            return code
    
@login_required(login_url="/login-user/")
def profile(request):
    today = date.today()
    create_refferal_code=request.GET.get('create_refferal_code') or ''
    creator = Creator.objects.filter(user=request.user).first()
    staff_businesses = Staff.objects.filter(user=request.user)
    challenges = Challenge.objects.filter(closed=False)
    points = ChallengeResult.objects.filter(creator=creator)
    businesses_reffered = Business.objects.filter(reffered_by=request.user)
    creators_reffered = Creator.objects.filter(reffered_by=request.user)
    refferal_code = RefferralCode.objects.filter(user=request.user).first()
    challenges_count = 0
    businesses = []

    if creator:
        businesses = Business.objects.filter(challenges__participants=creator).distinct().prefetch_related("challenges_set") #business user has participated in their challange
        challenges_count = Challenge.objects.filter(closed=False, participants=creator).count()

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
            last_update_instance = MonthlyRefferalPointsUpdate.objects.filter(creator = creator).first()
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
        'points': points,
        'businesses_reffered': businesses_reffered,
        'creators_reffered': creators_reffered,
        'refferal_code': refferal_code
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
                'Your Password Reset Code',
                f'Your reset code is: {reset_code.code}',
                'noreply@example.com',
                [email],
            )
            messages.success(request, 'A reset code has been sent to your email and expires in ten minutes.')
            return redirect('verify_reset_code')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    else:
        form = RequestResetCodeForm()
    return render(request, 'home/request_reset_code.html')


def verify_reset_code(request):
    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
        try:
            reset_code = PasswordResetCode.objects.filter(code=code, is_valid=True).order_by('-created_at').first()
            if reset_code.is_expired():
                reset_code.is_valid = False
                reset_code.save()
                messages.error(request, 'This code has expired.')
            else:
                # Invalidate the code
                reset_code.is_valid = False
                reset_code.save()
                # Redirect to password reset form
                request.session['password_reset_user_id'] = reset_code.user.id
                return redirect('reset_password')
        except PasswordResetCode.DoesNotExist:
            messages.error(request, 'Invalid or expired code.')
    form = PasswordResetCodeForm()
    return render(request, 'home/verify_reset_code.html', {'form': form} )

def reset_password(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        return redirect('request_reset_code')
    
    user = User.objects.get(id=user_id)
    try:
        reset_code = PasswordResetCode.objects.filter(user=user).order_by('-created_at').first()
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
            return redirect('profile')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('login_user')
    else:
        return render(request, 'home/login.html', {'next':next})

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('login_user')

    
