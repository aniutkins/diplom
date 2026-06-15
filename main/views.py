
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, ItemForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExchangeRequest
from django.db.models import Q
from .models import ExchangeRequest
from .models import UserProfile
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Message


def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    if q:
        items = items.filter(title__icontains=q)

    if category and category.isdigit():
        items = items.filter(category_id=int(category))

    if sort == "new":
        items = items.order_by('-id')
    elif sort == "old":
        items = items.order_by('id')

    return render(request, 'main/home.html', {
        'items': items,
        'categories': categories
    })
    
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'main/item_detail.html', {'item': item})



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Невірний логін або пароль')
    return render(request, 'main/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

from .forms import RegisterForm, ItemForm
from django.contrib.auth.decorators import login_required


@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            return redirect('home')
    else:
        form = ItemForm()

    return render(request, 'main/add_item.html', {'form': form})



@login_required
def request_exchange(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # заборона обміну власної речі
    if item.owner == request.user:
        messages.error(request, "Ви не можете обміняти свою річ")
        return redirect('item_detail', item_id=item.id)

    # перевірка чи запит вже існує
    existing_request = ExchangeRequest.objects.filter(
        item=item,
        requester=request.user
    ).exists()

    if existing_request:
        messages.warning(request, "Ви вже відправили запит на цю річ")
    else:
        ExchangeRequest.objects.create(
            item=item,
            requester=request.user,
            message="Хочу обмінятися цією річчю"
        )
        messages.success(request, "Запит на обмін відправлено!")

    return redirect('item_detail', item_id=item.id)
    
    
@login_required
def incoming_requests(request):
    requests = ExchangeRequest.objects.filter(item__owner=request.user)

    return render(request, 'main/incoming_requests.html', {
        'requests': requests
    })
    
@login_required
def accept_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if exchange_request.item.owner == request.user:
        exchange_request.status = 'accepted'
        exchange_request.save()

    return redirect('incoming_requests')

@login_required
def rejected_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if exchange_request.item.owner == request.user:
        exchange_request.status = 'rejected'
        exchange_request.save()

    return redirect('incoming_requests')

    
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # перевірка: тільки власник може видалити
    if item.owner != request.user:
        messages.error(request, "Ви не можете видалити чужу річ")
        return redirect('home')

    item.delete()
    messages.success(request, "Річ успішно видалена")

    return redirect('my_items')

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # тільки власник може редагувати
    if item.owner != request.user:
        messages.error(request, "Ви не можете редагувати чужу річ")
        return redirect('home')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Річ оновлено")
            return redirect('my_items')
    else:
        form = ItemForm(instance=item)

    return render(request, 'main/edit_item.html', {'form': form})



@login_required
def my_exchanges(request):
    # запити, які я відправив
    sent_requests = ExchangeRequest.objects.filter(requester=request.user)

    # запити до моїх речей
    received_requests = ExchangeRequest.objects.filter(item__owner=request.user)

    return render(request, 'main/my_exchanges.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })
    
    
@login_required
def accept_exchange(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if exchange_request.item.owner != request.user:
        messages.error(request, "Це не ваш запит")
        return redirect('my_exchanges')

    # приймаємо цей запит
    exchange_request.status = 'accepted'
    exchange_request.save()

    item = exchange_request.item
    item.available = False
    item.save()

    # ❗ ВІДХИЛЯЄМО ВСІ ІНШІ
    ExchangeRequest.objects.filter(
        item=item
    ).exclude(id=exchange_request.id).update(status='rejected')

    messages.success(request, "Обмін прийнято!")

    return redirect('my_exchanges')

@login_required
def reject_exchange(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if exchange_request.item.owner != request.user:
        messages.error(request, "Це не ваш запит")
        return redirect('my_exchanges')

    exchange_request.status = 'rejected'
    exchange_request.save()

    messages.success(request, "Обмін відхилено")

    return redirect('my_exchanges')


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    my_items = Item.objects.filter(owner=request.user)
    my_requests = ExchangeRequest.objects.filter(requester=request.user)
    requests_to_me = ExchangeRequest.objects.filter(item__owner=request.user)

    return render(request, 'main/profile.html', {
        'profile': profile,
        'my_items': my_items,
        'my_requests': my_requests,
        'requests_to_me': requests_to_me
    })
  
@login_required
def my_items(request):
    items = Item.objects.filter(owner=request.user)
    return render(request, 'main/my_items.html', {'items': items})


@login_required
def my_requests(request):
    requests = ExchangeRequest.objects.filter(requester=request.user)
    return render(request, 'main/my_requests.html', {'requests': requests})


@login_required
def requests_to_me(request):
    requests = ExchangeRequest.objects.filter(item__owner=request.user)
    return render(request, 'main/requests_to_me.html', {'requests': requests})

from .forms import ProfileForm

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST,  request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, "Профіль оновлено!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'main/edit_profile.html', {'form': form})




@login_required
def update_request_status(request, request_id, action):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if exchange_request.item.owner != request.user:
        messages.error(request, "У вас немає доступу")
        return redirect('home')

    if action == 'accept':
        exchange_request.status = 'accepted'
        exchange_request.item.available = False
        exchange_request.item.save()

        ExchangeRequest.objects.filter(item=exchange_request.item)\
            .exclude(id=exchange_request.id)\
            .update(status='rejected')

        messages.success(request, "Запит прийнято ✅")

    elif action == 'reject':
        exchange_request.status = 'rejected'
        messages.info(request, "Запит відхилено ❌")

    exchange_request.save()

    return redirect('requests_to_me')

from .models import UserProfile

def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    profile, _ = UserProfile.objects.get_or_create(user=user)

    items = Item.objects.filter(owner=user, available=True)

    return render(request, 'main/user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'items': items
    })
    
from .models import Message
from django.db.models import Q

@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        text = request.POST.get('text')

        if text:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text
            )
            return redirect('chat', user_id=other_user.id)

    return render(request, 'main/chat.html', {
        'chat_messages': messages,
        'other_user': other_user
    })
    
@login_required
def my_chats(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    )

    users = []

    for msg in messages:
        if msg.sender != request.user and msg.sender not in users:
            users.append(msg.sender)
        if msg.receiver != request.user and msg.receiver not in users:
            users.append(msg.receiver)

    return render(request, 'main/my_chats.html', {
        'users': users
    })