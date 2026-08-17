# lv-bank-rpa

## LV Bank RPA

A production-ready local RPA platform for automating bank statements and transferring data to Latvian accounting systems.

## Contents
- About the project
- Key Features
- Architecture
- Data flow
- Supported systems
- Why API/Gateway and not Selenium
- Project structure
- Production principles
- Installation
- Configuration
- Setting up banks
- Swedbank Gateway
- SEB Baltic Gateway
- Import to Zalktis
- Integration with Jumis
- Idempotency and duplicate protection
- Security
- Logging and Audit Trail
- Error Handling
- CLI
- Scheduler
- Docker
- Testing
- Monitoring
- Disaster Recovery
- Deployment
- Troubleshooting
- Roadmap
- License

## About the project

LV Bank RPA is designed for local automated exchange of banking and accounting data:
~~~
┌───────────────────────┐
│       Swedbank        │
│    Gateway / API      │
└───────────┬───────────┘
            │
            │
┌───────────▼───────────┐
│      SEB Gateway      │
│       / API            │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│     Bank Adapter      │
│   XML / JSON / CSV    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Normalization Layer   │
│ Unified Transaction   │
│        Model          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Validation Engine     │
│ Schema + Business     │
│ Rules + Reconciliation│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Idempotency Store     │
│ SQLite / PostgreSQL   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Accounting Adapter    │
├───────────────────────┤
│ Zalktis               │
│ Jumis                 │
│ Future ERP systems    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Import file / API     │
│ XML / CSV / other     │
└───────────────────────┘
~~~

The main idea of ​​the project is to separate banking integration and accounting integration.

## Key Features
# Banks
- Swedbank Gateway
- SEB Baltic Gateway
- Ability to add other banks
- Multiple account support
- Multiple company support
- Periodic statement downloads
- Repeat period retrieval without creating duplicates
# Accounting
- Zalktis
- Jumis
- Extensible architecture for other systems
# Reliability
- Idempotency
- Transaction fingerprint
- Unique `transaction_id`
- Period control
- Transaction quantity control
- Summary balance control
- Retry with exponential backoff
- Dead-letter queue for unparsed documents
- Atomic export
- Archive of source bank files
# Security
- mTLS
- client certificates
- secrets outside of Git
- lack of Internet banking passwords in the configuration
- minimum rights
- audit log
- encryption backup
- certificate rotation
# Operation
- CLI
- Windows Task Scheduler
- Linux systemd
- Docker
- health checks
- structured logging
- metrics
- dry-run
- manual re-run

## Architecture

The project uses the following principle:
~~~bash
Adapters
   ↓
Domain
   ↓
Validation
   ↓
Persistence
   ↓
Export
~~~

Banking APIs are isolated from business logic.
~~~bash
bank/
├── base.py
├── swedbank.py
└── seb.py
~~~

Accounting systems are also isolated:
~~~bash
accounting/
├── base.py
├── zalktis.py
└── jumis.py
~~~

## Data Flow
Typical production flow:
~~~bash
1. Scheduler starts the job

2. Application receives a list of active bank accounts

3. A period is defined for each account

4. Bank Adapter contacts Gateway

5. Bank document is received

6. XML/JSON schema is validated

7. Normalization is performed

8. Canonical Transaction is created

9. Duplicate/idempotency key is checked

10. Business validation is performed

11. Reconciliation is performed

12. The record is saved in the database

13. Accounting Adapter generates a file

14. The file undergoes validation

15. The file is atomically placed in the outgoing directory

16. The original bank document is archived

17. An audit event is created

18. The job receives the SUCCESS status
~~~

## Supported Systems
# Swedbank
Swedbank Gateway is used for corporate automation, not browser automation.

Swedbank states that the Gateway provides:

- automated account statements;
- account information;
- real-time information;
- integration with ERP/accounting systems;
- API;
- technical documentation;
- ISO/XSD documentation.
- 
Swedbank Gateway — official documentation and API description

Specific endpoints, certificates, and formats should be taken from the bank's current technical specifications and not hardcoded based on third-party examples.

## SEB
# SEB uses the SEB Baltic Gateway.

SEB specifies support for:

- account statements;
- statements for a specific period;
- intraday information;
- information on accounts of other banks;
- direct API connection;
- authentication certificates.
  
SEB Baltic Gateway

For direct connection, SEB specifies the following requirements:

1.develop and test a technical solution;
2.conclude a Baltic Gateway agreement;
3.prepare a certificate request;
4.activate the Gateway after completing the agreement and certificate.

## Zalktis
# Zalktis supports importing bank statements from:

- ISO XML;
- FiDAViSta XML;
- CSV;
- Swedbank CSV;
- SEB CSV;
- CSV from some other banks.
  
Zalktis — official documentation on bank statements

Therefore, production implementations should provide Zalktis with an officially supported format, not arbitrary CSV.

Recommended priority:
~~~bash
ISO / FiDAViSta XML
        ↓
If unavailable
        ↓
Official CSV file for the specific bank
~~~

## Jumis
# Jumis must have a separate AccountingAdapter.

It should not be assumed that the Zalktis file can be imported into Jumis without modification.

Architecture:
~~~bash
class AccountingAdapter(ABC):

    @abstractmethod
    def export(
        self,
        transactions: list[Transaction],
        destination: Path
    ) -> ExportResult:
~~~

In production, before implementing `JumisAdapter`, you must specify:

- Supported import format;
- Jumis version;
- Encoding;
- Separator;
- Decimal format;
- Account mapping;
- Import rules;
- Duplicate behavior.

## Project structure
~~~bash

lv-bank-rpa/
│
├── app/
│   ├── __init__.py
│   │
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
│   │   └── seb/
│   │       ├── client.py
│   │       ├── auth.py
│   │       ├── parser.py
│   │       └── schemas/
│   │
│   ├── accounting/
│   │   ├── base.py
│   │   ├── zalktis/
│   │   │   ├── exporter.py
│   │   │   ├── validator.py
│   │   │   └── schemas/
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
├── CHANGELOG.md
└── LICENSE
~~~

## Bank Certificates

Recommended structure:
~~~bash
secrets/
├── swedbank/
│   ├── client.crt
│   └── client.key
│
└── seb/
    ├── client.crt
    └── client.key
~~~
The directory must have limited permissions.
