from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import *
from .forms import *
from django.http import HttpResponse

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required

def dashboard(request):
    # Количество заявок по статусам
    total_draft = Application.objects.filter(status=Application.DRAFT).count()
    total_approved = Application.objects.filter(status=Application.APPROVED).count()
    total_declined = Application.objects.filter(status=Application.DECLINED).count()
    
    # Список категорий
    categories = Category.objects.all()

    # Поиск заявок
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    applications = Application.objects.all()

    if query:
        applications = applications.filter(description__icontains=query)

    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'total_draft': total_draft,
        'total_approved': total_approved,
        'total_declined': total_declined,
        'categories': categories,
        'applications': applications,
    }
    return render(request, 'dashboard.html', context)


@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        if 'approve' in request.POST:
            application.status = Application.APPROVED
        elif 'decline' in request.POST:
            application.status = Application.DECLINED

        # Добавляем комментарий при принятии или отклонении заявки
        application.comment = request.POST.get('comment', '')
        application.save()

        return redirect('dashboard')

    return render(request, 'application_detail.html', {'application': application})


@login_required
def create_or_edit_category(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    else:
        category = None
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Переадресация после сохранения
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'create_edit_category.html', {'form': form, 'category': category})


def application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    user_telegram_id = request.GET.get('telegram_id')

    # Проверяем, является ли текущий пользователь создателем заявки
    if application.telegram_id != user_telegram_id:
        return HttpResponseForbidden("Вы не можете просматривать эту заявку.")
    
    return render(request, 'application_status.html', {'application': application})