from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, PasswordResetForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse

# making query
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request , f'Account created for { username }! Now LogIn with the Username and Password.')
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request,'users/register.html', {'form':form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request , f'Account Updated!.')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request,'users/profile.html',context)
 
def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            password_reset_form.save()
            user_name = password_reset_form.cleaned_data.get('username')
            return HttpResponse(user_name + ' is the associated user.')
            user_obj = User.objects.filter(username=user_name).first()
            # return HttpResponse(user_obj + 'is the associated user.')
            

            if user_obj:
                subject = "Password Reset Requested"
                email_template_name = "password_reset_email.txt"
                c = {
                "email":user_obj.mail,
                'domain':'127.0.0.1:8000',
                'site_name':'Website',
                "user":user_obj,
                "uid": urlsafe_base64_encode(force_bytes(user_obj.pk)),
                'token': default_token_generator.make_token(user_obj),
                'protocol': 'https',
                }
                email = render_to_string(email_template_name, c)
                return HttpResponse('Make sure all fields are entered and valid.')
                try:
                    #send_mail( subject2, body2, from2, [to2], connection=connection)
                    send_mail(subject, email, settings.EMAIL_HOST_USER , [user_obj.email], fail_silently=False)
                    
                except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                
                return redirect('password_reset_done')

    form = PasswordResetForm()
    
    return render(request,'users/password_reset.html', {'form':form})