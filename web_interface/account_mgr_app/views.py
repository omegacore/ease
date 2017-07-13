from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

from .forms import SignUpForm


# Create your views here.


def signup(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form =SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('title_page')
    else:
        # form = UserCreationForm()
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
