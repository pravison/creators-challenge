from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
