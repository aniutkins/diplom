
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
        path('exchange/<int:item_id>/', views.request_exchange, name='request_exchange'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add-item/', views.add_item, name='add_item'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('incoming-requests/', views.incoming_requests, name='incoming_requests'),
path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
path('decline-request/<int:request_id>/', views.reject_exchange, name='decline_request'),
path('my-items/', views.my_items, name='my_items'),
path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
path('my-exchanges/', views.my_exchanges, name='my_exchanges'),
path('accept/<int:request_id>/', views.accept_exchange, name='accept_exchange'),
path('reject/<int:request_id>/', views.reject_exchange, name='reject_exchange'),
path('profile/', views.profile, name='profile'),
path('requests-to-me/', views.requests_to_me, name='requests_to_me'),
path('edit-profile/', views.edit_profile, name='edit_profile'),
path('request/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),
path('user/<int:user_id>/', views.user_profile, name='user_profile'),
path('chat/<int:user_id>/', views.chat, name='chat'),
path('my-chats/', views.my_chats, name='my_chats'),
path('request/<int:item_id>/', views.request_exchange, name='request_exchange'),
]