from django.urls import path, include
from django.conf.urls import handler404
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('account/', views.new_account, name='account'),
    path('login/', views.user_login, name="login"),
    path('loan/', views.loan_application, name='loan'),
    path('pay_loan/', views.pay_loan, name='pay_loan'),
    path('logout/', views.user_logout, name='logout'),
]

# handler404 = "accounts.views.not_found_view"