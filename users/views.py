from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone = phone
            user.save() 
            messages.success(request, 'Registration successfull')
            return redirect('register')
    else:
        form = RegistrationForm()
            
    context = {
        'form':form,
    }
    return render(request, 'users/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Invalid credentials'), 
            return redirect('login')
        
    return render(request, 'users/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login') 
