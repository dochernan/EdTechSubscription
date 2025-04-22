from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('subscriptions/', views.list_subscriptions, name='subscriptions'),
    path('apps/', views.apps, name='apps'),
    path('users/', views.list_users, name='users'),
    path('faq/', views.faq, name='faq'),
    path('aiguidelines/', views.aiguidelines, name='aiguidelines'),
    path('users/delete/<str:key>/', views.delete_user, name='delete_user'),
    path('users/edit/<str:key>/', views.edit_user, name='edit_user'),
    path('add-subscription/', views.add_subscription, name='add_subscription'),
    path('subscriptions/delete/<str:key>/', views.delete_subscription, name='delete_subscription'),
    path('subscriptions/edit/<str:key>/', views.edit_subscription, name='edit_subscription'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('request/', views.request, name='request'),
    path('responsibleuse/', views.responsibleuse, name='responsibleuse'),
    path('logout/', views.logout_view, name='logout'),
    path('subscriptions/search/', views.ajax_search_subscriptions, name='ajax_search_subscriptions'),
    path('users/search/', views.ajax_search_users, name='ajax_search_users'),

]
