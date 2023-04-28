from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse 
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests



#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):
    if request.user.is_authenticated:
        return redirect('home') 
    
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
            user.set_password(password)
            user.save() 
            
            #User activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('users/account_verification_email.html',{
                'user':  user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registring with us. We have sent you a verification email to your email address. Please verify it.')
            return redirect('/users/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
            
    context = {
        'form':form,
    }
    return render(request, 'users/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(request, username=email, password=password)
        # print(email, password)
        # print(user)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # print(cart_item)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                    #get cart items from the users to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    existing_var_list = []
                    id = []
                    
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pv in product_variation:
                        if pv in existing_var_list:
                            index = existing_var_list.index(pv)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user 
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user 
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print('query', query)
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else: 
            messages.error(request,'Invalid credentials'), 
            return redirect('login')
        
    return render(request, 'users/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login') 

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations!, Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
    return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'users/dashboard.html')

def forgot_password(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email):
            user = User.objects.get(email__iexact=email)

            #Reset password
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            message = render_to_string('users/reset_password_email.html',{
                'user':  user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')
            
        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgot_password')
            
    return render(request, 'users/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid 
        messages.success(request, 'Please reset your password')
        return redirect('reset-password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confim_password = request.POST['confirm_password']

        if password == confim_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfull')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset-password')
    else:   
        return render(request, 'users/reset_password.html')