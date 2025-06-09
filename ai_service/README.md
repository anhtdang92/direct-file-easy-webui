# Prism AI Service

This service provides AI-powered tax analysis and audit risk assessment for the Prism tax preparation platform.

## Features

- Audit risk scoring using machine learning
- Feature extraction from tax documents
- Risk factor identification
- Personalized recommendations
- Real-time analysis

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Service

Development:
```bash
python app.py
```

Production:
```bash
gunicorn app:app
```

## API Endpoints

### POST /api/ai/analyze
Analyzes tax data and returns audit risk assessment.

Request body:
```json
{
    "total_income": 100000,
    "income_sources": ["W2", "1099"],
    "total_deductions": 20000,
    "itemized_deductions": ["mortgage", "charity"],
    "business_income": 50000,
    "business_expenses": 20000,
    "investment_income": 5000,
    "capital_gains": 2000,
    "investment_transactions": ["stock_sale", "dividend"],
    "home_office_deduction": 5000,
    "vehicle_expenses": 3000,
    "meal_entertainment_expenses": 2000,
    "charitable_contributions": 5000
}
```

Response:
```json
{
    "audit_risk_score": 0.35,
    "risk_level": "Low",
    "risk_factors": [
        "Multiple income sources",
        "High business expense ratio"
    ],
    "recommendations": [
        "Review deduction documentation",
        "Ensure all income is properly reported",
        "Keep detailed records of all transactions"
    ]
}
```

## Model Training

The audit risk model can be trained using historical tax data. See `training/` directory for training scripts and data preparation utilities.

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

4. Type checking:
```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License 