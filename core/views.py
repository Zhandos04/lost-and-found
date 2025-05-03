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

class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    context_object_name = 'items'
    paginate_by = 8
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lost_count'] = Item.objects.filter(status='lost').count()
        context['found_count'] = Item.objects.filter(status='found').count()
        context['returned_count'] = Item.objects.filter(status='returned').count()
        context['categories'] = Category.objects.all()
        context['search_form'] = SearchForm()
        return context
    
    def get_queryset(self):
        return Item.objects.filter(status__in=['lost', 'found']).order_by('-date_posted')

class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        status = self.kwargs.get('status', None)
        if status and status in ['lost', 'found']:
            return Item.objects.filter(status=status).order_by('-date_posted')
        return Item.objects.all().order_by('-date_posted')
    
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
                # Получаем полный путь к файлу
                image_path = form.instance.image.path
                
                # Выполняем анализ с использованием TensorFlow
                ai_description = analyze_image(image_path)
                
                # Сохраняем полученное описание
                form.instance.ai_description = ai_description
                form.instance.save()
            except Exception as e:
                print(f"Ошибка в AI анализе изображения: {str(e)}")
        
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
                # Получаем полный путь к файлу
                image_path = form.instance.image.path
                
                # Выполняем анализ с использованием TensorFlow
                ai_description = analyze_image(image_path)
                
                # Сохраняем полученное описание
                form.instance.ai_description = ai_description
                form.instance.save()
            except Exception as e:
                print(f"Ошибка в AI анализе изображения: {str(e)}")
        
        messages.success(self.request, 'Объявление успешно создано!')
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
    items = Item.objects.all().order_by('-date_posted')
    
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