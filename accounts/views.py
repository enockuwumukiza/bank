from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse,HttpResponseForbidden
from django.template import loader
from django.contrib import messages
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.decorators import login_required
from decimal import Decimal,InvalidOperation
from .models import Account,Transaction,Loan
from .forms import LoanApplicationForm


def new_account(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        account_type = request.POST.get('account_type')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('account') 

        
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('account')

        account = Account.objects.create_user(
            email=email, 
            full_name=full_name, 
            phone=phone, 
            password=password
        )

        login(request, account)
        
        messages.success(request, 'Account created successfully!')
        return redirect('dashboard') 

    return render(request, 'account.html') 

def home(request):
    return render(request, 'home.html')

def user_logout(request):
    logout(request)  
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')  


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')  # Redirect to a dashboard or homepage
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'login.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        user_account = request.user
        user_account.refresh_from_db()  
        user_name = user_account.full_name
        balance = user_account.balance
        
    else:
        user_name = "Guest"
        balance = 0.00  
        
    loan = Loan.objects.filter(user=request.user).last()  # or your relevant logic
    current_loan = loan.amount if loan else 0

    # Add loan amount to context
    context = {
        'balance': request.user.balance,
        'loan_amount': current_loan,
    } 

    return render(request, 'dashboard.html', {"user_name": user_name, "balance": balance, 'context':context})
    



def deposit(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount or Decimal(amount) <= 0:
            messages.error(request, 'Invalid deposit amount')
            return redirect('deposit')
        
       
        user_account = request.user

        # Update the balance
        user_account.balance += Decimal(amount)
        user_account.save()

        # Create a deposit transaction record
        Transaction.objects.create(account=user_account, transaction_type=Transaction.DEPOSIT, amount=Decimal(amount))

        messages.success(request, f'Deposited ${amount} successfully!')
        

        return redirect('dashboard')
    return render(request, 'deposit.html')

def withdraw(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        # Check if the amount is valid 
        if not amount or Decimal(amount) <= 0:
            messages.error(request, 'Invalid withdrawal amount')
            return redirect('withdraw')  
        
        
        user_account = request.user

        
        if user_account.balance < Decimal(amount):
            messages.error(request, f'Insufficient balance -- your balance is Rwf {user_account.balance}')
            return redirect('withdraw')  
        
        # Update the balance
        user_account.balance -= Decimal(amount)
        user_account.save()

        # Create a withdrawal transaction record
        Transaction.objects.create(account=user_account, transaction_type=Transaction.WITHDRAWAL, amount=Decimal(amount))

        messages.success(request, f'Withdrawn Rwf {amount} successfully!')
        return redirect('dashboard')  # Redirect to the dashboard after a successful withdrawal
    return render(request, 'withdraw.html')

@login_required
def loan_application(request):
    """Handles the loan application form."""
    loan = None  # Initialize the loan variable

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            # Access the loan amount from the form
            loan_amount = form.cleaned_data['amount']  # This is how to access the loan amount
            
            # Optional: Check if the amount is valid (e.g., greater than zero)
            if loan_amount <= 0:
                messages.error(request, "Loan amount must be greater than zero.")
                return redirect('loan')

            # Set the user for the loan application
            loan = form.save(commit=False)
            loan.user = request.user

            # Get the current loan balance for the user (if any)
            current_loan = Loan.objects.filter(user=request.user).last()
            
            # If there is an existing loan, add the requested loan amount to the existing loan balance
            if current_loan:
                loan.amount += current_loan.amount  # Add to the existing loan balance
            # Else, set the loan amount to the requested amount if no existing loan is found
            else:
                loan.amount = loan_amount

            loan.save()

            messages.success(request, "Your loan application has been submitted successfully!")
            return redirect('dashboard')  # Redirect to a success page or list of loans
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoanApplicationForm()

    return render(request, 'loan.html', {'form': form, 'loan': loan})

@login_required
def pay_loan(request):
    """Handles the loan payment form."""
    if request.method == 'POST':
        try:
            # Convert payment amount to Decimal for precision
            payment_amount = Decimal(request.POST.get('amount'))
            
            if payment_amount <= 0:
                messages.error(request, "Payment amount must be greater than zero.")
                return redirect('pay_loan')
            
            # Get the current loan for the user
            current_loan = Loan.objects.filter(user=request.user).last()
            
            if not current_loan:
                messages.error(request, "No loan found for the user.")
                return redirect('dashboard')  # Redirect to a different page
            
            if current_loan.amount <= 0:
                messages.error(request, "You have already paid off your loan.")
                return redirect('dashboard')  # Redirect to a different page

            # Check if the payment amount is greater than or equal to the loan balance
            if payment_amount >= current_loan.amount:
                # If the payment is greater than or equal to the loan balance, mark loan as fully paid
                current_loan.amount = Decimal('0.00')  # Set to zero as a Decimal
                current_loan.save()
                messages.success(request, "Your loan has been fully paid!")
            else:
                # Otherwise, reduce the loan balance
                current_loan.amount -= payment_amount
                current_loan.save()
                messages.success(request, "Your payment was successful. Loan balance updated.")

            return redirect('dashboard')  # Redirect to a success page or dashboard

        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid payment amount. Please enter a valid number.")
            return redirect('pay_loan')

    return render(request, 'pay_loan.html')
