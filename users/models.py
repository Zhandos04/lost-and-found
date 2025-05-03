from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Адрес')
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

# Сигнал для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)