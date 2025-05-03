from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = (
        ('lost', 'Утеряно'),
        ('found', 'Найдено'),
        ('claimed', 'Востребовано'),
        ('returned', 'Возвращено владельцу'),
    )
    
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    ai_description = models.TextField(verbose_name='AI-описание', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now, verbose_name='Дата публикации')
    date_lost_found = models.DateField(verbose_name='Дата потери/находки')
    location = models.CharField(max_length=200, verbose_name='Место')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    image = models.ImageField(upload_to='items/', verbose_name='Изображение', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lost', verbose_name='Статус')
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')
    is_moderated = models.BooleanField(default=False, verbose_name='Проверено модератором')
    
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['-date_posted']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'pk': self.pk})

class Claim(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Подтверждено'),
        ('rejected', 'Отклонено'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims', verbose_name='Предмет')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    description = models.TextField(verbose_name='Описание претензии')
    proof = models.TextField(verbose_name='Доказательство владения')
    date_claimed = models.DateTimeField(default=timezone.now, verbose_name='Дата претензии')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')
    
    class Meta:
        verbose_name = 'Претензия'
        verbose_name_plural = 'Претензии'
        ordering = ['-date_claimed']
    
    def __str__(self):
        return f'Претензия {self.user.username} на {self.item.title}'