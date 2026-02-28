from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .forms import RecordForm
from .models import Record, Tag
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q


@login_required #denies access to the page to an unlogged user
def record_list(request): #main page
    records = Record.objects.filter(user=request.user).order_by('-date')
    #.order_by('-date') - сортировка по дате по убыванию
    #Record.objects - Это менеджер модели. через него делаются все запросы к базе

    query = request.GET.get('search')
    tag = request.GET.get('tag')

    if query:
        records = records.filter(
            Q(title__icontains=query),
            Q(content__icontains=query)
        )

    if tag:
        records = records.filter(tags__id=tag)

    records = records.distinct() #remove duplicates

    paginator = Paginator(records, 5) #pagination
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': query,
        'selected_tag': tag,
        'all_tags': Tag.objects.all(),
    }

    return render(request, 'records/record_list.html', context)

@login_required
def show_record(request, slug): # show one page
    record = get_object_or_404(
        Record,
        slug=slug,
        user=request.user
    )

    return render(request, 'records/record.html', {'record': record})

@login_required
def add_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            form.save_m2m()

            new_tag_name = form.cleaned_data.get("new_tag")

            if new_tag_name:
                tag, created = Tag.objects.get_or_create(
                    name=new_tag_name.strip().lower()
                )
                record.tags.add(tag)
            return redirect('record_list')
    else:
        form = RecordForm()
    return render(request, 'records/add_record.html', {'form': form, 'all_tags': Tag.objects.all()})

@login_required
def edit_record(request, slug):

    record = get_object_or_404(
        Record,
        slug=slug,
        user=request.user
    )

    if request.method == 'POST':
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save()

            new_tag_name = form.cleaned_data.get("new_tag")

            if new_tag_name:
                tag, created = Tag.objects.get_or_create(
                    name=new_tag_name.strip().lower()
                )
                record.tags.add(tag)

            return redirect('record', slug=record.slug)
    else:
        form = RecordForm(instance=record)

    return render(request, 'records/edit_record.html', {'form': form, 'record': record, 'all_tags': Tag.objects.all()})

@login_required
def delete_record(request, slug):
    record = get_object_or_404(
        Record,
        slug=slug,
        user=request.user,
    )

    if request.method == 'POST':
        record.delete()

    return redirect('record_list')

@login_required
def show_statistics(request):
    records = Record.objects.filter(user=request.user).order_by('date')

    total_records = records.count()
    total_words = sum(record.word_count() for record in records)

    titles = [record.title for record in records]
    words = [record.word_count() for record in records]
    average_words = int(sum(words) / len(records))

    context = {
        'total_records': total_records,
        'total_words': total_words,
        'titles': titles,
        'words': words,
        'average_words': average_words,
    }

    return render(request, 'records/statistics.html', context)

@require_POST
@login_required
def create_tag(request):
    name = request.POST.get('name', "").strip().lower()

    if not name:
        return JsonResponse({'error': 'Empty name'}, status=400)

    tag, created = Tag.objects.get_or_create(name=name)

    return JsonResponse({
        "id": tag.id,
        "name": tag.name
    })

@require_POST
@login_required
def attach_tag(request):
    record_id = request.POST.get('record_id')
    tag_id = request.POST.get('tag_id')

    record = get_object_or_404(
        Record,
        id=record_id,
        user=request.user
    )
    tag = get_object_or_404(
        Tag,
        id=tag_id
    )

    record.tags.add(tag)

    return JsonResponse({
        "id": tag.id,
        "name": tag.name
    })
