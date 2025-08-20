# LegalRescue.ai AI Backend
---

## Table of Contents

- [Overview](#overview)
- [Core AI Capabilities](#core-ai-capabilities)
- [Legal Practice Areas](#legal-practice-areas)
- [System Features](#system-features)
- [Installation](#installation)
- [Dependencies Documentation](#dependencies-documentation)
- [API Documentation](#api-documentation)
- [Security & Compliance](#security--compliance)

---

## Overview

The LegalRescue.ai AI Backend powers seamless legal support through AI-driven case analysis, automatic categorization, intelligent form prefilling, and generation of structured legal summaries — streamlining the path from user input to actionable legal documentation.

**Technology Foundation:**
- OpenAI GPT-4o Mini for advanced legal text analysis
- Comprehensive predefined form library in JSON format
- Supabase database for scalable data management
- Flask-based RESTful API architecture
- Real-time processing with sub-second response times

---

## Core AI Capabilities

### Intelligent Case Analysis Engine

Our AI-powered analysis system provides comprehensive legal case evaluation using advanced natural language processing specifically trained for legal contexts.

**Analysis Features:**
- Sophisticated legal text processing and understanding
- Automatic case classification across 13 practice areas and 80+ subcategories
- Confidence-based scoring for quality assurance
- Key legal detail extraction and structuring
- Alternative classification suggestions for ambiguous cases
- Professional case title generation with PII protection

### Smart Form Automation System

The platform utilizes a comprehensive library of predefined legal form templates stored in structured JSON format, with AI-powered mapping of extracted case information to appropriate form fields.

**Form Processing Features:**
- Access to predefined legal form templates for all practice areas
- Intelligent extraction of relevant information from case descriptions
- Automated mapping of case details to corresponding form fields
- Multi-format field support including text, radio, checkbox, date, and numeric fields
- Contextual field population with educated determinations
- Comprehensive validation ensuring data accuracy and completeness

### Professional Case Summary Generation

Advanced AI system that creates attorney-ready case documentation by combining analysis results with completed form data.

**Documentation Features:**
- Structured professional summaries with standardized legal sections
- Integration of AI analysis with user-provided form data
- Practice-specific legal terminology and insights
- Four-section format: General Summary, Key Aspects, Potential Merits, Critical Factors
- Professional formatting suitable for client consultation and legal review

### Advanced Data Protection

Comprehensive security framework ensuring client confidentiality and regulatory compliance.

**Protection Features:**
- Automatic PII detection and removal using advanced pattern recognition
- Smart data anonymization preserving legal context
- Multi-layer input validation and sanitization
- Secure data transmission with end-to-end encryption

---

## Legal Practice Areas

Our platform provides specialized AI analysis and automated form processing across **13 comprehensive legal categories** with **80+ specialized subcategories**:

### Family Law
**Subcategories:** Adoptions • Child Custody & Visitation • Child Support • Divorce • Guardianship • Paternity • Separations • Spousal Support or Alimony

**Specialized Processing:** Relationship analysis, asset division mapping, child welfare assessments, custody arrangement optimization, financial support calculations

### Employment Law
**Subcategories:** Disabilities • Employment Contracts • Employment Discrimination • Pensions and Benefits • Sexual Harassment • Wages and Overtime Pay • Workplace Disputes • Wrongful Termination

**Specialized Processing:** Workplace incident classification, discrimination basis identification, wage calculation assistance, termination analysis, employment timeline tracking

### Criminal Law
**Subcategories:** General Criminal Defense • Environmental Violations • Drug Crimes • Drunk Driving/DUI/DWI • Felonies • Misdemeanors • Speeding and Moving Violations • White Collar Crime • Tax Evasion

**Specialized Processing:** Criminal charge classification, court timeline management, bail status tracking, criminal history organization, legal deadline monitoring

### Real Estate Law
**Subcategories:** Commercial Real Estate • Condominiums and Cooperatives • Construction Disputes • Foreclosures • Mortgages • Purchase and Sale of Residence • Title and Boundary Disputes

**Specialized Processing:** Property valuation analysis, transaction timeline management, contract analysis, title issue identification, mortgage calculation assistance

### Business & Corporate Law
**Subcategories:** Breach of Contract • Corporate Tax • Business Disputes • Buying and Selling a Business • Contract Drafting and Review • Corporations, LLCs, Partnerships, etc. • Entertainment Law

**Specialized Processing:** Entity classification, contract breach analysis, business valuation assessment, corporate structure optimization, commercial dispute resolution

### Immigration Law
**Subcategories:** Citizenship • Deportation • Permanent Visas or Green Cards • Temporary Visas

**Specialized Processing:** Immigration status classification, eligibility assessment, application timeline management, documentation requirement analysis

### Personal Injury Law
**Subcategories:** Automobile Accidents • Dangerous Property or Buildings • Defective Products • Medical Malpractice • Personal Injury (General)

**Specialized Processing:** Injury classification and severity assessment, medical cost tracking, liability analysis, insurance claim optimization

### Wills, Trusts & Estates Law
**Subcategories:** Contested Wills or Probate • Drafting Wills and Trusts • Estate Administration • Estate Planning

**Specialized Processing:** Estate valuation, beneficiary relationship mapping, probate timeline management, tax planning assistance

### Bankruptcy, Finances & Tax Law
**Subcategories:** Collections • Consumer Bankruptcy • Consumer Credit • Income Tax • Property Tax • Repossessions • Creditors' or Debtors' Rights

**Specialized Processing:** Debt categorization and priority analysis, asset assessment, bankruptcy eligibility determination, financial restructuring options

### Government & Administrative Law
**Subcategories:** Education and Schools • Social Security – Disability • Social Security – Retirement • Social Security – Dependent Benefits • Social Security – Survivor Benefits • Veterans Benefits • General Administrative Law • Environmental Law • Liquor Licenses • Constitutional Law

**Specialized Processing:** Government agency procedure navigation, benefit eligibility analysis, regulatory compliance assessment, administrative timeline tracking

### Product & Services Liability Law
**Subcategories:** Attorney Malpractice • Defective Products • Warranties • Consumer Protection and Fraud

**Specialized Processing:** Product defect classification, professional standard assessment, damage evaluation, remedy determination

### Intellectual Property Law
**Subcategories:** Copyright • Patents • Trademarks

**Specialized Processing:** IP type classification, registration status analysis, infringement assessment, licensing opportunity evaluation

### Landlord/Tenant Law
**Subcategories:** General Landlord and Tenant Issues

**Specialized Processing:** Lease agreement analysis, violation identification, eviction procedure management, property condition assessment

---

## System Features

### AI Processing Engine
- **Primary Model:** OpenAI GPT-4o Mini for advanced legal analysis
- **Custom Legal Prompts:** Specialized prompt engineering for legal accuracy
- **Confidence Scoring:** Reliability assessment and quality control mechanisms

### Form Management System
- **Predefined Templates:** Comprehensive JSON library containing all legal form structures
- **Intelligent Mapping:** AI-powered extraction and automated field population
- **Category-Based Selection:** Automatic form retrieval based on legal classification
- **Validation Framework:** Multi-layer data validation and quality assurance

### Database Infrastructure
- **Primary Database:** Supabase for scalable, real-time data management
- **Structured Storage:** Optimized schemas for legal case data and form templates
- **Audit Capabilities:** Complete logging and tracking of all processing activities
- **Backup Systems:** Automated backup with point-in-time recovery options

---

## Project Structure

```
ai-backend/
├── main.py                          # Application entry point and Flask app configuration
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (not in repo)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── dependencies.md                 # Dependencies documentation
├── list_libs.py                    # Dependency analysis script
├── test_api.py                     # API testing script
│
├── app/                            # Main application package
│   ├── __init__.py
│   ├── package-lock.json           # NPM package lock file
│   │
│   ├── api/                        # API layer
│   │   ├── __init__.py
│   │   ├── endpoints.py            # API endpoint definitions
│   │   └── routes/                 # API route definitions
│   │       ├── __init__.py
│   │       ├── case.py             # Case management endpoints
│   │       ├── category_routes.py  # Legal category endpoints
│   │       ├── form_routes.py      # Form generation endpoints
│   │       ├── general_routes.py   # System health and info endpoints
│   │       └── prediction_routes.py # AI prediction endpoints
│   │
│   ├── services/                   # Business logic layer
│   │   ├── case_analyzer.py        # AI-powered case analysis service
│   │   ├── database_service.py     # Supabase database operations
│   │   ├── form_prefill.py         # Intelligent form population service
│   │   ├── health_check.py         # System monitoring service
│   │   ├── legal_specialist_config.py # Legal domain configuration
│   │   ├── test_cases.py           # Test case definitions
│   │   │
│   │   ├── category/               # Category management services
│   │   │   ├── __init__.py
│   │   │   ├── category_manager.py # Legal category management
│   │   │   └── category_validator.py # Category validation logic
│   │   │
│   │   ├── form/                   # Form processing services
│   │   │   ├── form_generator.py   # Dynamic form generation
│   │   │   └── form_validator.py   # Form data validation
│   │   │
│   │   └── prediction/             # AI prediction services
│   │       ├── category_predictor.py # Legal category prediction
│   │       └── prompt_generator.py  # AI prompt generation
│   │
│   ├── models/                     # Data models and schemas
│   │   ├── case.py                 # Case data models
│   │   ├── category.py             # Category data models
│   │   └── form.py                 # Form data models
│   │
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py             # Application settings and config
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── formatters.py           # Data formatting utilities
│   │   ├── validators.py           # Data validation utilities
│   │   └── pii_remover.py          # PII detection and removal
│   │
│   └── data/                       # Static data files
│       └── legalForms.json         # Predefined legal form templates
│
└── logs/                           # Application logs
    ├── app.log                     # Main application log file
    └── legal_case_system.log       # Legal system specific logs
```

### Key Components

**Core Application Files:**
- `main.py` - Flask application initialization, CORS configuration, and startup logic
- `requirements.txt` - Complete dependency list including OpenAI, Supabase, Flask, and security libraries

**API Layer (`app/api/routes/`):**
- `case.py` - Primary case processing endpoints (analyze, prefill-form, generate-summary)
- `category_routes.py` - Legal category information and management
- `form_routes.py` - Form generation and template management
- `general_routes.py` - System health monitoring and information endpoints

**Service Layer (`app/services/`):**
- `case_analyzer.py` - OpenAI GPT-4o Mini integration for legal case analysis
- `form_prefiller.py` - AI-powered form population using predefined JSON templates
- `database_service.py` - Supabase database operations and data management
- `health_check.py` - System performance monitoring and diagnostics

**Data Models (`app/models/`):**
- `case.py` - Case data structures, metadata, and status management
- `category.py` - Legal category definitions and subcategory mappings
- `form.py` - Form structure definitions and field validation rules

**Configuration & Utilities:**
- `config/settings.py` - Environment-based configuration management
- `utils/pii_remover.py` - Advanced PII detection and anonymization
- `utils/validators.py` - Comprehensive data validation framework
- `data/legalForms.json` - Complete library of predefined legal form templates

---

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key with GPT-4o Mini access
- Supabase account with database credentials
- Minimum 4GB RAM (8GB recommended for production environments)

### Installation Steps

**1. Repository Setup**
```bash
git clone https://github.com/LegalRescue-ai/ai-backend.git
cd ai-backend
```

**2. Environment Configuration**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Environment Variables**
Create `.env` file with required configuration settings including OpenAI API key, Supabase credentials, and security settings.

**4. Database Setup**
Initialize required Supabase tables using provided database schema.

**5. Application Launch**
```bash
python main.py
```

The application will be available at `http://localhost:3001`

---

## Dependencies Documentation

> **Auto-generated on:** 2025-08-20 15:36:25  
> **Project Path:** `C:\Users\Administrator\Desktop\AI-BACKEND\ai-backend`  
> **Total Packages:** 85

### Overview

This section provides a comprehensive overview of all dependencies used in this Python project, including both direct dependencies (explicitly imported in your code) and sub-dependencies (required by your direct dependencies).

### Quick Setup

To set up this project environment:

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Verify installation
pip list
```

### Direct Dependencies (6)

These are the libraries explicitly imported and used in your project code:

| Package | Version | Description |
|---------|---------|-------------|
| `Flask` | 2.3.3 | *Direct dependency* |
| `Flask-Cors` | 4.0.0 | *Direct dependency* |
| `Flask-Session` | 0.8.0 | *Direct dependency* |
| `openai` | 1.61.1 | *Direct dependency* |
| `requests` | 2.31.0 | *Direct dependency* |
| `supabase` | 1.0.3 | *Direct dependency* |


### Sub-Dependencies (79)

These are automatically installed as requirements of your direct dependencies:

| Package | Version | Type |
|---------|---------|------|
| `annotated-types` | 0.7.0 | Sub-dependency |
| `anyio` | 3.7.1 | Sub-dependency |
| `blinker` | 1.9.0 | Sub-dependency |
| `cachelib` | 0.13.0 | Sub-dependency |
| `certifi` | 2025.1.31 | Sub-dependency |
| `cffi` | 1.17.1 | Sub-dependency |
| `chardet` | 5.2.0 | Sub-dependency |
| `charset-normalizer` | 3.4.1 | Sub-dependency |
| `click` | 8.1.8 | Sub-dependency |
| `click-log` | 0.4.0 | Sub-dependency |
| `colorama` | 0.4.6 | Sub-dependency |
| `cryptography` | 41.0.4 | Sub-dependency |
| `deprecation` | 2.1.0 | Sub-dependency |
| `distro` | 1.9.0 | Sub-dependency |
| `docopt` | 0.6.2 | Sub-dependency |
| `docutils` | 0.22 | Sub-dependency |
| `dotty-dict` | 1.3.1 | Sub-dependency |
| `ecdsa` | 0.19.0 | Sub-dependency |
| `gitdb` | 4.0.12 | Sub-dependency |
| `GitPython` | 3.1.45 | Sub-dependency |
| `gotrue` | 1.3.1 | Sub-dependency |
| `gunicorn` | 21.2.0 | Sub-dependency |
| `h11` | 0.14.0 | Sub-dependency |
| `httpcore` | 0.16.3 | Sub-dependency |
| `httpx` | 0.23.3 | Sub-dependency |
| `idna` | 3.10 | Sub-dependency |
| `importlib_metadata` | 8.7.0 | Sub-dependency |
| `invoke` | 1.7.3 | Sub-dependency |
| `itsdangerous` | 2.2.0 | Sub-dependency |
| `jaraco.classes` | 3.4.0 | Sub-dependency |
| `jaraco.context` | 6.0.1 | Sub-dependency |
| `jaraco.functools` | 4.3.0 | Sub-dependency |
| `Jinja2` | 3.1.5 | Sub-dependency |
| `jiter` | 0.8.2 | Sub-dependency |
| `keyring` | 25.6.0 | Sub-dependency |
| `MarkupSafe` | 3.0.2 | Sub-dependency |
| `more-itertools` | 10.7.0 | Sub-dependency |
| `msgspec` | 0.19.0 | Sub-dependency |
| `nh3` | 0.3.0 | Sub-dependency |
| `packaging` | 24.2 | Sub-dependency |
| `pipreqs` | 0.4.13 | Sub-dependency |
| `pkginfo` | 1.12.1.2 | Sub-dependency |
| `postgrest` | 0.10.7 | Sub-dependency |
| `pyasn1` | 0.6.1 | Sub-dependency |
| `pycparser` | 2.22 | Sub-dependency |
| `pydantic` | 2.10.6 | Sub-dependency |
| `pydantic_core` | 2.27.2 | Sub-dependency |
| `Pygments` | 2.19.2 | Sub-dependency |
| `python-dateutil` | 2.9.0.post0 | Sub-dependency |
| `python-dotenv` | 1.0.0 | Sub-dependency |
| `python-gitlab` | 3.15.0 | Sub-dependency |
| `python-jose` | 3.3.0 | Sub-dependency |
| `python-semantic-release` | 7.33.2 | Sub-dependency |
| `pywin32-ctypes` | 0.2.3 | Sub-dependency |
| `readme_renderer` | 44.0 | Sub-dependency |
| `realtime` | 1.0.6 | Sub-dependency |
| `requests-toolbelt` | 1.0.0 | Sub-dependency |
| `rfc3986` | 1.5.0 | Sub-dependency |
| `rsa` | 4.9 | Sub-dependency |
| `semver` | 2.13.0 | Sub-dependency |
| `setuptools` | 80.9.0 | Sub-dependency |
| `six` | 1.17.0 | Sub-dependency |
| `smmap` | 5.0.2 | Sub-dependency |
| `sniffio` | 1.3.1 | Sub-dependency |
| `stdlib-list` | 0.11.1 | Sub-dependency |
| `storage3` | 0.5.3 | Sub-dependency |
| `StrEnum` | 0.4.15 | Sub-dependency |
| `supafunc` | 0.2.2 | Sub-dependency |
| `tomlkit` | 0.13.3 | Sub-dependency |
| `tqdm` | 4.67.1 | Sub-dependency |
| `twine` | 3.8.0 | Sub-dependency |
| `typing_extensions` | 4.12.2 | Sub-dependency |
| `urllib3` | 2.3.0 | Sub-dependency |
| `waitress` | 3.0.2 | Sub-dependency |
| `websockets` | 12.0 | Sub-dependency |
| `Werkzeug` | 3.1.3 | Sub-dependency |
| `wheel` | 0.45.1 | Sub-dependency |
| `yarg` | 0.1.10 | Sub-dependency |
| `zipp` | 3.23.0 | Sub-dependency |


### Dependency Statistics

- **Direct Dependencies:** 6
- **Sub-Dependencies:** 79
- **Total Installed Packages:** 85
- **Python Files Scanned:** 34

### Import Analysis

**Detected Direct Imports:**
- `app`
- `ast`
- `case`
- `case_analyzer`
- `category_routes`
- `concurrent`
- `dotenv`
- `flask`
- `flask_cors`
- `flask_session`
- `form_routes`
- `general_routes`
- `importlib`
- `legal_specialist_config`
- `openai`
- `pkg_resources`
- `platform`
- `prediction_routes`
- `psutil`
- `requests`
- `supabase`
- `uuid`


### Maintenance

**Updating Dependencies**

```bash
# Update all packages to latest versions
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade package_name

# Re-generate this documentation
python document_dependencies.py
```

**Adding New Dependencies**

1. Install the package: `pip install new_package`
2. Update requirements: `pip freeze > requirements.txt`
3. Re-run documentation generator: `python document_dependencies.py`

### Requirements.txt

Your current `requirements.txt` file contains all the exact versions needed to reproduce this environment. Always commit this file to version control.

### Troubleshooting

**Common Issues:**

1. **Import Errors:** Ensure all packages in requirements.txt are installed
2. **Version Conflicts:** Use virtual environments to isolate dependencies
3. **Missing Packages:** Run `pip install -r requirements.txt` to install all dependencies

**Environment Check:**

```bash
# Check Python version
python --version

# Check pip version
pip --version

# List all installed packages
pip list

# Check for outdated packages
pip list --outdated
```

---

## API Documentation

### Core Processing Endpoints

**Case Analysis**
`POST /api/case/analyze`
- Analyzes case descriptions using AI
- Returns legal classification, confidence scores, and extracted details
- Includes automatic PII removal and data cleaning

**Form Prefilling**
`POST /api/case/prefill-form`
- Retrieves predefined form templates based on legal category
- Maps extracted case information to appropriate form fields
- Returns populated form data with validation

**Summary Generation**
`POST /api/case/generate-summary`
- Creates professional case summaries combining AI analysis and form data
- Generates structured legal documentation
- Stores complete case information in database

**Case Management**
`GET /api/case/cases` - Retrieve stored cases with optional filtering
`GET /api/case/cases/{id}` - Get specific case details by ID

### System Management Endpoints

**Category Information**
`GET /api/categories/` - Complete legal category and subcategory listing

**System Monitoring**
`GET /api/general/health` - System health status and performance metrics
`GET /api/general/system-info` - Detailed system capabilities and configuration

### Request/Response Format
All endpoints use JSON format for data exchange with comprehensive error handling and status reporting.

---

## Security & Compliance

### Data Protection Framework
- **PII Removal:** Automatic detection and removal of personally identifiable information
- **Encryption:** TLS encryption for all data transmission and secure storage
- **Access Control:** Role-based authentication with comprehensive audit logging
- **Input Validation:** Multi-layer sanitization preventing security vulnerabilities

### Compliance Standards
- **Legal Compliance:** Attorney-client privilege and confidentiality requirements
- **Data Privacy:** GDPR and HIPAA compliance for data protection
- **Security Standards:** Enterprise-grade security protocols and practices
- **Audit Capabilities:** Complete logging and tracking for compliance reporting

### Quality Assurance
- **Confidence Scoring:** AI reliability assessment for quality control
- **Validation Systems:** Multi-layer data validation and consistency checking
- **Error Prevention:** Proactive identification and correction of data issues
- **Manual Review:** Automatic flagging of low-confidence classifications