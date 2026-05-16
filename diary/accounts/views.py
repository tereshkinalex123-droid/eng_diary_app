from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Profile
import uuid


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
    # Получаем профиль пользователя или создаем, если его нет
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    tg_link = None
    # Если Telegram еще не привязан, готовим ссылку
    if not user_profile.telegram_id:
        if not user_profile.connection_token:
            user_profile.connection_token = str(uuid.uuid4())
            user_profile.save()

        bot_username = "lingua_f1ow_bot"
        tg_link = f"https://t.me/{bot_username}?start={user_profile.connection_token}"

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': user_profile,
        'streak': getattr(request.user, 'streak', None),  # Передаем объект streak
        'tg_link': tg_link,
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
        'user': request.user,
        'streak': getattr(request.user, 'streak', None),
    })