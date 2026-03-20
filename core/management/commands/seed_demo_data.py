"""
Management command: seed_demo_data
Usage:  python manage.py seed_demo_data

Populates the AZANI ISPO database with realistic demo data covering:
  • 12 institutions (all 4 types, all connection statuses)
  • Contact persons for each institution
  • Site assessments (infrastructure details)
  • Payment records – registration, installation, PC/LAN purchases
  • Bandwidth subscriptions (including upgrades with 10% discount)
  • Monthly billing history (paid, overdue, disconnected)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import uuid

from core.models import (
    Institution, ContactPerson, SiteAssessment,
    Payment, BandwidthSubscription, MonthlyBilling,
    BANDWIDTH_COSTS, REGISTRATION_FEE, INSTALLATION_FEE, PC_UNIT_COST,
    OVERDUE_FINE_RATE, RECONNECTION_FEE,
)


def rcp():
    """Generate a unique receipt number."""
    return f"RCP-{uuid.uuid4().hex[:8].upper()}"


today      = date.today()
last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
two_months = (last_month.replace(day=1) - timedelta(days=1)).replace(day=1)


# ── Demo data definitions ──────────────────────────────────────────────────────
DEMO = [
    # ── 1. Fully active, 10 MBPS, all paid up ──────────────────────────────
    {
        'inst': dict(name="Nairobi West Primary School", institution_type="PRIMARY",
                     county="Nairobi", sub_county="Dagoretti South",
                     address="P.O Box 1001, Nairobi", phone="+254722100001",
                     email="nwps@schools.ke", connection_status="INSTALLED", current_bandwidth=10),
        'contact': dict(title="Mrs", first_name="Grace", last_name="Wanjiku",
                        designation="Head Teacher", national_id="12345678",
                        phone="+254722100001", email="grace.wanjiku@schools.ke"),
        'assess': dict(assessed_by="Eng. John Kamau", number_of_users=120,
                       has_computers=True, number_of_computers=30,
                       has_lan=True, number_of_lan_nodes=15, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Well equipped. LAN covers all classrooms."),
        'bandwidth': 10, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'PAID'},
        ],
    },
    # ── 2. Active, upgraded 10→20 MBPS (10% discount applied) ─────────────
    {
        'inst': dict(name="Mombasa Junior Academy", institution_type="JUNIOR",
                     county="Mombasa", sub_county="Nyali",
                     address="P.O Box 2002, Nyali, Mombasa", phone="+254733200002",
                     email="mja@edu.ke", connection_status="INSTALLED", current_bandwidth=20),
        'contact': dict(title="Mr", first_name="Hassan", last_name="Mwamba",
                        designation="Principal", national_id="23456789",
                        phone="+254733200002", email="h.mwamba@mja.ke"),
        'assess': dict(assessed_by="Eng. Alice Otieno", number_of_users=200,
                       has_computers=True, number_of_computers=45,
                       has_lan=True, number_of_lan_nodes=20, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Modern computer lab. Ready for installation."),
        'bandwidth': 20, 'prev_bw': 10,   # upgraded – 10% discount
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'PAID'},
        ],
    },
    # ── 3. Senior school, 25 MBPS, OVERDUE last month ─────────────────────
    {
        'inst': dict(name="Kisumu Senior High School", institution_type="SENIOR",
                     county="Kisumu", sub_county="Kisumu Central",
                     address="P.O Box 3003, Kisumu", phone="+254744300003",
                     email="kisumuhigh@edu.ke", connection_status="INSTALLED", current_bandwidth=25),
        'contact': dict(title="Dr", first_name="Onyango", last_name="Odhiambo",
                        designation="Principal", national_id="34567890",
                        phone="+254744300003", email="onyango@kisumuhigh.ke"),
        'assess': dict(assessed_by="Eng. Peter Njoroge", number_of_users=350,
                       has_computers=True, number_of_computers=60,
                       has_lan=True, number_of_lan_nodes=30, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Large school. High bandwidth needed."),
        'bandwidth': 25, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'OVERDUE'},   # defaulter
        ],
    },
    # ── 4. College, 50 MBPS, fully paid ────────────────────────────────────
    {
        'inst': dict(name="Nakuru Technical College", institution_type="COLLEGE",
                     county="Nakuru", sub_county="Nakuru East",
                     address="P.O Box 4004, Nakuru", phone="+254755400004",
                     email="ntc@college.ke", connection_status="INSTALLED", current_bandwidth=50),
        'contact': dict(title="Prof", first_name="Samuel", last_name="Kimani",
                        designation="Principal", national_id="45678901",
                        phone="+254755400004", email="s.kimani@ntc.ke"),
        'assess': dict(assessed_by="Eng. Rose Mutua", number_of_users=800,
                       has_computers=True, number_of_computers=120,
                       has_lan=True, number_of_lan_nodes=50, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Large campus. Backbone fibre ready."),
        'bandwidth': 50, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'PAID'},
        ],
    },
    # ── 5. DISCONNECTED (failed to pay last month + fine) ──────────────────
    {
        'inst': dict(name="Thika Road Junior School", institution_type="JUNIOR",
                     county="Kiambu", sub_county="Thika",
                     address="P.O Box 5005, Thika", phone="+254766500005",
                     email="trjs@edu.ke", connection_status="DISCONNECTED", current_bandwidth=10),
        'contact': dict(title="Mrs", first_name="Wambui", last_name="Muthoni",
                        designation="Head Teacher", national_id="56789012",
                        phone="+254766500005", email="wambui@trjs.ke"),
        'assess': dict(assessed_by="Eng. David Mwangi", number_of_users=95,
                       has_computers=True, number_of_computers=20,
                       has_lan=True, number_of_lan_nodes=10, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Ready. Small school."),
        'bandwidth': 10, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'DISCONNECTED'},  # disconnected
        ],
    },
    # ── 6. NEEDS_INFRA – buying 10 PCs + 8 LAN nodes ──────────────────────
    {
        'inst': dict(name="Eldoret Primary School", institution_type="PRIMARY",
                     county="Uasin Gishu", sub_county="Eldoret",
                     address="P.O Box 6006, Eldoret", phone="+254777600006",
                     email="eldoret.primary@edu.ke", connection_status="NEEDS_INFRA",
                     current_bandwidth=None),
        'contact': dict(title="Mrs", first_name="Purity", last_name="Chebet",
                        designation="Head Teacher", national_id="67890123",
                        phone="+254777600006", email="purity.chebet@edu.ke"),
        'assess': dict(assessed_by="Eng. Faith Akinyi", number_of_users=90,
                       has_computers=False, number_of_computers=0,
                       has_lan=False, number_of_lan_nodes=0, is_ready=False,
                       pcs_to_purchase=10, lan_nodes_to_purchase=8,
                       remarks="No computers or LAN. Must purchase from Azani before installation."),
        'bandwidth': None, 'prev_bw': None,
        'bills': [],
    },
    # ── 7. READY for installation (all infra in place) ─────────────────────
    {
        'inst': dict(name="Kisii Senior Academy", institution_type="SENIOR",
                     county="Kisii", sub_county="Kisii Central",
                     address="P.O Box 7007, Kisii", phone="+254788700007",
                     email="kisii.senior@edu.ke", connection_status="READY",
                     current_bandwidth=None),
        'contact': dict(title="Mr", first_name="Benson", last_name="Ongaki",
                        designation="Principal", national_id="78901234",
                        phone="+254788700007", email="b.ongaki@kisii.ke"),
        'assess': dict(assessed_by="Eng. John Kamau", number_of_users=280,
                       has_computers=True, number_of_computers=50,
                       has_lan=True, number_of_lan_nodes=25, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="All requirements met. Awaiting installation payment."),
        'bandwidth': None, 'prev_bw': None,
        'bills': [],
    },
    # ── 8. PENDING – just registered, not yet assessed ──────────────────────
    {
        'inst': dict(name="Machakos Girls College", institution_type="COLLEGE",
                     county="Machakos", sub_county="Machakos Town",
                     address="P.O Box 8008, Machakos", phone="+254799800008",
                     email="mgc@college.ke", connection_status="PENDING",
                     current_bandwidth=None),
        'contact': dict(title="Dr", first_name="Anne", last_name="Mutua",
                        designation="Principal", national_id="89012345",
                        phone="+254799800008", email="anne.mutua@mgc.ke"),
        'assess': None,  # Not yet assessed
        'bandwidth': None, 'prev_bw': None,
        'bills': [],
    },
    # ── 9. Active, 4 MBPS (smallest plan), 2 months paid ──────────────────
    {
        'inst': dict(name="Kajiado Primary School", institution_type="PRIMARY",
                     county="Kajiado", sub_county="Kajiado North",
                     address="P.O Box 9009, Kajiado", phone="+254700900009",
                     email="kajiado.primary@edu.ke", connection_status="INSTALLED",
                     current_bandwidth=4),
        'contact': dict(title="Mr", first_name="John", last_name="Ole Ntutu",
                        designation="Head Teacher", national_id="90123456",
                        phone="+254700900009", email="john.ole@kajiado.ke"),
        'assess': dict(assessed_by="Eng. Alice Otieno", number_of_users=60,
                       has_computers=True, number_of_computers=12,
                       has_lan=True, number_of_lan_nodes=6, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Rural school. Basic connectivity sufficient for now."),
        'bandwidth': 4, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'PAID'},
        ],
    },
    # ── 10. College, upgraded 20→50 MBPS (discount applied) ───────────────
    {
        'inst': dict(name="Meru University College", institution_type="COLLEGE",
                     county="Meru", sub_county="Imenti North",
                     address="P.O Box 1010, Meru", phone="+254711101010",
                     email="muc@meru.ac.ke", connection_status="INSTALLED", current_bandwidth=50),
        'contact': dict(title="Prof", first_name="Lucy", last_name="Kirimi",
                        designation="Dean of ICT", national_id="01234567",
                        phone="+254711101010", email="l.kirimi@muc.ke"),
        'assess': dict(assessed_by="Eng. Peter Njoroge", number_of_users=1200,
                       has_computers=True, number_of_computers=200,
                       has_lan=True, number_of_lan_nodes=80, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="University campus. Upgraded from 20 MBPS to 50 MBPS."),
        'bandwidth': 50, 'prev_bw': 20,   # upgraded – 10% discount
        'bills': [
            {'month': two_months, 'status': 'PAID'},
            {'month': last_month, 'status': 'PAID'},
        ],
    },
    # ── 11. NEEDS_INFRA – buying 15 PCs + 12 LAN nodes ────────────────────
    {
        'inst': dict(name="Garissa Junior Secondary", institution_type="JUNIOR",
                     county="Garissa", sub_county="Garissa Township",
                     address="P.O Box 1111, Garissa", phone="+254722111011",
                     email="gjs@edu.ke", connection_status="NEEDS_INFRA",
                     current_bandwidth=None),
        'contact': dict(title="Mr", first_name="Mohamed", last_name="Abdi",
                        designation="Deputy Principal", national_id="11223344",
                        phone="+254722111011", email="m.abdi@gjs.ke"),
        'assess': dict(assessed_by="Eng. Faith Akinyi", number_of_users=150,
                       has_computers=False, number_of_computers=0,
                       has_lan=True, number_of_lan_nodes=5, is_ready=False,
                       pcs_to_purchase=15, lan_nodes_to_purchase=12,
                       remarks="Has partial LAN. Needs computers and additional LAN nodes."),
        'bandwidth': None, 'prev_bw': None,
        'bills': [],
    },
    # ── 12. Senior, 20 MBPS, overdue 2 months (multiple defaulter) ─────────
    {
        'inst': dict(name="Nakuru Senior School", institution_type="SENIOR",
                     county="Nakuru", sub_county="Nakuru West",
                     address="P.O Box 1212, Nakuru", phone="+254733121212",
                     email="nss@edu.ke", connection_status="INSTALLED", current_bandwidth=20),
        'contact': dict(title="Mrs", first_name="Tabitha", last_name="Njoroge",
                        designation="Principal", national_id="22334455",
                        phone="+254733121212", email="t.njoroge@nss.ke"),
        'assess': dict(assessed_by="Eng. Rose Mutua", number_of_users=310,
                       has_computers=True, number_of_computers=55,
                       has_lan=True, number_of_lan_nodes=28, is_ready=True,
                       pcs_to_purchase=0, lan_nodes_to_purchase=0,
                       remarks="Well set up. Payment delays noted."),
        'bandwidth': 20, 'prev_bw': None,
        'bills': [
            {'month': two_months, 'status': 'OVERDUE'},  # two months overdue!
            {'month': last_month,  'status': 'OVERDUE'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the AZANI ISPO database with realistic demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n🌱  Seeding AZANI ISPO demo data...\n'))

        for entry in DEMO:
            idata = entry['inst']
            inst, created = Institution.objects.get_or_create(
                name=idata['name'], defaults=idata)

            if not created:
                self.stdout.write(f'   ⏭  Skipping (exists): {inst.name}')
                continue

            self.stdout.write(f'   ✅  Creating: {inst.name}')

            # ── Contact Person ──────────────────────────────────────────────
            ContactPerson.objects.create(institution=inst, **entry['contact'])

            # ── Registration fee (always created and paid) ──────────────────
            Payment.objects.create(
                institution=inst, payment_type='REGISTRATION',
                amount=REGISTRATION_FEE, status='PAID',
                payment_date=today - timedelta(days=90),
                receipt_number=rcp(),
                description='Registration fee – paid on enrolment',
            )

            # ── Site Assessment ─────────────────────────────────────────────
            assessment = None
            if entry['assess']:
                assessment = SiteAssessment.objects.create(
                    institution=inst, **entry['assess'])

                # PC purchase payment (unpaid) if needed
                if assessment.pcs_to_purchase > 0:
                    Payment.objects.create(
                        institution=inst, payment_type='PC_PURCHASE',
                        amount=assessment.pc_purchase_cost, status='UNPAID',
                        receipt_number=rcp(),
                        description=(f"{assessment.pcs_to_purchase} PC(s) "
                                     f"@ KSh {PC_UNIT_COST:,.0f} each"),
                    )

                # LAN purchase payment (unpaid) if needed
                if assessment.lan_nodes_to_purchase > 0:
                    Payment.objects.create(
                        institution=inst, payment_type='LAN_PURCHASE',
                        amount=assessment.lan_node_cost, status='UNPAID',
                        receipt_number=rcp(),
                        description=(f"{assessment.lan_nodes_to_purchase} LAN nodes "
                                     f"(cost tier: KSh {assessment.lan_node_cost:,.0f})"),
                    )

            # ── Installation fee + bandwidth subscription (for installed/disconnected) ──
            if inst.current_bandwidth:
                bw      = inst.current_bandwidth
                prev_bw = entry['prev_bw']

                # Installation fee – paid
                Payment.objects.create(
                    institution=inst, payment_type='INSTALLATION',
                    amount=INSTALLATION_FEE, status='PAID',
                    payment_date=today - timedelta(days=75),
                    receipt_number=rcp(),
                    description='Installation fee – internet activated',
                )

                # If upgraded from a previous plan, record old subscription first
                if prev_bw:
                    old_cost = BANDWIDTH_COSTS[prev_bw]
                    BandwidthSubscription.objects.create(
                        institution=inst, bandwidth=prev_bw,
                        monthly_cost=old_cost, is_upgrade=False,
                        start_date=today - timedelta(days=75),
                        end_date=today - timedelta(days=30),
                        is_active=False,
                    )

                # Current subscription (with upgrade discount if applicable)
                base_cost   = BANDWIDTH_COSTS[bw]
                is_upgrade  = prev_bw is not None and bw > prev_bw
                discount    = base_cost * Decimal('0.10') if is_upgrade else Decimal('0')
                actual_cost = base_cost - discount

                BandwidthSubscription.objects.create(
                    institution=inst, bandwidth=bw,
                    monthly_cost=actual_cost, is_upgrade=is_upgrade,
                    previous_bandwidth=prev_bw if is_upgrade else None,
                    discount_applied=discount,
                    start_date=today - timedelta(days=75 if not is_upgrade else 30),
                    is_active=True,
                )
                inst.subscription_start = today - timedelta(days=75)
                inst.save()

                # If upgrade, log the upgrade payment note
                if is_upgrade:
                    self.stdout.write(
                        f'      ↑  Upgraded {prev_bw}→{bw} MBPS, '
                        f'discount KSh {discount:,.0f}, '
                        f'pays KSh {actual_cost:,.0f}/month')

                # ── Monthly billing history ─────────────────────────────────
                for bill_def in entry['bills']:
                    bmonth = bill_def['month']
                    bstatus= bill_def['status']

                    fine        = Decimal('0')
                    reconn_fee  = Decimal('0')
                    disconn_date= None

                    if bstatus in ('OVERDUE', 'DISCONNECTED'):
                        fine = actual_cost * OVERDUE_FINE_RATE
                    if bstatus == 'DISCONNECTED':
                        disconn_date = bmonth + timedelta(days=40)

                    total = actual_cost + fine + reconn_fee

                    mb = MonthlyBilling.objects.create(
                        institution=inst, billing_month=bmonth, bandwidth=bw,
                        base_amount=actual_cost, overdue_fine=fine,
                        reconnection_fee=reconn_fee, total_amount=total,
                        status=bstatus,
                        due_date=bmonth.replace(day=28),
                        payment_date=bmonth + timedelta(days=20) if bstatus == 'PAID' else None,
                        disconnection_date=disconn_date,
                    )

                    # Monthly payment record
                    pay_status   = 'PAID' if bstatus == 'PAID' else 'UNPAID'
                    pay_date     = bmonth + timedelta(days=20) if bstatus == 'PAID' else None

                    Payment.objects.create(
                        institution=inst, payment_type='MONTHLY',
                        amount=actual_cost, status=pay_status,
                        payment_date=pay_date, receipt_number=rcp(),
                        billing_month=bmonth,
                        due_date=bmonth.replace(day=28),
                        description=f"Monthly internet fee – {bmonth:%B %Y} – {bw} MBPS",
                    )

                    # Overdue fine payment record (unpaid for defaulters)
                    if fine > 0:
                        Payment.objects.create(
                            institution=inst, payment_type='OVERDUE_FINE',
                            amount=fine, status='UNPAID',
                            receipt_number=rcp(),
                            billing_month=bmonth,
                            description=f"Overdue fine 15% – {bmonth:%B %Y}",
                        )

                # Update last payment date for paid-up institutions
                paid_bills = [b for b in entry['bills'] if b['status'] == 'PAID']
                if paid_bills:
                    inst.last_payment_date = max(b['month'] for b in paid_bills) + timedelta(days=20)
                    inst.save()

        self.stdout.write(self.style.SUCCESS(
            '\n✅  Demo data seeded successfully!\n'
            '\nWhat was created:\n'
            '  • 12 institutions (Primary, Junior, Senior, College)\n'
            '  • Contact persons for all institutions\n'
            '  • Site assessments with infrastructure details\n'
            '  • Registration, installation, PC & LAN payments\n'
            '  • Bandwidth subscriptions (incl. upgrades with 10% discount)\n'
            '  • Monthly billing history (paid, overdue, disconnected)\n'
            '\nStatuses covered:\n'
            '  INSTALLED (7) | DISCONNECTED (1) | NEEDS_INFRA (2) | READY (1) | PENDING (1)\n'
            '\nNext steps:\n'
            '  python manage.py createsuperuser\n'
            '  python manage.py runserver\n'
            '  Open http://127.0.0.1:8000\n'
        ))
