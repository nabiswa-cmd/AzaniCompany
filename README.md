# AZANI Internet Service Provider Information System

A fully-featured Django-based Database Management System for **Azani Company**,
which provides internet services and infrastructure to learning institutions in Kenya.

---

## Quick Start (4 Commands)

```bash
# 1. Install Django
pip install -r requirements.txt

# 2. Apply migrations (creates the database)
cd azani
python manage.py migrate

# 3. Load demo data (12 institutions, all scenarios)
python manage.py seed_demo_data

# 4. Create admin user, then run
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.
Admin panel: **http://127.0.0.1:8000/admin/**

---

## Business Rules Implemented

### Fees

| Fee | Amount (KSh) |
|---|---|
| Registration Fee | 8,500 |
| Installation Fee | 10,000 |
| Personal Computer (each) | 40,000 |
| Overdue Fine | 15% of monthly bill |
| Reconnection Fee | 1,000 |
| Bandwidth Upgrade Discount | 10% off new plan |

### Bandwidth Plans

| Bandwidth | Monthly Cost (KSh) |
|---|---|
| 4 MBPS | 1,200 |
| 10 MBPS | 2,000 |
| 20 MBPS | 3,500 |
| 25 MBPS | 4,000 |
| 50 MBPS | 7,000 |

### LAN Node Pricing

| Nodes | Cost (KSh) |
|---|---|
| 2 – 10 | 10,000 |
| 11 – 20 | 20,000 |
| 21 – 40 | 30,000 |
| 41 – 100 | 40,000 |

---

## Demo Data (seed_demo_data)

Running `python manage.py seed_demo_data` creates **12 institutions** covering every scenario:

| Institution | Type | Status | Notes |
|---|---|---|---|
| Nairobi West Primary School | PRIMARY | INSTALLED | 10 MBPS, all paid |
| Mombasa Junior Academy | JUNIOR | INSTALLED | Upgraded 10→20 MBPS (10% discount) |
| Kisumu Senior High School | SENIOR | INSTALLED | 25 MBPS, last month OVERDUE |
| Nakuru Technical College | COLLEGE | INSTALLED | 50 MBPS, fully paid |
| Thika Road Junior School | JUNIOR | DISCONNECTED | Failed to pay, disconnected |
| Eldoret Primary School | PRIMARY | NEEDS_INFRA | Buying 10 PCs + 8 LAN nodes |
| Kisii Senior Academy | SENIOR | READY | Awaiting installation payment |
| Machakos Girls College | COLLEGE | PENDING | Just registered, not yet assessed |
| Kajiado Primary School | PRIMARY | INSTALLED | 4 MBPS (smallest plan) |
| Meru University College | COLLEGE | INSTALLED | Upgraded 20→50 MBPS (10% discount) |
| Garissa Junior Secondary | JUNIOR | NEEDS_INFRA | Needs 15 PCs + 12 LAN nodes |
| Nakuru Senior School | SENIOR | INSTALLED | 20 MBPS, 2 months OVERDUE |

---

## Features

### Institution Management
- Register institutions with full contact person details
- Track through the full lifecycle: PENDING → ASSESSED → READY/NEEDS_INFRA → INSTALLED

### Payment Capture
- Registration fees (KSh 8,500)
- PC and LAN infrastructure purchases
- Installation fees (KSh 10,000)
- Monthly internet payments
- Overdue fines (auto-calculated at 15%)
- Reconnection fees (KSh 1,000)

### Billing System
- Generate monthly bills for all active institutions
- Apply 15% overdue fines for late payments
- Auto-disconnect institutions past the 10th of the next month
- Reconnection fee charged when service restored

### Reports (all printable)
1. **Registered Institutions** — grouped by type
2. **Defaulters** — overdue/disconnected with amounts
3. **Disconnections** — institutions with service issues
4. **Infrastructure Requirements** — PC and LAN needs per institution
5. **Monthly Charges** — revenue by institution category
6. **Service Aggregate** — all charges per institution
7. **Installation Cost** — full cost breakdown per institution

---

## Project Structure

```
azani/
├── manage.py
├── azani/                  ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/                   ← Main application
    ├── models.py           ← 6 database models
    ├── views.py            ← 25 views with full business logic
    ├── forms.py            ← All forms
    ├── urls.py             ← 22 URL routes
    ├── admin.py            ← Admin panel config
    ├── migrations/
    │   └── 0001_initial.py
    ├── management/
    │   └── commands/
    │       └── seed_demo_data.py   ← 12 demo institutions
    └── templates/core/     ← 23 HTML templates
```

---

## Database Models

| Model | Purpose |
|---|---|
| `Institution` | Core record — name, type, county, status, bandwidth |
| `ContactPerson` | Contact details for institution representative |
| `SiteAssessment` | Site visit findings — users, computers, LAN |
| `Payment` | All financial transactions (7 payment types) |
| `BandwidthSubscription` | Bandwidth history with upgrade discounts |
| `MonthlyBilling` | Monthly bill with fine and reconnection tracking |

---

## URL Reference

| URL | Purpose |
|---|---|
| `/` | Dashboard |
| `/institutions/` | All institutions |
| `/institutions/register/` | Register new institution |
| `/institutions/<id>/` | Institution detail |
| `/institutions/<id>/edit/` | Edit institution |
| `/institutions/<id>/assess/` | Site assessment |
| `/institutions/<id>/subscription/` | Bandwidth management |
| `/institutions/<id>/pay/registration/` | Pay registration fee |
| `/institutions/<id>/pay/installation/` | Pay installation fee |
| `/institutions/<id>/pay/infrastructure/` | Pay PC/LAN costs |
| `/billing/` | Monthly bills list |
| `/billing/generate/` | Generate bills |
| `/billing/apply-fines/` | Apply overdue fines |
| `/billing/<id>/pay/` | Pay a bill |
| `/reports/` | Reports home |
| `/reports/registered/` | Registered institutions |
| `/reports/defaulters/` | Defaulters report |
| `/reports/disconnected/` | Disconnection report |
| `/reports/infrastructure/` | Infrastructure report |
| `/reports/monthly-charges/` | Monthly charges |
| `/reports/service-aggregate/<id>/` | Service aggregate |
| `/reports/installation-cost/<id>/` | Installation cost |
| `/admin/` | Django admin panel |

---

© 2026 Azani Company Ltd. All rights reserved.
