from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .forms import CustomUserCreationForm,CustomErrorList
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST,error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            SecurityQuestions.objects.create(
                user=user,
                question_1=form.cleaned_data['security_question_1'],
                answer_1=form.cleaned_data['security_answer_1'],
                question_2=form.cleaned_data['security_question_2'],
                answer_2=form.cleaned_data['security_answer_2']
            )

            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from .forms import SecurityQuestionsForm, ResetPasswordForm
from .models import SecurityQuestions
from django.contrib.auth.hashers import make_password
import random

def forgot_password(request):
    template_data = {}
    template_data['title'] = 'Forgot Password'

    if request.method == 'GET':
        template_data['form'] = SecurityQuestionsForm()
        return render(request, 'accounts/forgot_password.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = SecurityQuestionsForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            answer = form.cleaned_data['answer']

            try:
                user = User.objects.get(username=username)
                security = SecurityQuestions.objects.get(user=user)

                # Randomly choose between question 1 and 2
                if 'question_number' not in request.session:
                    question_number = random.choice([1, 2])
                    request.session['question_number'] = question_number
                else:
                    question_number = request.session['question_number']

                correct_answer = security.answer_1 if question_number == 1 else security.answer_2
                if answer.lower() == correct_answer.lower():
                    return redirect('accounts.reset_password', username=username)

                template_data['error'] = "Incorrect answer"
                template_data['security_question'] = {
                    security.question_1 if question_number == 1 else security.question_2
                }
                template_data['form'] = form
                return render(request, 'accounts/forgot_password.html', {'template_data': template_data})

            except (User.DoesNotExist, SecurityQuestions.DoesNotExist):
                template_data['error'] = "Username not found"
                template_data['form'] = form
                return render(request, 'accounts/forgot_password.html', {'template_data': template_data})

def reset_password(request, username):
    template_data = {}
    template_data['title'] = 'Reset Password'
    user = get_object_or_404(User, username=username)

    if request.method == 'GET':
        template_data['form'] = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.password = make_password(form.cleaned_data['new_password1'])
            user.save()
            return redirect('accounts.login')

        template_data['form'] = form
        template_data['error'] = "Please correct the errors below"
        return render(request, 'accounts/reset_password.html', {'template_data': template_data})



