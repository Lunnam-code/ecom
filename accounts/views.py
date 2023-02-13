from django.shortcuts import render, redirect
from .models import Account
from .forms import RegisterationForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():#if form is vaild then we get all the data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            
            #user activation
            current_site =get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()#this will send the email
            #the message is too long we can do it on the command
            # messages.success(request,'Thank you for registering with us. We have sent you verification email to your email address. Please verify!')
            # return redirect('register')
            return redirect('/accounts/signin/?command=verification&email='+email)#go to login and do if request.GET.command == 'verification'
    else:
        form = RegisterationForm()
    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context)

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']#email inside is the name on the form field
        password = request.POST['password']#password inside is the name on the form field
        user = auth.authenticate(email=email,password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('signin')
    return render(request,'accounts/login.html')

@login_required(login_url = 'signin')#login required decorator
def signout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('signin')

def activate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, Account.DoestNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulation! Your account is activated')
        return redirect('signin')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url = 'signin')#should be accessed when you are logged in
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == 'POST':
        email =request.POST['email']
        if Account.objects.filter(email=email).exists():#check if the email exists in the account
            user = Account.objects.get(email__exact=email) #get the user from the account, exact is case sensitive but iexact is not case sensitive
            #reset password
            current_site =get_current_site(request)
            mail_subject = 'Reset Password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            # once the email is send 
            messages.success(request,'Password reset email has been sent to your email address!')
            return redirect('signin')
        else:
            messages.error(request,'Email those not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, Account.DoestNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid #save uid inside session, so that i can access this session when reseting the password
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link has expired!')
        return redirect('signin')
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')#get uid from session we save above
            user = Account.objects.get(pk=uid)#get user
            user.set_password(password)
            user.save()
            messages.success(request,'Password Reset Successful')
            return redirect('signin')
        else:
            messages.error(request,'Password does not match')
            return redirect('restpassword')
    else:
        return render(request, 'accounts/resetpassword.html')
    