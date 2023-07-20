from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path("", views.personal_dashboard_index, name="index"),
    path('personal_dashboard/', views.personal_dashboard_index, name='personal_dashboard_index'),
    # KADA_SHBOARD
    path('kada_shboard/', views.kadashboard_index, name='create_event'),
    path('kada_shboard/create_event/', views.create_event, name='create_event'),
    path("kada_shboard/<slug:event_slug>/detail", views.event_detail, name="event_detail"),
    path('create_expense/<slug:event_slug>', views.create_expense, name='create_expense'),
    path('<str:event_slug>/edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('save_and_redirect_expense/', views.save_and_redirect_expense, name='save_and_redirect_expense'),

    # ACCOUNTS
    path('account/', views.account, name='account'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('update_account/', views.update_account, name='update_account'),
]
