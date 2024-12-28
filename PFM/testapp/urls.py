
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

    path('',views.home, name='home'),
    path('register/',views.registerUser, name='register'),
    path('login/',views.loginUser, name='login'),
    path('logout/',views.logoutUser, name='logout'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('income_report/', views.income_report, name='income_report'),
    path('expense_report/', views.expense_report, name='expense_report'),
    path('overview_report/', views.overview_report, name='overview_report'),
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/edit/<int:pk>/', views.edit_budget, name='edit_budget'),
    path('budgets/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    path('budgets/check/', views.budget_exceedance, name='check_budget_exceedance'),
    path('budget/set/', views.set_budget, name='set_budget'),
    path('backup/', views.backup_data, name='backup_data'),
    path('restore/', views.restore_data, name='restore_data')
]
