# LV Bank RPA — Project Specification

> Production-oriented local RPA platform for automating bank statement retrieval, validation, reconciliation and import preparation for Latvian accounting systems.

---

## 1. Project Overview

**LV Bank RPA** is a Python-based local automation platform designed to automate repetitive accounting operations:

```text
Bank API / Gateway
       │
       ▼
┌──────────────────┐
│ Bank Adapter     │
│ Swedbank / SEB   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ XML / CAMT Parser│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Domain Model     │
│ Transactions     │
└────────┬─────────┘
         │
         ├──────────────► Idempotency
         │
         ├──────────────► Validation
         │
         └──────────────► Reconciliation
                              │
                              ▼
                     ┌─────────────────┐
                     │ Accounting      │
                     │ Adapter         │
                     └────────┬────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 Zalktis              Jumis
