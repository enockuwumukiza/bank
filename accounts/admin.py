from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Transaction, Loan

class AccountAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'phone', 'account_type', 'balance', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('email', 'full_name', 'phone')
    list_filter = ('is_active', 'is_staff', 'account_type')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'account_type', 'balance')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_admin')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    readonly_fields = ('last_login',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'account_type', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

    # Remove filter_horizontal for 'groups' and 'user_permissions' since they're not part of your model
    filter_horizontal = ()  # Empty tuple means no fields will be horizontally filtered

# Register the Account model with the custom admin class
admin.site.register(Account, AccountAdmin)

# Register other models (Transaction and Loan) as well
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'timestamp')
    search_fields = ('account__email', 'transaction_type')
    list_filter = ('transaction_type',)
    ordering = ('-timestamp',)

admin.site.register(Transaction, TransactionAdmin)

class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'is_active')
    search_fields = ('user__full_name', 'user__email')
    list_filter = ('is_active',)
    ordering = ('-amount',)

admin.site.register(Loan, LoanAdmin)
