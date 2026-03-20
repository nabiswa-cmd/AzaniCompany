from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Institutions
    path('institutions/',                          views.institution_list,      name='institution_list'),
    path('institutions/register/',                 views.institution_register,  name='institution_register'),
    path('institutions/<int:pk>/',                 views.institution_detail,    name='institution_detail'),
    path('institutions/<int:pk>/edit/',            views.institution_edit,      name='institution_edit'),
    path('institutions/<int:pk>/assess/',          views.site_assessment,       name='site_assessment'),
    path('institutions/<int:pk>/subscription/',    views.manage_subscription,   name='manage_subscription'),
    path('institutions/<int:pk>/pay/registration/',views.pay_registration,      name='pay_registration'),
    path('institutions/<int:pk>/pay/installation/',views.pay_installation,      name='pay_installation'),
    path('institutions/<int:pk>/pay/infrastructure/',views.pay_infrastructure,  name='pay_infrastructure'),
    # Billing
    path('billing/',                 views.billing_list,           name='billing_list'),
    path('billing/generate/',        views.generate_monthly_bills, name='generate_monthly_bills'),
    path('billing/<int:bill_id>/pay/',views.pay_monthly_bill,      name='pay_monthly_bill'),
    path('billing/apply-fines/',     views.apply_overdue_fines,    name='apply_overdue_fines'),
    # Reports
    path('reports/',                             views.reports_home,             name='reports_home'),
    path('reports/registered/',                  views.report_registered,        name='report_registered'),
    path('reports/defaulters/',                  views.report_defaulters,        name='report_defaulters'),
    path('reports/disconnected/',                views.report_disconnected,      name='report_disconnected'),
    path('reports/infrastructure/',              views.report_infrastructure,    name='report_infrastructure'),
    path('reports/monthly-charges/',             views.report_monthly_charges,   name='report_monthly_charges'),
    path('reports/service-aggregate/<int:pk>/',  views.report_service_aggregate, name='report_service_aggregate'),
    path('reports/installation-cost/<int:pk>/',  views.report_installation_cost, name='report_installation_cost'),
]
