# LV Bank RPA — Project Specification

> Production-oriented local RPA platform for automating bank statement retrieval, validation, reconciliation and import preparation for Latvian accounting systems.

---

## 1. Project Overview

**LV Bank RPA** is a Python-based local automation platform designed to automate repetitive accounting operations:

```bash
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

```

The application is designed for local execution and should not require banking credentials or private certificates to be stored in the source repository.
  
## 2. Goals
# Primary goals
- Automate bank statement retrieval.
- Support multiple Latvian banks through adapters.
- Normalize banking transactions into a common domain model.
- Validate imported statements.
- Prevent duplicate transaction imports.
- Reconcile statement opening/closing balances.
- Generate accounting-system import files.
- Maintain an audit trail.
- Archive original bank documents.
- Support scheduled execution.
- Provide deterministic and testable processing.
- Keep bank-specific implementation isolated from accounting-specific implementation.

## 3. Non-Goals
# The project does not attempt to:

execute payments;
- create or approve bank transfers;
- bypass bank authentication;
- store banking passwords in source code;
- automate CAPTCHA or MFA bypass;
- modify accounting records directly without an approved import workflow;
- replace the accounting system;
- replace bank security mechanisms.
The system is intended for read/import automation and controlled accounting integration.

## 4. Supported Platforms
# Target platforms:

Platform Status
Windows 11 Supported
Windows Server Planned
Ubuntu Linux	Supported
Debian Linux	Supported
Docker	Supported
macOS	Development only 
 
 
## 5. Architecture
The project follows a layered architecture.
~~~bash

┌───────────────────────────────────────────────┐
│                    CLI / Scheduler            │
├───────────────────────────────────────────────┤
│                    Services                   │
│ Import │ Export │ Reconciliation │ Scheduler  │
├───────────────────────────────────────────────┤
│                     Domain                    │
│ Transactions │ Statements │ Validation        │
├───────────────────────────────────────────────┤
│                  Adapters                     │
│ Banks                         Accounting      │
│ Swedbank │ SEB                Zalktis │ Jumis │
├───────────────────────────────────────────────┤
│                Infrastructure                 │
│ HTTP │ Filesystem │ Secrets │ Database        │
└───────────────────────────────────────────────┘
~~~

## 6. Repository Structure
~~~bash
lv-bank-rpa/
│
├── app/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── logging.py
│   ├── exceptions.py
│   │
│   ├── domain/
│   │   ├── models.py
│   │   ├── enums.py
│   │   ├── validators.py
│   │   └── fingerprints.py
│   │
│   ├── banks/
│   │   ├── base.py
│   │   ├── swedbank/
│   │   │   ├── client.py
│   │   │   ├── auth.py
│   │   │   ├── parser.py
│   │   │   └── schemas/
│   │   │
│   │   └── seb/
│   │       ├── client.py
│   │       ├── auth.py
│   │       ├── parser.py
│   │       └── schemas/
│   │
│   ├── accounting/
│   │   ├── base.py
│   │   │
│   │   ├── zalktis/
│   │   │   ├── exporter.py
│   │   │   ├── validator.py
│   │   │   └── schemas/
│   │   │
│   │   └── jumis/
│   │       ├── exporter.py
│   │       └── validator.py
│   │
│   ├── persistence/
│   │   ├── database.py
│   │   ├── repositories.py
│   │   └── migrations/
│   │
│   ├── services/
│   │   ├── import_service.py
│   │   ├── export_service.py
│   │   ├── reconciliation.py
│   │   └── scheduler.py
│   │
│   └── infrastructure/
│       ├── http.py
│       ├── filesystem.py
│       └── secrets.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── contract/
│
├── data/
│   ├── incoming/
│   ├── processing/
│   ├── outgoing/
│   ├── archive/
│   └── failed/
│
├── config/
│   ├── config.example.yaml
│   └── schemas/
│
├── scripts/
│   ├── install-windows.ps1
│   ├── install-linux.sh
│   └── backup.sh
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── security.yml
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── PROJECT.md
├── CHANGELOG.md
└── LICENSE
~~~

## 7. Core Components
# 7.1 Bank adapters
All banks implement a common interface:
~~~bash
class BankAdapter(ABC):

    @abstractmethod
    def get_statement(
        self,
        account_iban: str,
        date_from: date,
        date_to: date,
    ) -> Statement:
~~~

This allows the application to work with different banks without changing the core business logic.

Example:
~~~bash
BankAdapter
    │
    ├── SwedbankGatewayClient
    │
    └── SEBBalticGatewayClient
~~~

## 8. Swedbank Integration
The Swedbank integration is intended to use the bank's official Gateway/API interfaces and supported statement formats.

The implementation must be based on the technical specification supplied by the bank.

Expected responsibilities:
~~~bash
Swedbank Client
       │
       ├── Authentication
       ├── TLS / certificate handling
       ├── Request creation
       ├── Response validation
       ├── Retry handling
       ├── XML retrieval
       └── Parser
~~~
The project must not contain:
~~~bash
real certificates
private keys
production credentials
production account numbers
~~~

## 9. SEB Integration
SEB integration follows the same adapter architecture.
~~~bash
SEB Client
    │
    ├── Authentication
    ├── Certificate handling
    ├── API/Gateway communication
    ├── Response validation
    └── CAMT/XML parser
~~~

## 10. Canonical Transaction Model
All banks are converted to the same internal representation.

Example:
~~~bash
Transaction(
    bank=BankName.SWEDBANK,
    account_iban="LV...",
    transaction_id="123456",
    booking_date=date(...),
    amount=Decimal("125.50"),
    currency="EUR",
    direction=TransactionDirection.CREDIT,
    description="Customer payment",
)
~~~
This prevents bank-specific fields from leaking into the accounting layer.

##11. Money Handling
The project must never use floating-point numbers for monetary calculations.

Correct:
~~~bash
from decimal import Decimal

amount = Decimal("125.50")
~~~
Incorrect:
~~~bash
amount = 125.50
~~~
All monetary operations must use:
~~~bash
Decimal
~~~
with explicit currency handling.

## 12. Idempotency
Duplicate imports are one of the primary risks in financial automation.

Every transaction receives a deterministic fingerprint:
~~~bash
SHA-256(
    bank
    +
    account
    +
    transaction_id
    +
    booking_date
    +
    amount
    +
    currency
    +
    direction
    +
    counterpart
    +
    end_to_end_id
)
~~~
Example:
~~~bash
8a1f7f2c...
~~~
Before inserting a transaction:
~~~bash
Transaction
     │
     ▼
Generate fingerprint
     │
     ▼
Already exists?
   /       \
 yes       no
  │         │
skip      import
~~~
This makes repeated synchronization safe.

## 13. Reconciliation
Every imported statement should be reconciled before accounting export.

Formula:
~~~bash
Closing Balance =
    Opening Balance
    + Credits
    - Debits
~~~
If:
~~~bash
calculated closing != bank closing
~~~
the import is rejected.

Example:
~~~bash
Opening balance:     10,000.00 EUR
Credits:              5,000.00 EUR
Debits:              -2,000.00 EUR
Expected closing:    13,000.00 EUR
Bank closing:        13,000.00 EUR

Result: PASS
~~~
A reconciliation failure must prevent automatic export.

## 14. Accounting Integration
Accounting systems are implemented through adapters.
~~~bash
AccountingAdapter
       │
       ├── ZalktisExporter
       │
       └── JumisExporter
~~~
The accounting layer must never know whether a transaction originated from:
~~~bash
Swedbank
SEB
manual import
another bank
~~~
It receives normalized transactions only.

## 15. Zalktis
The Zalktis integration should use a supported import format corresponding to the target Zalktis version and configuration.

Potential formats may include:
~~~bash
ISO/FiDAViSta XML
CSV
other officially supported import formats
~~~
The exact formatter should be selected according to the accounting installation and import configuration.

Production implementation should include:
~~~bash
schema validation
encoding validation
date validation
currency validation
duplicate detection
required-field validation
~~~

## 16. Jumis
Jumis should be implemented through an independent adapter.
~~~bash
class JumisExporter(AccountingAdapter):
    ...
~~~
This prevents Jumis-specific formatting requirements from affecting Zalktis.

##17. File Processing Pipeline
Files move through controlled directories.
~~~bash
data/incoming/
       │
       ▼
data/processing/
       │
       ├── validation
       ├── parsing
       ├── reconciliation
       └── duplicate detection
       │
       ├───────────────┐
       ▼               ▼
data/archive/      data/failed/
       │
       ▼
data/outgoing/
~~~
A file should never be modified in-place after successful processing.

## 18. Atomic Writes
Generated files must first be written to a temporary file.
~~~bash
output.csv.tmp
      │
      ▼
flush
      │
      ▼
atomic rename
      │
      ▼
output.csv
~~~
This prevents partially written accounting files.

## 19. Configuration
Configuration is separated from source code.

Example:
~~~bash
application:
  environment: production
  timezone: Europe/Riga

database:
  url: postgresql://...

accounting:
  provider: zalktis

  zalktis:
    output_directory: ./data/outgoing/zalktis
~~~
Sensitive values must not be committed.

## 20. Secrets
The following must never be committed:
~~~bash
.env
private keys
client certificates
bank passwords
API tokens
production credentials
database passwords
~~~
Example:
~~~bash
.env.example
~~~
may contain:
~~~bash
DATABASE_URL=
SWEDBANK_ENABLED=false
SEB_ENABLED=false
~~~
but never real credentials.

## 21. Database
Development:
~~~bash
SQLite
~~~
Production:
~~~bash
PostgreSQL
~~~
The database stores metadata such as:
~~~bash
transaction fingerprint
transaction ID
bank
account
import timestamp
processing status
job ID
~~~
Raw bank documents should additionally be archived on the filesystem or controlled object storage.

##22. Auditability
Every import should be traceable.

Recommended audit information:
~~~bash
job_id
bank
account
period
source document
source hash
transaction count
new transactions
duplicates
reconciliation result
export result
timestamp
application version
~~~
Example:
~~~bash
Job:       2026-08-17-001
Bank:      SEB
Period:    2026-08-16 → 2026-08-17
Records:   143
New:       138
Duplicate: 5
Reconcile: PASS
Export:    SUCCESS
~~~

## 23. Error Handling
Errors are classified.
~~~bash
ConfigurationError
AuthenticationError
BankAPIError
StatementParseError
ReconciliationError
ExportError
~~~
The CLI should return a non-zero exit code on failure.

Example:
~~~bash
lv-bank-rpa sync
~~~
Success:
~~~bash
exit code 0
~~~
Failure:
~~~bash
exit code 1
~~~
This is important for Task Scheduler, cron, systemd and CI/CD.

## 24. Retry Policy
Transient errors may be retried.

Example:
~~~bash
attempt 1
    │
    └── failure
          │
          ▼
       2 seconds
          │
          ▼
attempt 2
          │
          └── failure
                │
                ▼
             5 seconds
                │
                ▼
attempt 3
~~~
Do not retry indefinitely.

Authentication and validation errors should generally fail immediately.

## 25. Logging
Logs should contain operational information but never secrets.

Allowed:
~~~bash
Bank: SEB
Account: LV********1234
Transactions: 145
Duration: 3.4 sec
~~~
Not allowed:
~~~bash
password=...
private_key=...
client_secret=...
full authorization token
~~~
Production logging should support structured JSON.

## 26. Security Model
# Security principles:

- least privilege;
- no credentials in Git;
- TLS verification enabled;
- certificate validation;
- encrypted secret storage where appropriate;
- restricted filesystem permissions;
- audit logs;
- immutable source documents;
- idempotent processing;
- no payment functionality;
- explicit dry-run mode.

## 27. Dry Run
The system should support:
~~~bash
lv-bank-rpa sync --dry-run
~~~
Dry run should:
~~~bash
retrieve
parse
validate
reconcile
calculate export
~~~
but should not:
~~~bash
write accounting import
commit irreversible changes
~~~
This is useful for deployment testing.

## 28. CLI
Planned commands:
~~~bash
lv-bank-rpa health
~~~
Check application health.
~~~bash
lv-bank-rpa sync
~~~
Synchronize configured bank accounts.
~~~bash
lv-bank-rpa sync --from 2026-08-01 --to 2026-08-17
~~~
Synchronize a specific period.
~~~bash
lv-bank-rpa sync --dry-run
~~~
Run without final export.
~~~bash
lv-bank-rpa reconcile
~~~
Run reconciliation.
~~~bash
lv-bank-rpa export
~~~
Generate accounting import files.
~~~bash
lv-bank-rpa archive
~~~
Archive processed source documents.

## 29. Scheduling
Windows:
~~~bash
Windows Task Scheduler
        │
        ▼
lv-bank-rpa sync
~~~
Linux:
~~~bash
systemd timer
        │
        ▼
lv-bank-rpa sync
~~~
Alternative:
~~~bash
cron
~~~
The scheduler must not contain banking business logic.

## 30. Docker
Production deployment may use:
~~~bash
Docker
    │
    ├── application
    └── PostgreSQL
~~~
Example:
~~~bash
docker compose up -d
~~~
Bank certificates and secrets should be mounted securely and never baked into the image.

## 31. Testing Strategy
The project uses several test layers.

$$ Unit tests
Test individual functions:
~~~bash
IBAN validation
fingerprints
parsers
reconciliation
validators
exporters
~~~
# Integration tests
Test:
~~~bash
Bank adapter
Database
Filesystem
Accounting exporter
~~~
# Contract tests
Validate external formats:
~~~bash
CAMT XML
bank-specific schemas
accounting import schemas
~~~
# Golden-file tests
Example:
~~~bash
input:
tests/fixtures/swedbank/statement.xml

expected:
tests/fixtures/zalktis/expected.csv
~~~

## 32. CI/CD
GitHub Actions should execute:
~~~bash
checkout
   │
   ▼
Python setup
   │
   ▼
pip install
   │
   ├── ruff
   ├── mypy
   ├── pytest
   └── security scan
~~~
Pull requests should not be merged when tests fail.

## 33. Security Scanning
Recommended tools:
~~~bash
ruff
mypy
pip-audit
bandit
GitHub Dependabot
GitHub Secret Scanning
~~~
The repository must not contain:
~~~bash
private keys
bank credentials
API tokens
real customer data
production statements
~~~

## 34. Data Protection
Bank statements can contain personal and financial information.

Therefore:

- real statements must not be committed to Git;
- fixtures must use synthetic data;
- logs must avoid personal data;
- archive permissions must be restricted;
- backups must be encrypted;
- retention policies should be defined.

## 35. Backup
Backup targets:
~~~bash
Database
Configuration
Processed source documents
Audit metadata
~~~
Do not blindly back up:
~~~bash
temporary files
processing files
logs containing secrets
~~~
Example:
~~~bash
scripts/backup.sh
~~~
should create an encrypted backup according to the deployment environment.

## 36. Operational Workflow
Typical daily operation:
~~~bash
06:00
  │
  ▼
Scheduler starts
  │
  ▼
Authenticate with bank
  │
  ▼
Download statement
  │
  ▼
Validate XML
  │
  ▼
Parse transactions
  │
  ▼
Generate fingerprints
  │
  ▼
Detect duplicates
  │
  ▼
Reconcile balances
  │
  ├── FAIL ──► data/failed/
  │
  ▼
Generate accounting file
  │
  ▼
data/outgoing/
  │
  ▼
Archive original
  │
  ▼
Audit log
~~~

## 37. Failure Recovery
If processing fails:
~~~bash
data/processing/
        │
        ▼
     ERROR
        │
        ▼
data/failed/
~~~
The original input must remain available for investigation.

A failed job should be safely retryable.

Because transaction fingerprints are deterministic, retrying the same statement should not create duplicate accounting transactions.

## 38. Production Readiness Checklist
# Application
- [ ] Configuration validation
- [ ] Structured logging
- [ ] Error classification
- [ ] Retry policy
- [ ] Timeouts
- [ ] Idempotency
- [ ] Reconciliation
- [ ] Audit trail
- [ ] Dry-run mode
# Bank integrations
- [ ] Official API/Gateway contract
- [ ] TLS validation
- [ ] Client certificate handling
- [ ] Authentication tests
- [ ] XML schema validation
- [ ] Error mapping
- [ ] Rate-limit handling
# Accounting
- [ ] Zalktis format confirmed
- [ ] Zalktis import tested
- [ ] Jumis format confirmed
- [ ] Duplicate protection
- [ ] Encoding tests
- [ ] Decimal precision tests
# Security
- [ ] No secrets in Git
- [ ] Certificate permissions
- [ ] Encrypted backups
- [ ]Secret rotation procedure
- [ ] Audit logging
- [ ] Dependency scanning
# Operations
- [ ] Windows scheduler
- [ ] Linux scheduler
- [ ] Backup
- [ ] Monitoring
- [ ] Alerting
- [ ] Recovery procedure

## 39. Development Workflow
Clone repository:
~~~bash
git clone https://github.com/mscbuild/lv-bank-rpa/
cd lv-bank-rpa
~~~
Create environment:
~~~bash
python -m venv .venv
~~~
## Activate:

# Windows
~~~bash
.venv\Scripts\Activate.ps1
~~~
# Linux/macOS
~~~bash
source .venv/bin/activate
~~~
Install:
~~~bash
pip install -e ".[dev]"
~~~
Run tests:
~~~bash
pytest
~~~
Run linter:
~~~bash
ruff check .
~~~
Run type checker:
~~~bash
mypy app
~~~
Run application:
~~~bash
lv-bank-rpa health
~~~

## 40. Git Workflow
Recommended branch model:
~~~bash
main
 │
 ├── develop
 │
 ├── feature/swedbank-api
 │
 ├── feature/seb-api
 │
 ├── feature/zalktis-export
 │
 └── fix/reconciliation
~~~

Commit examples:
~~~bash
feat(bank): add Swedbank gateway adapter
feat(bank): add SEB statement parser
feat(accounting): add Zalktis exporter
feat(core): add transaction idempotency
fix(reconciliation): handle debit sign
test(bank): add CAMT fixtures
security: harden certificate validation
docs: update deployment guide
~~~

## 41. Versioning
The project follows Semantic Versioning:
~~~bash
MAJOR.MINOR.PATCH
~~~
Example:
~~~bash
0.1.0
0.2.0
1.0.0
1.0.1
~~~
Before 1.0.0, API and database structures may change.

## 42. Release Criteria
A production release should require:
~~~bash
✓ all tests pass
✓ lint passes
✓ type checking passes
✓ security scan passes
✓ bank contract tests pass
✓ accounting import tested
✓ reconciliation tested
✓ backup tested
✓ recovery tested
✓ documentation updated
~~~
## 43. License
The project license should be selected before the first public release. `Apache-2.0`

