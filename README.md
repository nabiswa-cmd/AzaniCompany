# AZANI Internet Service Provider Information System

A fully-featured Django-based Database Management System for **Azani Company**,
which provides internet services and infrastructure to learning institutions in Kenya.


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
© 2026 Azani Company Ltd. All rights reserved.
