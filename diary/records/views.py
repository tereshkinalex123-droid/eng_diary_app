from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Record
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required #denies access to the page to an unlogged user
def record_list(request): #main page
    records = Record.objects.filter(user=request.user).order_by('-date')
    #.order_by('-date') - сортировка по дате по убыванию
    #Record.objects - Это менеджер модели. через него делаются все запросы к базе

    query = request.GET.get('search')
    if query:
        records = records.filter(title__icontains=query) #ДОДЕЛАТЬ КАК БУДЕТ ИСКАТЬ ПО ТЕГУ ИЛИ ТАЙТЛУ

    paginator = Paginator(records, 5) #pagination
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': query,
    }

    return render(request, 'records/record.html', context)

@login_required
def show_record(request, slug): # show one page
    record = get_object_or_404(
        Record,
        slug=slug,
        user=request.user
    )

    return render(request, 'records/show_record.html', {'record': record})

@login_required
def add_record(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        Record.objects.create(
            user=request.user,
            title=title,
            content=content,
        )

        return redirect('record_list')

    return render(request, 'records/add_record.html')

@login_required
def edit_record(request, slug):
    record = get_object_or_404(
        Record,
        slug=slug,
        user=request.user
    )

    if request.method == 'POST':
        record.title = request.POST.get('title')
        record.content = request.POST.get('content')
        record.save()
        return redirect('show_record', slug=record.slug)

    return render(request, 'records/edit_record.html', {'record': record})

@login_required
def show_statistics(request): #ДОДЕЛАТЬ
    records = Record.objects.filter(user=request.user)

    total_records = records.count()
    total_words = sum(record.word_count() for record in records)

    return render(request, 'records/statistics.html',
                  {'total_records': total_records,
                   'total_words': total_words})