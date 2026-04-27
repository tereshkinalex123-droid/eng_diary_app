from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
    })

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'accounts/profile_settings.html', {'form': form})

@login_required
def profile_stats(request):
    return render(request, 'accounts/profile_stats.html', {
        'user': request.user,})
