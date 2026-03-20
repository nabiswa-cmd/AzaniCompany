"""
AZANI ISPO – Views
Full business logic: registration, payments, billing, reports.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import (Institution, ContactPerson, SiteAssessment,
                     Payment, BandwidthSubscription, MonthlyBilling,
                     BANDWIDTH_COSTS, REGISTRATION_FEE, INSTALLATION_FEE,
                     PC_UNIT_COST, RECONNECTION_FEE, OVERDUE_FINE_RATE)
from .forms import (InstitutionForm, ContactPersonForm, SiteAssessmentForm,
                    BandwidthSubscriptionForm, GenerateBillsForm, SearchForm, new_receipt)


# ── Dashboard ──────────────────────────────────────────────────────────────────
def dashboard(request):
    insts   = Institution.objects.all()
    today   = date.today()
    cur_mon = today.replace(day=1)

    monthly_revenue = MonthlyBilling.objects.filter(
        billing_month=cur_mon, status='PAID').aggregate(t=Sum('total_amount'))['t'] or Decimal('0')

    defaulters_count = MonthlyBilling.objects.filter(
        status__in=['OVERDUE','DISCONNECTED']).values('institution').distinct().count()

    recent_payments = Payment.objects.filter(
        status='PAID').select_related('institution').order_by('-payment_date')[:10]

    revenue_by_type = []
    for code, label in [('PRIMARY','Primary'),('JUNIOR','Junior'),('SENIOR','Senior'),('COLLEGE','College')]:
        rev = MonthlyBilling.objects.filter(
            institution__institution_type=code, status='PAID'
        ).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        revenue_by_type.append({
            'type': label,
            'revenue': rev,
            'count': insts.filter(institution_type=code).count(),
        })

    cutoff = today - timedelta(days=10)
    upcoming_disconnections = MonthlyBilling.objects.filter(
        status='OVERDUE', due_date__lt=cutoff
    ).select_related('institution')[:5]

    return render(request,'core/dashboard.html',{
        'total_institutions':      insts.count(),
        'active_institutions':     insts.filter(connection_status='INSTALLED').count(),
        'disconnected_institutions': insts.filter(connection_status='DISCONNECTED').count(),
        'pending_institutions':    insts.filter(connection_status='PENDING').count(),
        'monthly_revenue':         monthly_revenue,
        'defaulters_count':        defaulters_count,
        'recent_payments':         recent_payments,
        'revenue_by_type':         revenue_by_type,
        'upcoming_disconnections': upcoming_disconnections,
    })


# ── Institution list ───────────────────────────────────────────────────────────
def institution_list(request):
    form  = SearchForm(request.GET)
    insts = Institution.objects.select_related('contact_person','site_assessment').all()
    if form.is_valid():
        q     = form.cleaned_data.get('q')
        itype = form.cleaned_data.get('institution_type')
        stat  = form.cleaned_data.get('status')
        if q:     insts = insts.filter(Q(name__icontains=q)|Q(county__icontains=q)|Q(email__icontains=q))
        if itype: insts = insts.filter(institution_type=itype)
        if stat:  insts = insts.filter(connection_status=stat)
    return render(request,'core/institution_list.html',{'institutions':insts,'form':form})


# ── Register institution ───────────────────────────────────────────────────────
def institution_register(request):
    if request.method == 'POST':
        iform = InstitutionForm(request.POST)
        cform = ContactPersonForm(request.POST)
        if iform.is_valid() and cform.is_valid():
            inst         = iform.save()
            contact      = cform.save(commit=False)
            contact.institution = inst
            contact.save()
            # Create registration fee payment record (UNPAID)
            Payment.objects.create(
                institution=inst, payment_type='REGISTRATION',
                amount=REGISTRATION_FEE, status='UNPAID',
                receipt_number=new_receipt(),
                description='Registration fee – payable upon enrolment',
                due_date=date.today()+timedelta(days=7),
            )
            messages.success(request,
                f"'{inst.name}' registered! Registration fee of KSh {REGISTRATION_FEE:,.0f} has been billed.")
            return redirect('institution_detail', pk=inst.pk)
    else:
        iform = InstitutionForm()
        cform = ContactPersonForm()
    return render(request,'core/institution_register.html',{
        'inst_form':iform,'contact_form':cform,'registration_fee':REGISTRATION_FEE})


# ── Institution detail ─────────────────────────────────────────────────────────
def institution_detail(request, pk):
    inst    = get_object_or_404(Institution.objects.select_related('contact_person','site_assessment'), pk=pk)
    payments= inst.payments.all().order_by('-created_at')
    subs    = inst.subscriptions.all().order_by('-start_date')
    bills   = inst.monthly_bills.all().order_by('-billing_month')

    total_paid        = payments.filter(status='PAID').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_outstanding = payments.filter(status='UNPAID').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    service_aggregate = (payments.filter(status='PAID')
                         .values('payment_type').annotate(total=Sum('amount')).order_by('payment_type'))

    return render(request,'core/institution_detail.html',{
        'institution':inst, 'payments':payments, 'subscriptions':subs,
        'monthly_bills':bills, 'total_paid':total_paid,
        'total_outstanding':total_outstanding, 'service_aggregate':service_aggregate,
        'bandwidth_costs':BANDWIDTH_COSTS,
    })


# ── Edit institution ───────────────────────────────────────────────────────────
def institution_edit(request, pk):
    inst    = get_object_or_404(Institution, pk=pk)
    contact = getattr(inst,'contact_person',None)
    if request.method == 'POST':
        iform = InstitutionForm(request.POST, instance=inst)
        cform = ContactPersonForm(request.POST, instance=contact)
        if iform.is_valid() and cform.is_valid():
            iform.save()
            c = cform.save(commit=False); c.institution = inst; c.save()
            messages.success(request,"Institution updated.")
            return redirect('institution_detail', pk=pk)
    else:
        iform = InstitutionForm(instance=inst)
        cform = ContactPersonForm(instance=contact)
    return render(request,'core/institution_edit.html',{
        'institution':inst,'inst_form':iform,'contact_form':cform})


# ── Site assessment ────────────────────────────────────────────────────────────
def site_assessment(request, pk):
    inst     = get_object_or_404(Institution, pk=pk)
    existing = getattr(inst,'site_assessment',None)
    if request.method == 'POST':
        form = SiteAssessmentForm(request.POST, instance=existing)
        if form.is_valid():
            a = form.save(commit=False); a.institution = inst; a.save()
            inst.connection_status = 'READY' if a.is_ready else 'NEEDS_INFRA'
            inst.save()
            # Auto-create unpaid PC/LAN payments if purchases needed
            if a.pcs_to_purchase > 0 and not inst.payments.filter(payment_type='PC_PURCHASE').exists():
                Payment.objects.create(institution=inst, payment_type='PC_PURCHASE',
                    amount=a.pc_purchase_cost, status='UNPAID', receipt_number=new_receipt(),
                    description=f"{a.pcs_to_purchase} PC(s) @ KSh {PC_UNIT_COST:,.0f} each")
            if a.lan_nodes_to_purchase > 0 and not inst.payments.filter(payment_type='LAN_PURCHASE').exists():
                Payment.objects.create(institution=inst, payment_type='LAN_PURCHASE',
                    amount=a.lan_node_cost, status='UNPAID', receipt_number=new_receipt(),
                    description=f"{a.lan_nodes_to_purchase} LAN nodes")
            messages.success(request,"Site assessment saved.")
            return redirect('institution_detail', pk=pk)
    else:
        form = SiteAssessmentForm(instance=existing)
    return render(request,'core/site_assessment.html',{
        'institution':inst,'form':form,'existing':existing,'pc_cost':PC_UNIT_COST})


# ── Pay registration fee ───────────────────────────────────────────────────────
def pay_registration(request, pk):
    inst    = get_object_or_404(Institution, pk=pk)
    payment = inst.payments.filter(payment_type='REGISTRATION').first()
    if request.method == 'POST':
        if payment and payment.status == 'UNPAID':
            payment.status = 'PAID'
            payment.payment_date = date.today()
            payment.save()
            messages.success(request,f"Registration fee KSh {REGISTRATION_FEE:,.0f} paid. ✅")
        return redirect('institution_detail', pk=pk)
    return render(request,'core/pay_registration.html',{
        'institution':inst,'payment':payment,'registration_fee':REGISTRATION_FEE})


# ── Pay installation fee ───────────────────────────────────────────────────────
def pay_installation(request, pk):
    inst = get_object_or_404(Institution, pk=pk)
    if inst.connection_status not in ('READY','INSTALLED'):
        messages.error(request,"Institution must be assessed and marked ready first.")
        return redirect('institution_detail', pk=pk)
    if request.method == 'POST':
        Payment.objects.create(institution=inst, payment_type='INSTALLATION',
            amount=INSTALLATION_FEE, status='PAID', payment_date=date.today(),
            receipt_number=new_receipt(), description='Installation fee – site ready')
        inst.connection_status = 'INSTALLED'
        inst.subscription_start = date.today()
        inst.save()
        messages.success(request,f"Installation fee KSh {INSTALLATION_FEE:,.0f} paid. Internet activated! 🎉")
        return redirect('institution_detail', pk=pk)
    return render(request,'core/pay_installation.html',{
        'institution':inst,'installation_fee':INSTALLATION_FEE})


# ── Pay infrastructure (PCs & LAN) ────────────────────────────────────────────
def pay_infrastructure(request, pk):
    inst   = get_object_or_404(Institution, pk=pk)
    unpaid = inst.payments.filter(payment_type__in=['PC_PURCHASE','LAN_PURCHASE'], status='UNPAID')
    if request.method == 'POST':
        ids = request.POST.getlist('payment_ids')
        for pid in ids:
            try:
                p = inst.payments.get(pk=int(pid)); p.status='PAID'; p.payment_date=date.today(); p.save()
            except Payment.DoesNotExist: pass
        # If all infra paid → mark ready
        if not inst.payments.filter(payment_type__in=['PC_PURCHASE','LAN_PURCHASE'],status='UNPAID').exists():
            if inst.connection_status == 'NEEDS_INFRA':
                inst.connection_status = 'READY'; inst.save()
        messages.success(request,"Infrastructure payment(s) recorded.")
        return redirect('institution_detail', pk=pk)
    return render(request,'core/pay_infrastructure.html',{
        'institution':inst,'unpaid_payments':unpaid})


# ── Manage bandwidth subscription ──────────────────────────────────────────────
def manage_subscription(request, pk):
    inst    = get_object_or_404(Institution, pk=pk)
    cur_bw  = inst.current_bandwidth
    if request.method == 'POST':
        form = BandwidthSubscriptionForm(request.POST, current_bandwidth=cur_bw)
        if form.is_valid():
            new_bw = form.cleaned_data['bandwidth']
            sub    = BandwidthSubscription.create_subscription(inst, new_bw, cur_bw)
            verb   = "upgraded to" if sub.is_upgrade else "subscribed to"
            disc   = f" (10% discount: KSh {sub.discount_applied:,.0f} saved)" if sub.is_upgrade else ""
            messages.success(request,f"Institution {verb} {sub.get_bandwidth_display()} @ KSh {sub.monthly_cost:,.0f}/month{disc}.")
            return redirect('institution_detail', pk=pk)
    else:
        form = BandwidthSubscriptionForm(current_bandwidth=cur_bw)

    cost_table = []
    for bw, cost in BANDWIDTH_COSTS.items():
        is_upgrade  = cur_bw and bw > cur_bw
        discounted  = cost * Decimal('0.90') if is_upgrade else cost
        cost_table.append({'bandwidth':bw,'base_cost':cost,'discounted_cost':discounted,
                           'is_current':bw==cur_bw,'is_upgrade':is_upgrade})
    return render(request,'core/subscription.html',{
        'institution':inst,'form':form,'cost_table':cost_table,'current_bandwidth':cur_bw})


# ── Generate monthly bills ─────────────────────────────────────────────────────
def generate_monthly_bills(request):
    if request.method == 'POST':
        form = GenerateBillsForm(request.POST)
        if form.is_valid():
            billing_month = form.cleaned_data['billing_month'].replace(day=1)
            due_date      = form.cleaned_data['due_date']
            active = Institution.objects.filter(connection_status='INSTALLED', current_bandwidth__isnull=False)
            created = skipped = 0
            for inst in active:
                _, was_created = MonthlyBilling.objects.get_or_create(
                    institution=inst, billing_month=billing_month,
                    defaults=dict(bandwidth=inst.current_bandwidth, base_amount=inst.monthly_fee,
                                  total_amount=inst.monthly_fee, due_date=due_date, status='BILLED'))
                if was_created:
                    Payment.objects.create(
                        institution=inst, payment_type='MONTHLY', amount=inst.monthly_fee,
                        status='UNPAID', receipt_number=new_receipt(), billing_month=billing_month,
                        due_date=due_date,
                        description=f"Monthly fee – {billing_month:%B %Y} – {inst.current_bandwidth} MBPS")
                    created += 1
                else:
                    skipped += 1
            messages.success(request,f"Generated {created} bills for {billing_month:%B %Y}. {skipped} already existed.")
            return redirect('billing_list')
    else:
        form = GenerateBillsForm()
    return render(request,'core/generate_bills.html',{'form':form})


# ── Billing list ───────────────────────────────────────────────────────────────
def billing_list(request):
    bills  = MonthlyBilling.objects.select_related('institution').all()
    month  = request.GET.get('month','')
    status = request.GET.get('status','')
    if month:
        try:
            from datetime import datetime
            dt = datetime.strptime(month,'%Y-%m')
            bills = bills.filter(billing_month__year=dt.year, billing_month__month=dt.month)
        except ValueError: pass
    if status: bills = bills.filter(status=status)
    summary = bills.aggregate(
        total_billed=Sum('base_amount'), total_fines=Sum('overdue_fine'),
        total_reconnection=Sum('reconnection_fee'), total_amount=Sum('total_amount'))
    return render(request,'core/billing_list.html',{
        'bills':bills,'summary':summary,'month':month,'status_filter':status})


# ── Pay monthly bill ───────────────────────────────────────────────────────────
def pay_monthly_bill(request, bill_id):
    bill    = get_object_or_404(MonthlyBilling, pk=bill_id)
    inst    = bill.institution
    was_disconnected = inst.connection_status == 'DISCONNECTED'
    if request.method == 'POST':
        bill.status = 'PAID'; bill.payment_date = date.today()
        # Add reconnection fee if institution was disconnected
        if was_disconnected and bill.reconnection_fee == 0:
            bill.reconnection_fee = RECONNECTION_FEE
            Payment.objects.create(institution=inst, payment_type='RECONNECTION',
                amount=RECONNECTION_FEE, status='PAID', payment_date=date.today(),
                receipt_number=new_receipt(), description="Reconnection fee after disconnection")
            inst.connection_status = 'INSTALLED'; inst.save()
        bill.recalculate()
        # Mark the monthly payment record paid
        Payment.objects.filter(institution=inst, payment_type='MONTHLY',
            billing_month=bill.billing_month, status='UNPAID').update(
            status='PAID', payment_date=date.today())
        # Record overdue fine payment if applicable
        if bill.overdue_fine > 0:
            Payment.objects.create(institution=inst, payment_type='OVERDUE_FINE',
                amount=bill.overdue_fine, status='PAID', payment_date=date.today(),
                receipt_number=new_receipt(),
                description=f"Overdue fine 15% for {bill.billing_month:%B %Y}")
        inst.last_payment_date = date.today(); inst.save()
        messages.success(request,f"Bill for {bill.billing_month:%B %Y} settled. ✅")
        return redirect('institution_detail', pk=inst.pk)
    return render(request,'core/pay_monthly.html',{
        'bill':bill,'institution':inst,'was_disconnected':was_disconnected,
        'reconnection_fee':RECONNECTION_FEE})


# ── Apply overdue fines & disconnections ───────────────────────────────────────
def apply_overdue_fines(request):
    today = date.today()
    if request.method == 'POST':
        # Apply 15% fine to all overdue-but-not-yet-fined bills
        fined = 0
        for bill in MonthlyBilling.objects.filter(status='BILLED', due_date__lt=today):
            bill.overdue_fine = bill.base_amount * OVERDUE_FINE_RATE
            bill.status = 'OVERDUE'
            bill.recalculate(); fined += 1

        # Disconnect institutions whose overdue bill is still unpaid after the 10th of next month
        cutoff = today - timedelta(days=10)
        disconnected = 0
        for bill in MonthlyBilling.objects.filter(status='OVERDUE', due_date__lt=cutoff):
            bill.status = 'DISCONNECTED'; bill.disconnection_date = today; bill.save()
            bill.institution.connection_status = 'DISCONNECTED'; bill.institution.save()
            disconnected += 1

        messages.success(request,
            f"Fines applied to {fined} overdue bills. {disconnected} institution(s) disconnected.")
        return redirect('billing_list')

    overdue_count = MonthlyBilling.objects.filter(status='BILLED', due_date__lt=today).count()
    return render(request,'core/apply_fines.html',{'overdue_count':overdue_count})


# ── Reports ────────────────────────────────────────────────────────────────────
def reports_home(request):
    return render(request,'core/reports_home.html',{
        'institutions': Institution.objects.all()})

def report_registered(request):
    insts  = Institution.objects.select_related('contact_person').all().order_by('institution_type','name')
    by_type= {}
    for i in insts:
        by_type.setdefault(i.get_institution_type_display(),[]).append(i)
    return render(request,'core/report_registered.html',{
        'institutions':insts,'by_type':by_type,'total':insts.count(),'report_date':date.today()})

def report_defaulters(request):
    overdue = MonthlyBilling.objects.filter(
        status__in=['OVERDUE','DISCONNECTED']
    ).select_related('institution__contact_person').order_by('-billing_month','institution__name')
    dmap = {}
    for b in overdue:
        k = b.institution_id
        if k not in dmap:
            dmap[k] = {'institution':b.institution,'bills':[],'total_due':Decimal('0')}
        dmap[k]['bills'].append(b)
        dmap[k]['total_due'] += b.total_amount
    defaulters  = list(dmap.values())
    grand_total = sum(d['total_due'] for d in defaulters)
    return render(request,'core/report_defaulters.html',{
        'defaulters':defaulters,'grand_total':grand_total,'report_date':date.today()})

def report_disconnected(request):
    disc = Institution.objects.filter(
        connection_status='DISCONNECTED').select_related('contact_person').prefetch_related('monthly_bills')
    details = []
    for inst in disc:
        last_bill  = inst.monthly_bills.filter(status='DISCONNECTED').order_by('-billing_month').first()
        total_owed = inst.monthly_bills.filter(
            status__in=['OVERDUE','DISCONNECTED']).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        details.append({'institution':inst,'last_bill':last_bill,
                        'total_owed':total_owed,'reconnection_cost':total_owed+RECONNECTION_FEE})
    return render(request,'core/report_disconnected.html',{
        'details':details,'reconnection_fee':RECONNECTION_FEE,'report_date':date.today()})

def report_infrastructure(request):
    assessments = SiteAssessment.objects.select_related(
        'institution__contact_person').all().order_by('institution__institution_type','institution__name')
    total_pcs      = sum(a.pcs_to_purchase for a in assessments)
    total_lan      = sum(a.lan_nodes_to_purchase for a in assessments)
    total_pc_cost  = sum(a.pc_purchase_cost for a in assessments)
    total_lan_cost = sum(a.lan_node_cost for a in assessments)
    return render(request,'core/report_infrastructure.html',{
        'assessments':assessments,'total_pcs':total_pcs,'total_lan':total_lan,
        'total_pc_cost':total_pc_cost,'total_lan_cost':total_lan_cost,'report_date':date.today()})

def report_monthly_charges(request):
    bills = MonthlyBilling.objects.select_related('institution').all()
    month = request.GET.get('month','')
    if month:
        try:
            from datetime import datetime
            dt = datetime.strptime(month,'%Y-%m')
            bills = bills.filter(billing_month__year=dt.year, billing_month__month=dt.month)
        except ValueError: pass
    type_summary = []
    for code, label in [('PRIMARY','Primary School'),('JUNIOR','Junior School'),
                         ('SENIOR','Senior School'),('COLLEGE','College')]:
        tb  = bills.filter(institution__institution_type=code)
        agg = tb.aggregate(base=Sum('base_amount'),fines=Sum('overdue_fine'),
                           reconnection=Sum('reconnection_fee'),total=Sum('total_amount'),count=Count('id'))
        type_summary.append({'type':label,'count':agg['count'] or 0,
            'base':agg['base'] or Decimal('0'),'fines':agg['fines'] or Decimal('0'),
            'reconnection':agg['reconnection'] or Decimal('0'),'total':agg['total'] or Decimal('0')})
    grand = bills.aggregate(base=Sum('base_amount'),fines=Sum('overdue_fine'),
                            reconnection=Sum('reconnection_fee'),total=Sum('total_amount'))
    return render(request,'core/report_monthly_charges.html',{
        'type_summary':type_summary,'grand':grand,
        'bills':bills.order_by('-billing_month','institution__institution_type'),
        'month':month,'report_date':date.today()})

def report_service_aggregate(request, pk):
    inst    = get_object_or_404(Institution, pk=pk)
    paid    = inst.payments.filter(status='PAID')
    summary = paid.values('payment_type').annotate(total=Sum('amount'),count=Count('id')).order_by('payment_type')
    grand   = paid.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    monthly = inst.monthly_bills.all().order_by('billing_month')
    return render(request,'core/report_service_aggregate.html',{
        'institution':inst,'service_summary':summary,'grand_total':grand,
        'monthly':monthly,'report_date':date.today()})

def report_installation_cost(request, pk):
    inst       = get_object_or_404(Institution.objects.select_related('site_assessment'), pk=pk)
    assessment = getattr(inst,'site_assessment',None)
    payments   = inst.payments.filter(
        payment_type__in=['REGISTRATION','INSTALLATION','PC_PURCHASE','LAN_PURCHASE'])
    return render(request,'core/report_installation_cost.html',{
        'institution':inst,'assessment':assessment,'payments':payments,
        'registration_fee':REGISTRATION_FEE,'installation_fee':INSTALLATION_FEE,
        'report_date':date.today()})
