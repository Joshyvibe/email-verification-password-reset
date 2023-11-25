
from django.shortcuts import render, redirect

from django.contrib import auth, messages

from .forms import LoginForm, SignUpForm

from django.contrib.auth.models import User
from django.conf import settings


from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.core.mail import send_mail, EmailMessage
from .tokens import account_activation_token



def activate(request, uidb64, token):
    User = auth.get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None


    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login.')
        return redirect('login')
    
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('index')


def activateEmail(request, user, to_email):
    context = {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    }

    email_content = render_to_string('core/acct_active_email.html', context)

    email_subject = 'Activate your account.'
    recipient_list = [to_email]
    from_email = 'allforms@limited.com'

    success = send_mail(
        email_subject,
        '',
        from_email,
        recipient_list,
        html_message=email_content,
        fail_silently=False
    )

    if success > 0:
        messages.success(
            request,
            f"Dear {user}, Please go to your email '{to_email}' inbox and click on "
            f"the received activation link to confirm and complete the registration. Note: Check your spam folder"
        )
    else:
        messages.error(request, f'There was a problem sending email to {to_email}, please make sure your email was spelt correctly.')


def send_custom_password_reset_email(request, user):
    context = {
        'name': user,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': get_current_site(request).domain,
    }
    subject = 'Password Reset'
    from_email = 'allforms@limited.com'
    to_email = user.email

   
    email_content = render_to_string('core/password_reset_email.html', context)
    

    msg = EmailMessage(
        subject,
        email_content,
        from_email,
        [to_email],
        alternatives=[(email_content, 'text/html')],
    )
    msg.send()


def index(request):
    return render(request, 'core/index.html')



def success (request):
    return render(request , 'core/success.html')


def login(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                auth.login(request, user)
                messages.success(request, f"Hello {user.username}! You have been logged in")
                return redirect("/")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, "core/login.html", {"form": form})


def custom_logout(request):
    auth.logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("index")




def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
           email = form.cleaned_data.get('email')
           if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered, Please use a different email.')
           else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail(request, user, email)
                messages.success(request, f"New account created: Please check your email to activate your account")
                return redirect('/')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
                
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

    




class CustomPasswordResetView(PasswordResetView):
    template_name = 'core/password_reset_form.html'
    email_template_name = 'core/password_reset_email.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        users = list(form.get_users(form.cleaned_data['email']))
        user = users[0] if users else None

        if user:
        

            send_custom_password_reset_email(self.request, user)
            return response
        else:
            messages.error(self.request, 'Activation link is invalid!')

            
        

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'core/password_reset_confirm.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your password has been reset successfully.')
        return super().form_valid(form)