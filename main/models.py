from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Категорії речей
class Category(models.Model):
    name = models.CharField(max_length=50)  # назва категорії
    def __str__(self):
        return self.name

# Речі, які додають користувачі
class Item(models.Model):
    title = models.CharField(max_length=100)          # назва речі
    description = models.TextField()                  # опис
    image = models.ImageField(upload_to='items/', blank=True, null=True)  # фото
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)     # чи доступна річ

    def __str__(self):
        return self.title

# Запити на обмін/отримання речі
class ExchangeRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('accepted', 'Прийнято'),
        ('rejected', 'Відхилено'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

   
