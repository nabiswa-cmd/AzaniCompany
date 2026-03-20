from django.contrib import admin
from .models import Institution, ContactPerson, SiteAssessment, Payment, BandwidthSubscription, MonthlyBilling

admin.site.site_header = "AZANI ISPO Administration"
admin.site.site_title  = "Azani Admin"
admin.site.index_title = "Internet Service Provider Management"

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display  = ['name','institution_type','county','connection_status','current_bandwidth','registration_date']
    list_filter   = ['institution_type','connection_status','county']
    search_fields = ['name','email','phone']

@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display  = ['full_name','institution','designation','phone','email']
    search_fields = ['first_name','last_name','national_id','institution__name']

@admin.register(SiteAssessment)
class SiteAssessmentAdmin(admin.ModelAdmin):
    list_display = ['institution','assessment_date','is_ready','number_of_users','pcs_to_purchase','lan_nodes_to_purchase']
    list_filter  = ['is_ready']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ['receipt_number','institution','payment_type','amount','status','payment_date']
    list_filter   = ['payment_type','status']
    search_fields = ['receipt_number','institution__name']

@admin.register(BandwidthSubscription)
class BandwidthSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['institution','bandwidth','monthly_cost','is_upgrade','discount_applied','start_date','is_active']
    list_filter  = ['bandwidth','is_upgrade','is_active']

@admin.register(MonthlyBilling)
class MonthlyBillingAdmin(admin.ModelAdmin):
    list_display = ['institution','billing_month','base_amount','overdue_fine','reconnection_fee','total_amount','status','due_date']
    list_filter  = ['status','billing_month','institution__institution_type']
    search_fields= ['institution__name']
