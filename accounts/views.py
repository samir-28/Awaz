from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages ,auth
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import get_user_model


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.is_active = False # Require email activation
            user.save()

            # Prepare email verification
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            print("\nActivate your account:\n", message)

            # Redirect to login with message to check email
            return redirect('/accounts/login/?command=verification&email=' + email)
        else:
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                request.session['frontend_login'] = True  
                messages.success(request, 'You are now logged in.')
                print(user)
                # Redirect based on user_type
                if user.user_type == 'admin':
                    return redirect('admin_dashboard')
                elif user.user_type == 'municipality':
                    return redirect('municipality_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Account is not activated. Please verify your email.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


def activate(request, uidb64, token):
    try:
        # Decode UID from base64 to string
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 'Congratulations! Your account has been activated.')
        else:
            messages.info(request, 'Your account is already activated.')
        return redirect('login')  
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('register') 
    
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    request.session.pop('frontend_login', None)
    messages.success(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            print("\nReset your account password:\n", message)
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')

             
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')



def municipality_dashboard(request):
    if request.user.is_authenticated and request.user.user_type == 'municipality':
        return render(request, 'dashboard/municipality_dashboard.html')
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login')
    
def admin_dashboard(request):
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return render(request, 'dashboard/admin_dashboard.html')
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login')