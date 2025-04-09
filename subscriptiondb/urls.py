from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subscriptions/', views.list_subscriptions, name='subscriptions'),
    path('add-subscription/', views.add_subscription, name='add_subscription'),
    path('subscriptions/delete/<str:key>/', views.delete_subscription, name='delete_subscription'),
path('subscriptions/edit/<str:key>/', views.edit_subscription, name='edit_subscription'),
path('contact_us/', views.contact_us, name='contact_us'),

path('thank_you/', views.thank_you, name='thank_you'),


path('logout/', views.logout_view, name='logout'),
]