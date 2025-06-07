# Direct File - Quick Index

## Project Overview
Direct File is a free IRS service that allows taxpayers to electronically file federal tax returns directly with the IRS. It's designed to be mobile-friendly and accessible in both English and Spanish.

## Key Components
1. **Interview-Based System**
   - Converts complex tax code into plain language questions
   - Translates answers into standard tax forms
   - Integrates with IRS Modernized e-File (MeF) API

2. **Fact Graph**
   - Declarative, XML-based knowledge graph
   - Written in Scala
   - Runs on both JVM backend and client-side (via Scala.js)
   - Handles incomplete information reasoning

3. **State Integration**
   - Supports state/local tax filing through third-party tools
   - Uses State API for data transfer
   - Includes enriched JSON format for state revenue agencies

## Development Team
- IRS in-house technologists
- USDS and GSA support
- Vendor teams: TrussWorks, Coforma, and ATI

## Getting Started
- See `ONBOARDING.md` for local setup instructions

## Important Notes
- Some code is exempted due to PII, FTI, SBU, or NSS restrictions
- Repository follows federal open source policies
- Legal foundation includes various federal acts and memorandums

## Key Files
- `README.md` - Main project documentation
- `ONBOARDING.md` - Setup and development guide
- `LICENSE` - Project license information

## Project Structure
```
direct-file-easy-webui/
├── direct-file/     # Main application code
├── docs/           # Documentation
├── .git/           # Version control
├── LICENSE         # License file
├── ONBOARDING.md   # Setup guide
└── README.md       # Project overview
``` 