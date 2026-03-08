<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: N/A (first fill from template)
Added sections:
  - Core Principles (5 principles defined)
  - Technology Stack Constraints
  - Development Workflow
  - Governance
Removed sections: none
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ reviewed — "Constitution Check" section aligns with principles
  - .specify/templates/spec-template.md ✅ reviewed — FR/SC structure compatible
  - .specify/templates/tasks-template.md ✅ reviewed — phase structure compatible
  - .specify/templates/agent-file-template.md ✅ reviewed — no conflicting references
Follow-up TODOs: none
-->

# ShipInfo Constitution

## Core Principles

### I. Data Integrity First

All data ingested from external ferry company websites via scraping MUST be validated and
sanitized before it is stored in the database. Raw HTML or unvalidated text MUST NOT flow
directly into `RawScrapedData` or downstream entities without at least type-checking and
null-safety guards.

- Scraping results MUST be checked for structural completeness before a DB write is attempted.
- Missing or malformed fields MUST be logged and the record flagged, not silently dropped.
- Duplicate records MUST be detected via idempotency keys before insert/update.

**Rationale**: Ferry operation data directly affects user safety decisions. Corrupt or
incomplete data is worse than no data.

### II. Layered Architecture (NON-NEGOTIABLE)

The three runtime layers — **Scraping (Python)**, **Persistence (MySQL)**, and
**API/Web (Symfony)** — MUST remain decoupled. Cross-layer coupling is a violation.

- Python scrapers MUST NOT contain business logic; they write raw records only.
- Symfony MUST NOT contain scraping logic; it reads and serves processed data only.
- Database schema changes MUST go through Symfony migrations — Python scripts MUST NOT
  alter schema directly.

**Rationale**: Enables independent scaling, testing, and replacement of each layer without
cascading rewrites.

### III. Security & Injection Prevention

Scraped content is untrusted third-party input and MUST be treated as hostile.

- All scraped strings passed to SQL MUST use parameterised queries (Doctrine ORM or
  prepared statements). Raw string interpolation into SQL is prohibited.
- Any scraped content rendered in HTML MUST be escaped via Twig's auto-escape or an
  equivalent mechanism. Manually disabling auto-escape requires explicit justification in
  the PR.
- Secrets (DB credentials, service URLs) MUST live in `.env` and MUST NOT be committed to
  the repository.

**Rationale**: OWASP Top-10 compliance. Scraped content from external sites is a common
injection vector.

### IV. Simplicity & MVP

Start with the simplest solution that satisfies the current requirement. Premature
abstraction and speculative generalisation are prohibited.

- No new abstraction layer (service class, repository, helper module) MUST be introduced
  unless at least two concrete use-cases require it.
- YAGNI: future-proofing beyond the next planned feature is out of scope.
- New Docker services MUST be justified in the PR description with a concrete current need.

**Rationale**: A small, maintainable codebase is easier to reason about and iterate on than
an over-engineered one.

### V. Observability

All scraping runs and API errors MUST be observable without requiring a debugger session.

- Python scrapers MUST emit structured log lines (at minimum: timestamp, company, URL,
  status, record count or error message) to stdout/stderr.
- Symfony MUST log unhandled exceptions and 5xx responses at ERROR level.
- Scraping failures MUST NOT fail silently; they MUST surface as non-zero exit codes or
  logged ERROR entries.

**Rationale**: The scraping pipeline runs unattended. Silent failures mean stale data
presented as current.

## Technology Stack Constraints

The following technology choices are fixed for the current phase of the project. Changes
require a documented amendment to this constitution.

| Layer | Technology | Version |
|-------|-----------|---------|
| Scraping | Python + BeautifulSoup + requests | 3.9+ |
| Backend / API | PHP + Symfony | latest stable |
| Database | MySQL | 8.0 |
| Container runtime | Docker Compose | current stable |

- The primary application language for backend logic is **PHP / Symfony**. Python is
  exclusively for scraping.
- New runtime dependencies MUST be added to the appropriate `Dockerfile` or
  `composer.json`/`requirements.txt`; ad-hoc package installs inside running containers
  are prohibited.
- Environment-specific configuration MUST use the `.env` / Symfony `.env.local` pattern.

## Development Workflow

### Change Process

1. Feature work begins with a spec (`spec.md`) capturing user stories and acceptance criteria.
2. A plan (`plan.md`) defines technical approach and passes the Constitution Check before
   implementation starts.
3. Tasks (`tasks.md`) are generated from the plan and executed in dependency order.
4. PRs MUST reference the relevant spec/plan and confirm Constitution Check compliance.

### Quality Gates

- **Before merge**: All acceptance scenarios from `spec.md` MUST be manually or
  automatically verified.
- **Scraping changes**: MUST be tested against a live or recorded fixture of the target site.
- **Schema changes**: MUST include a reversible Doctrine migration.
- **Security-sensitive changes** (auth, data exposure, injection surfaces): MUST receive
  explicit review comment approval.

### Docker-First Development

All local development MUST run inside Docker Compose to maintain environment parity.
Running application code directly on the host machine (outside Docker) is permitted only
for one-off script debugging and MUST NOT be treated as the authoritative test environment.

## Governance

This constitution supersedes all informal conventions and verbal agreements. When this
document conflicts with `CLAUDE.md`, this constitution takes precedence on architectural
decisions; `CLAUDE.md` governs AI assistant persona and workflow preferences.

### Amendment Procedure

1. Open a PR that modifies this file with a clear rationale for the change.
2. Bump the version following semantic versioning:
   - **MAJOR**: Removal or redefinition of an existing principle.
   - **MINOR**: Addition of a new principle or material expansion of an existing one.
   - **PATCH**: Wording clarification, typo fix, non-semantic refinement.
3. Update the Sync Impact Report comment at the top of this file.
4. Propagate any affected changes to `.specify/templates/` files.
5. Merge only after at least one explicit approval.

### Compliance

All PRs and code reviews MUST verify that the change does not violate any of the five Core
Principles. Violations MUST be resolved before merge, not deferred. Complexity introduced
in violation of Principle IV MUST be documented in the `Complexity Tracking` table of the
relevant `plan.md`.

**Version**: 1.0.0 | **Ratified**: 2026-03-08 | **Last Amended**: 2026-03-08
