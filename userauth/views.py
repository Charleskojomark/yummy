from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm
from .models import UserProfile
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.urls import reverse_lazy



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user but don't activate it yet
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            
            # Set up the email for confirmation
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            html_message = render_to_string('email/verify_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            plain_message = strip_tags(html_message)
            to_email = form.cleaned_data.get('email')
            
            # Send the email
            email = EmailMultiAlternatives(mail_subject, plain_message, 'Yummy Kitchen <no-reply@yummykitchen.com>', [to_email])
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            # Provide success feedback to the user
            username = form.cleaned_data.get('username')
            messages.success(request, f"Welcome {username}, Please check your email to confirm your address.")
            return redirect('core:index')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='userauth.authentication.EmailBackend')  
        

            # Prepare the welcome email
        # current_site = get_current_site(request)
        # mail_subject = 'Welcome to Yummy Kitchen'
        # context = {
        #     'user': user,
        #     'domain': current_site.domain,
        # }
        # html_message = render_to_string('welcome_electrician_email.html', context)
        # plain_message = strip_tags(html_message)
        # to_email = user.email
        # email = EmailMultiAlternatives(mail_subject, plain_message, 'Yummy Kitchen', [to_email])
        # email.attach_alternative(html_message, "text/html")
        # email.send()

        messages.success(request, "Congratulations, Your account has been activated")
        return redirect('core:index')
    else:
        return HttpResponse('Activation link is invalid!')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']  # This can be email or username
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='userauth.authentication.EmailBackend')
            messages.success(request,f"You're logged in")

            return redirect('core:index')  
        else:
            # Handle invalid login
            messages.warning(request, "user does not exist")
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('userauth:login') 


def home_view(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['email'] = request.user.email
    return render(request, 'auth/home.html', context)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('userauth:password_reset_done')
    email_template_name = 'password/password_reset_email.html'
    subject_template_name = 'password/password_reset_subject.txt'
    from_email = 'Ojm Electrical'

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        context['userauth'] = self.request.build_absolute_uri('/')  # Add the site URL to the context
        super().send_mail(subject_template_name, email_template_name,
                          context, from_email, to_email, html_email_template_name)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('userauth:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password/password_reset_complete.html'
    
def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)
