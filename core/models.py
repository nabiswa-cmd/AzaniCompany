"""
AZANI ISPO - Models
All database tables for the Internet Service Provider system.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

# ── Constants ──────────────────────────────────────────────────────────────────
REGISTRATION_FEE  = Decimal('8500.00')
INSTALLATION_FEE  = Decimal('10000.00')
PC_UNIT_COST      = Decimal('40000.00')
UPGRADE_DISCOUNT  = Decimal('0.10')
OVERDUE_FINE_RATE = Decimal('0.15')
RECONNECTION_FEE  = Decimal('1000.00')

BANDWIDTH_CHOICES = [(4,'4 MBPS'),(10,'10 MBPS'),(20,'20 MBPS'),(25,'25 MBPS'),(50,'50 MBPS')]
BANDWIDTH_COSTS   = {4:Decimal('1200'),10:Decimal('2000'),20:Decimal('3500'),25:Decimal('4000'),50:Decimal('7000')}

INSTITUTION_TYPES  = [('PRIMARY','Primary School'),('JUNIOR','Junior School'),('SENIOR','Senior School'),('COLLEGE','College')]
CONNECTION_STATUSES= [('PENDING','Pending Assessment'),('ASSESSED','Site Assessed'),('READY','Ready for Installation'),
                       ('NEEDS_INFRA','Needs Infrastructure'),('INSTALLED','Installed & Active'),
                       ('SUSPENDED','Suspended'),('DISCONNECTED','Disconnected')]
PAYMENT_TYPES      = [('REGISTRATION','Registration Fee'),('INSTALLATION','Installation Fee'),
                       ('PC_PURCHASE','PC Purchase'),('LAN_PURCHASE','LAN Nodes Purchase'),
                       ('MONTHLY','Monthly Internet Fee'),('OVERDUE_FINE','Overdue Fine'),('RECONNECTION','Reconnection Fee')]

# ── Institution ────────────────────────────────────────────────────────────────
class Institution(models.Model):
    name                 = models.CharField(max_length=200, unique=True)
    institution_type     = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    county               = models.CharField(max_length=100)
    sub_county           = models.CharField(max_length=100, blank=True)
    address              = models.TextField()
    phone                = models.CharField(max_length=20)
    email                = models.EmailField()
    registration_date    = models.DateField(default=timezone.now)
    connection_status    = models.CharField(max_length=20, choices=CONNECTION_STATUSES, default='PENDING')
    current_bandwidth    = models.IntegerField(choices=BANDWIDTH_CHOICES, null=True, blank=True)
    subscription_start   = models.DateField(null=True, blank=True)
    last_payment_date    = models.DateField(null=True, blank=True)
    notes                = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_institution_type_display()})"

    @property
    def monthly_fee(self):
        return BANDWIDTH_COSTS.get(self.current_bandwidth, Decimal('0')) if self.current_bandwidth else Decimal('0')

# ── Contact Person ─────────────────────────────────────────────────────────────
class ContactPerson(models.Model):
    institution  = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name='contact_person')
    title        = models.CharField(max_length=20, blank=True)
    first_name   = models.CharField(max_length=100)
    last_name    = models.CharField(max_length=100)
    designation  = models.CharField(max_length=100)
    national_id  = models.CharField(max_length=20, unique=True)
    phone        = models.CharField(max_length=20)
    email        = models.EmailField()
    alt_phone    = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        return f"{self.title} {self.first_name} {self.last_name}".strip()

# ── Site Assessment ────────────────────────────────────────────────────────────
class SiteAssessment(models.Model):
    institution            = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name='site_assessment')
    assessment_date        = models.DateField(default=timezone.now)
    assessed_by            = models.CharField(max_length=100)
    number_of_users        = models.PositiveIntegerField()
    has_computers          = models.BooleanField(default=False)
    number_of_computers    = models.PositiveIntegerField(default=0)
    has_lan                = models.BooleanField(default=False)
    number_of_lan_nodes    = models.PositiveIntegerField(default=0)
    is_ready               = models.BooleanField(default=False)
    pcs_to_purchase        = models.PositiveIntegerField(default=0)
    lan_nodes_to_purchase  = models.PositiveIntegerField(default=0)
    remarks                = models.TextField(blank=True)

    def __str__(self):
        return f"Assessment: {self.institution.name} ({self.assessment_date})"

    @property
    def pc_purchase_cost(self):
        return PC_UNIT_COST * self.pcs_to_purchase

    @property
    def lan_node_cost(self):
        n = self.lan_nodes_to_purchase
        if n == 0:      return Decimal('0')
        elif n <= 10:   return Decimal('10000')
        elif n <= 20:   return Decimal('20000')
        elif n <= 40:   return Decimal('30000')
        elif n <= 100:  return Decimal('40000')
        return Decimal('0')

    @property
    def total_infrastructure_cost(self):
        return self.pc_purchase_cost + self.lan_node_cost

    @property
    def total_installation_cost(self):
        return INSTALLATION_FEE + self.total_infrastructure_cost

# ── Payment ────────────────────────────────────────────────────────────────────
class Payment(models.Model):
    STATUS = [('PAID','Paid'),('UNPAID','Unpaid'),('PARTIAL','Partial')]

    institution      = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='payments')
    payment_type     = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount           = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    status           = models.CharField(max_length=10, choices=STATUS, default='UNPAID')
    payment_date     = models.DateField(null=True, blank=True)
    due_date         = models.DateField(null=True, blank=True)
    billing_month    = models.DateField(null=True, blank=True)
    receipt_number   = models.CharField(max_length=50, unique=True)
    description      = models.TextField(blank=True)
    overdue_fine     = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    reconnection_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_number} | {self.institution.name} | {self.get_payment_type_display()} | KSh {self.amount}"

# ── Bandwidth Subscription ─────────────────────────────────────────────────────
class BandwidthSubscription(models.Model):
    institution        = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subscriptions')
    bandwidth          = models.IntegerField(choices=BANDWIDTH_CHOICES)
    monthly_cost       = models.DecimalField(max_digits=10, decimal_places=2)
    is_upgrade         = models.BooleanField(default=False)
    previous_bandwidth = models.IntegerField(choices=BANDWIDTH_CHOICES, null=True, blank=True)
    discount_applied   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    start_date         = models.DateField(default=timezone.now)
    end_date           = models.DateField(null=True, blank=True)
    is_active          = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.institution.name} – {self.get_bandwidth_display()} @ KSh {self.monthly_cost}/mo"

    @classmethod
    def create_subscription(cls, institution, bandwidth, previous_bandwidth=None):
        base_cost  = BANDWIDTH_COSTS[bandwidth]
        is_upgrade = previous_bandwidth is not None and bandwidth > previous_bandwidth
        discount   = base_cost * UPGRADE_DISCOUNT if is_upgrade else Decimal('0')
        actual_cost= base_cost - discount

        cls.objects.filter(institution=institution, is_active=True).update(
            is_active=False, end_date=timezone.now().date())

        sub = cls.objects.create(
            institution=institution, bandwidth=bandwidth,
            monthly_cost=actual_cost, is_upgrade=is_upgrade,
            previous_bandwidth=previous_bandwidth, discount_applied=discount,
        )
        institution.current_bandwidth = bandwidth
        institution.save()
        return sub

# ── Monthly Billing ────────────────────────────────────────────────────────────
class MonthlyBilling(models.Model):
    STATUS = [('BILLED','Billed'),('PAID','Paid'),('OVERDUE','Overdue'),('DISCONNECTED','Disconnected')]

    institution       = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='monthly_bills')
    billing_month     = models.DateField()
    bandwidth         = models.IntegerField(choices=BANDWIDTH_CHOICES)
    base_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    overdue_fine      = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    reconnection_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    total_amount      = models.DecimalField(max_digits=10, decimal_places=2)
    status            = models.CharField(max_length=20, choices=STATUS, default='BILLED')
    payment_date      = models.DateField(null=True, blank=True)
    due_date          = models.DateField()
    disconnection_date= models.DateField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-billing_month','institution__name']
        unique_together = [['institution','billing_month']]

    def __str__(self):
        return f"{self.institution.name} | {self.billing_month:%B %Y} | KSh {self.total_amount}"

    def recalculate(self):
        self.total_amount = self.base_amount + self.overdue_fine + self.reconnection_fee
        self.save()
