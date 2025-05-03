from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q

from .models import Item, Category, Claim
from .forms import ItemForm, ClaimForm, SearchForm
from .services.ai_service import analyze_image
from .services.notification_service import send_notification
from django.contrib.auth.models import User

class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    context_object_name = 'items'
    paginate_by = 8
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Простое отображение счетчиков
        filter_condition = Q(is_moderated=True)
        
        # Если пользователь аутентифицирован, показываем и его неподтвержденные объявления
        if self.request.user.is_authenticated:
            filter_condition |= Q(user=self.request.user)
            
        context['lost_count'] = Item.objects.filter(status='lost').filter(filter_condition).count()
        context['found_count'] = Item.objects.filter(status='found').filter(filter_condition).count()
        context['returned_count'] = Item.objects.filter(status='returned').filter(filter_condition).count()
        context['categories'] = Category.objects.all()
        context['search_form'] = SearchForm()
        return context
    
    def get_queryset(self):
        queryset = Item.objects.filter(status__in=['lost', 'found'])
        
        # Базовая фильтрация - показываем только подтвержденные
        filter_condition = Q(is_moderated=True)
        
        # Если пользователь аутентифицирован, показываем и его неподтвержденные объявления
        if self.request.user.is_authenticated:
            filter_condition |= Q(user=self.request.user)
            
        return queryset.filter(filter_condition).order_by('-date_posted')

class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        status = self.kwargs.get('status', None)
        queryset = Item.objects.all()
        
        # Базовая фильтрация - показываем только подтвержденные
        filter_condition = Q(is_moderated=True)
        
        # Если пользователь аутентифицирован, показываем и его неподтвержденные объявления
        if self.request.user.is_authenticated:
            filter_condition |= Q(user=self.request.user)
            
        queryset = queryset.filter(filter_condition)
        
        # Фильтр по статусу
        if status and status in ['lost', 'found']:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.kwargs.get('status', None)
        context['status'] = status
        context['search_form'] = SearchForm()
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'item_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        context['claim_form'] = ClaimForm()
        if self.request.user.is_authenticated:
            context['has_claimed'] = Claim.objects.filter(item=item, user=self.request.user).exists()
        return context

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'item_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Обработка изображения через AI-сервис, если оно загружено
        if form.instance.image:
            try:
                print(f"[VIEW] Начинаем анализ изображения для объявления")
                
                # Передаем объект ImageField напрямую в функцию анализа
                ai_description = analyze_image(form.instance.image)
                print(f"[VIEW] Получено AI-описание: {ai_description[:100]}...")
                
                # Сохраняем полученное описание
                form.instance.ai_description = ai_description
                print(f"[VIEW] Сохраняем AI-описание в объект")
                form.instance.save()
                print(f"[VIEW] Объект сохранен с AI-описанием")
            except Exception as e:
                print(f"[VIEW] ОШИБКА в AI анализе изображения: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("[VIEW] Нет изображения для анализа")
        
        messages.success(self.request, 'Объявление успешно создано!')
        return response

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'item_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Обработка изображения через AI-сервис, если оно загружено
        if form.instance.image:
            try:
                print(f"[VIEW] Начинаем анализ изображения для объявления")
                
                # Передаем объект ImageField напрямую в функцию анализа
                ai_description = analyze_image(form.instance.image)
                print(f"[VIEW] Получено AI-описание: {ai_description[:100]}...")
                
                # Сохраняем полученное описание
                form.instance.ai_description = ai_description
                print(f"[VIEW] Сохраняем AI-описание в объект")
                form.instance.save()
                print(f"[VIEW] Объект сохранен с AI-описанием")
            except Exception as e:
                print(f"[VIEW] ОШИБКА в AI анализе изображения: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("[VIEW] Нет изображения для анализа")
        
        messages.success(self.request, 'Объявление успешно обновлено!')
        return response
    
    def test_func(self):
        item = self.get_object()
        return self.request.user == item.user

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('home')
    
    def test_func(self):
        item = self.get_object()
        return self.request.user == item.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)

@login_required
def create_claim(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    # Проверка, что пользователь не создает претензию на свой же предмет
    if item.user == request.user:
        messages.error(request, 'Вы не можете создать претензию на свой собственный предмет.')
        return redirect('item-detail', pk=pk)
    
    # Проверка, что пользователь еще не создавал претензию на этот предмет
    if Claim.objects.filter(item=item, user=request.user).exists():
        messages.error(request, 'Вы уже создали претензию на этот предмет.')
        return redirect('item-detail', pk=pk)
    
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.user = request.user
            claim.save()
            
            # Отправка уведомления владельцу объявления
            send_notification(
                user=item.user,
                subject='Новая претензия на ваше объявление',
                message=f'Пользователь {request.user.username} оставил претензию на ваше объявление "{item.title}".'
            )
            
            messages.success(request, 'Ваша претензия успешно создана.')
            return redirect('item-detail', pk=pk)
    
    return redirect('item-detail', pk=pk)

def search_items(request):
    form = SearchForm(request.GET)
    
    # Базовая фильтрация - показываем только подтвержденные
    filter_condition = Q(is_moderated=True)
    
    # Если пользователь аутентифицирован, показываем и его неподтвержденные объявления
    if request.user.is_authenticated:
        filter_condition |= Q(user=request.user)
        
    items = Item.objects.filter(filter_condition).order_by('-date_posted')
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search_query:
            items = items.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(ai_description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        if category:
            items = items.filter(category=category)
        
        if status and status != 'all':
            items = items.filter(status=status)
        
        if date_from:
            items = items.filter(date_lost_found__gte=date_from)
        
        if date_to:
            items = items.filter(date_lost_found__lte=date_to)
    
    context = {
        'items': items,
        'search_form': form,
        'search_query': form.cleaned_data.get('search_query') if form.is_valid() else '',
    }
    return render(request, 'search.html', context)

@login_required
def my_items(request):
    lost_items = Item.objects.filter(user=request.user, status='lost')
    found_items = Item.objects.filter(user=request.user, status='found')
    claimed_items = Item.objects.filter(user=request.user, status__in=['claimed', 'returned'])
    
    claims = Claim.objects.filter(user=request.user)
    
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
        'claimed_items': claimed_items,
        'claims': claims,
    }
    return render(request, 'my_items.html', context)

@login_required
def manage_claims(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    claims = Claim.objects.filter(item=item)
    
    context = {
        'item': item,
        'claims': claims,
    }
    return render(request, 'manage_claims.html', context)

@login_required
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    item = claim.item
    
    # Проверка, что текущий пользователь является владельцем объявления
    if item.user != request.user:
        messages.error(request, 'У вас нет прав на это действие.')
        return redirect('home')
    
    # Обновление статуса претензии и объявления
    claim.status = 'approved'
    claim.save()
    
    item.status = 'claimed' if item.status == 'found' else 'returned'
    item.save()
    
    # Отклонение всех других претензий на этот предмет
    Claim.objects.filter(item=item).exclude(pk=claim.pk).update(status='rejected')
    
    # Отправка уведомления пользователю, чья претензия была одобрена
    send_notification(
        user=claim.user,
        subject='Ваша претензия одобрена',
        message=f'Ваша претензия на предмет "{item.title}" была одобрена. Свяжитесь с владельцем объявления для дальнейших действий.'
    )
    
    messages.success(request, 'Претензия одобрена, статус объявления обновлен.')
    return redirect('manage-claims', pk=item.pk)

@login_required
def reject_claim(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    item = claim.item
    
    # Проверка, что текущий пользователь является владельцем объявления
    if item.user != request.user:
        messages.error(request, 'У вас нет прав на это действие.')
        return redirect('home')
    
    # Обновление статуса претензии
    claim.status = 'rejected'
    claim.save()
    
    # Отправка уведомления пользователю, чья претензия была отклонена
    send_notification(
        user=claim.user,
        subject='Ваша претензия отклонена',
        message=f'Ваша претензия на предмет "{item.title}" была отклонена.'
    )
    
    messages.success(request, 'Претензия отклонена.')
    return redirect('manage-claims', pk=item.pk)

@login_required
def admin_dashboard(request):
    # Проверяем, имеет ли пользователь права администратора
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для доступа к этой странице.')
        return redirect('home')
    
    # Получаем неподтвержденные объявления
    unmoderated_items = Item.objects.filter(is_moderated=False).order_by('-date_posted')
    
    # Получаем статистику
    all_items_count = Item.objects.count()
    lost_items_count = Item.objects.filter(status='lost').count()
    found_items_count = Item.objects.filter(status='found').count()
    returned_items_count = Item.objects.filter(status='returned').count()
    users_count = User.objects.count()
    claims_count = Claim.objects.count()
    
    context = {
        'unmoderated_items': unmoderated_items,
        'all_items_count': all_items_count,
        'lost_items_count': lost_items_count,
        'found_items_count': found_items_count,
        'returned_items_count': returned_items_count,
        'users_count': users_count,
        'claims_count': claims_count,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def approve_item(request, pk):
    # Проверяем, имеет ли пользователь права администратора
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для доступа к этой странице.')
        return redirect('home')
    
    item = get_object_or_404(Item, pk=pk)
    item.is_moderated = True
    item.save()
    
    # Отправляем уведомление владельцу объявления
    send_notification(
        user=item.user,
        subject='Ваше объявление одобрено',
        message=f'Ваше объявление "{item.title}" было проверено и одобрено модератором.'
    )
    
    messages.success(request, f'Объявление "{item.title}" успешно одобрено.')
    return redirect('admin-dashboard')

@login_required
def reject_item(request, pk):
    # Проверяем, имеет ли пользователь права администратора
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для доступа к этой странице.')
        return redirect('home')
    
    item = get_object_or_404(Item, pk=pk)
    
    # Здесь мы можем выбрать, удалять ли объявление или оставлять неподтвержденным
    # В данном примере просто отмечаем, что оно не прошло модерацию
    
    # Отправляем уведомление владельцу объявления
    send_notification(
        user=item.user,
        subject='Ваше объявление отклонено',
        message=f'Ваше объявление "{item.title}" было проверено и отклонено модератором.'
    )
    
    messages.warning(request, f'Объявление "{item.title}" было отклонено.')
    return redirect('admin-dashboard')