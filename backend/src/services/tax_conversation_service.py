from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import logging
import re
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class ValidationRule:
    type: str
    required: bool = True
    min_value: Optional[Union[int, float, Decimal]] = None
    max_value: Optional[Union[int, float, Decimal]] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    custom_validation: Optional[callable] = None
    error_message: Optional[str] = None

class TaxFormType(Enum):
    # Income Forms
    W2 = "W-2"
    W2G = "W-2G"
    FORM1099R = "1099-R"
    FORM1099DIV = "1099-DIV"
    FORM1099INT = "1099-INT"
    FORM1099MISC = "1099-MISC"
    FORM1099K = "1099-K"
    FORM1099B = "1099-B"
    FORM1099C = "1099-C"
    FORM1099G = "1099-G"
    FORM1099Q = "1099-Q"
    FORM1099SA = "1099-SA"
    FORM1099SSA = "1099-SSA"
    FORM1099RRB = "1099-RRB"
    FORM1099PATR = "1099-PATR"
    
    # Business Forms
    SCHEDULEC = "Schedule C"
    SCHEDULEE = "Schedule E"
    SCHEDULEF = "Schedule F"
    FORM1065 = "1065"
    FORM1120S = "1120-S"
    FORM1120 = "1120"
    
    # Deduction Forms
    SCHEDULEA = "Schedule A"
    SCHEDULED = "Schedule D"
    FORM2106 = "2106"
    FORM4562 = "4562"
    FORM8829 = "8829"
    
    # Credit Forms
    FORM8862 = "8862"
    FORM8880 = "8880"
    FORM8889 = "8889"
    FORM8917 = "8917"
    FORM8936 = "8936"

class ConversationState(Enum):
    INITIAL = "initial"
    COLLECTING_PERSONAL_INFO = "collecting_personal_info"
    COLLECTING_INCOME = "collecting_income"
    COLLECTING_DEDUCTIONS = "collecting_deductions"
    COLLECTING_CREDITS = "collecting_credits"
    REVIEWING = "reviewing"
    COMPLETED = "completed"

class TaxConversationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.form_templates = {
            # Income Forms
            TaxFormType.W2: {
                "fields": [
                    "employer_name",
                    "employer_ein",
                    "wages",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "social_security_tax_withheld",
                    "medicare_tax_withheld",
                    "social_security_wages",
                    "medicare_wages",
                    "dependent_care_benefits",
                    "nonqualified_plans",
                    "deferrals"
                ],
                "description": "W-2 form for employment income",
                "validation": {
                    "employer_name": ValidationRule(
                        type="string",
                        min_length=1,
                        max_length=100,
                        error_message="Employer name must be between 1 and 100 characters"
                    ),
                    "employer_ein": ValidationRule(
                        type="string",
                        pattern=r"^\d{2}-\d{7}$",
                        error_message="EIN must be in format XX-XXXXXXX"
                    ),
                    "wages": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Wages must be a positive number less than 1 billion"
                    ),
                    "federal_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Federal tax withheld must be a positive number less than 1 billion"
                    ),
                    "state_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="State tax withheld must be a positive number less than 1 billion"
                    ),
                    "social_security_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Social security tax withheld must be a positive number less than 1 billion"
                    ),
                    "medicare_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Medicare tax withheld must be a positive number less than 1 billion"
                    ),
                    "social_security_wages": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Social security wages must be a positive number less than 1 billion"
                    ),
                    "medicare_wages": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Medicare wages must be a positive number less than 1 billion"
                    ),
                    "dependent_care_benefits": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Dependent care benefits must be a positive number less than 1 billion"
                    ),
                    "nonqualified_plans": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Nonqualified plans must be a positive number less than 1 billion"
                    ),
                    "deferrals": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Deferrals must be a positive number less than 1 billion"
                    )
                }
            },
            TaxFormType.W2G: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_winnings",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "local_tax_withheld",
                    "gambling_type",
                    "transaction_date"
                ],
                "description": "W-2G form for gambling winnings",
                "validation": {
                    "payer_name": ValidationRule(
                        type="string",
                        min_length=1,
                        max_length=100,
                        error_message="Payer name must be between 1 and 100 characters"
                    ),
                    "payer_tin": ValidationRule(
                        type="string",
                        pattern=r"^\d{2}-\d{7}$",
                        error_message="TIN must be in format XX-XXXXXXX"
                    ),
                    "gross_winnings": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Gross winnings must be a positive number less than 1 billion"
                    ),
                    "federal_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Federal tax withheld must be a positive number less than 1 billion"
                    ),
                    "state_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="State tax withheld must be a positive number less than 1 billion"
                    ),
                    "local_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Local tax withheld must be a positive number less than 1 billion"
                    ),
                    "gambling_type": ValidationRule(
                        type="string",
                        allowed_values=["slot_machine", "table_games", "bingo", "keno", "lottery", "other"],
                        error_message="Gambling type must be one of: slot_machine, table_games, bingo, keno, lottery, other"
                    ),
                    "transaction_date": ValidationRule(
                        type="date",
                        pattern=r"^\d{4}-\d{2}-\d{2}$",
                        error_message="Transaction date must be in format YYYY-MM-DD"
                    )
                }
            },
            TaxFormType.FORM1099R: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_distribution",
                    "taxable_amount",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "distribution_code",
                    "ira_sep_simple",
                    "total_distribution"
                ],
                "description": "1099-R form for retirement distributions",
                "validation": {
                    "payer_name": ValidationRule(
                        type="string",
                        min_length=1,
                        max_length=100,
                        error_message="Payer name must be between 1 and 100 characters"
                    ),
                    "payer_tin": ValidationRule(
                        type="string",
                        pattern=r"^\d{2}-\d{7}$",
                        error_message="TIN must be in format XX-XXXXXXX"
                    ),
                    "gross_distribution": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Gross distribution must be a positive number less than 1 billion"
                    ),
                    "taxable_amount": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Taxable amount must be a positive number less than 1 billion"
                    ),
                    "federal_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Federal tax withheld must be a positive number less than 1 billion"
                    ),
                    "state_tax_withheld": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="State tax withheld must be a positive number less than 1 billion"
                    ),
                    "distribution_code": ValidationRule(
                        type="string",
                        pattern=r"^[1-9][0-9]?$",
                        error_message="Distribution code must be a number between 1 and 99"
                    ),
                    "ira_sep_simple": ValidationRule(
                        type="string",
                        allowed_values=["IRA", "SEP", "SIMPLE", "NONE"],
                        error_message="IRA/SEP/SIMPLE must be one of: IRA, SEP, SIMPLE, NONE"
                    ),
                    "total_distribution": ValidationRule(
                        type="decimal",
                        min_value=0,
                        max_value=1000000000,
                        error_message="Total distribution must be a positive number less than 1 billion"
                    )
                }
            },
            TaxFormType.FORM1099DIV: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "total_ordinary_dividends",
                    "qualified_dividends",
                    "capital_gain_distributions",
                    "non_dividend_distributions",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "foreign_tax_paid",
                    "foreign_country"
                ],
                "description": "1099-DIV form for dividends"
            },
            TaxFormType.FORM1099INT: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "interest_income",
                    "early_withdrawal_penalty",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "foreign_tax_paid",
                    "foreign_country",
                    "tax_exempt_interest",
                    "specified_private_activity_bond_interest"
                ],
                "description": "1099-INT form for interest income"
            },
            TaxFormType.FORM1099MISC: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "rents",
                    "royalties",
                    "other_income",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "fishing_boat_proceeds",
                    "medical_health_payments",
                    "nonemployee_compensation",
                    "substitute_payments",
                    "crop_insurance_proceeds",
                    "gross_proceeds",
                    "attorney_fees",
                    "section_409a_deferrals",
                    "section_409a_income"
                ],
                "description": "1099-MISC form for miscellaneous income"
            },
            TaxFormType.FORM1099K: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_amount",
                    "card_not_present_transactions",
                    "merchant_category_code",
                    "number_of_transactions",
                    "state_tax_withheld",
                    "state_income"
                ],
                "description": "1099-K form for payment card transactions"
            },
            TaxFormType.FORM1099B: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "description_of_property",
                    "date_acquired",
                    "date_sold",
                    "proceeds",
                    "cost_basis",
                    "wash_sale_loss_disallowed",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "gain_loss",
                    "adjustment_code",
                    "adjustment_amount"
                ],
                "description": "1099-B form for broker transactions"
            },
            TaxFormType.FORM1099C: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "debt_amount",
                    "date_of_identifiable_event",
                    "interest_included",
                    "fair_market_value",
                    "debt_description",
                    "debt_code"
                ],
                "description": "1099-C form for debt cancellation"
            },
            TaxFormType.FORM1099G: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "unemployment_compensation",
                    "state_tax_withheld",
                    "local_tax_withheld",
                    "trade_adjustment_allowances",
                    "taxable_grant",
                    "agricultural_payments",
                    "federal_tax_withheld"
                ],
                "description": "1099-G form for government payments"
            },
            TaxFormType.FORM1099Q: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_distribution",
                    "earnings",
                    "basis",
                    "account_type",
                    "beneficiary_tin",
                    "beneficiary_name",
                    "transfer_rollover"
                ],
                "description": "1099-Q form for qualified education program payments"
            },
            TaxFormType.FORM1099SA: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_distribution",
                    "earnings",
                    "basis",
                    "account_type",
                    "beneficiary_tin",
                    "beneficiary_name",
                    "hsa_distribution_code"
                ],
                "description": "1099-SA form for HSA distributions"
            },
            TaxFormType.FORM1099SSA: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "benefits_paid",
                    "benefits_paid_year",
                    "benefits_paid_month",
                    "benefits_paid_day",
                    "benefits_paid_type",
                    "benefits_paid_code"
                ],
                "description": "1099-SSA form for social security benefits"
            },
            TaxFormType.FORM1099RRB: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "gross_payment",
                    "benefit_payment",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "local_tax_withheld",
                    "benefit_type",
                    "benefit_code"
                ],
                "description": "1099-RRB form for railroad retirement benefits"
            },
            TaxFormType.FORM1099PATR: {
                "fields": [
                    "payer_name",
                    "payer_tin",
                    "patronage_dividends",
                    "nonpatronage_distributions",
                    "per_unit_retain_allocations",
                    "federal_tax_withheld",
                    "state_tax_withheld",
                    "local_tax_withheld",
                    "redemption_amount",
                    "per_unit_retain_allocation_code"
                ],
                "description": "1099-PATR form for patronage dividends"
            },
            
            # Business Forms
            TaxFormType.SCHEDULEC: {
                "fields": [
                    "business_name",
                    "business_code",
                    "business_address",
                    "business_phone",
                    "business_start_date",
                    "business_end_date",
                    "material_participation",
                    "gross_receipts",
                    "returns_allowances",
                    "other_income",
                    "gross_income",
                    "inventory_beginning",
                    "inventory_end",
                    "purchases",
                    "materials",
                    "other_costs",
                    "cost_of_goods_sold",
                    "gross_profit",
                    "advertising",
                    "car_truck_expenses",
                    "commissions",
                    "contract_labor",
                    "depletion",
                    "depreciation",
                    "employee_benefit_programs",
                    "insurance",
                    "interest_mortgage",
                    "interest_other",
                    "legal_professional_services",
                    "office_expense",
                    "pension_profit_sharing",
                    "rent_lease_vehicles",
                    "rent_lease_other",
                    "repairs_maintenance",
                    "supplies",
                    "taxes_licenses",
                    "travel",
                    "meals",
                    "utilities",
                    "wages",
                    "other_expenses",
                    "total_expenses",
                    "net_profit_loss"
                ],
                "description": "Schedule C form for business income"
            },
            TaxFormType.SCHEDULEE: {
                "fields": [
                    "property_address",
                    "property_type",
                    "rental_income",
                    "royalties",
                    "partnership_income",
                    "s_corporation_income",
                    "estate_trust_income",
                    "other_income",
                    "total_income",
                    "advertising",
                    "auto_travel",
                    "cleaning_maintenance",
                    "commissions",
                    "insurance",
                    "legal_professional",
                    "management_fees",
                    "mortgage_interest",
                    "other_interest",
                    "repairs",
                    "supplies",
                    "taxes",
                    "utilities",
                    "depreciation",
                    "other_expenses",
                    "total_expenses",
                    "net_income_loss"
                ],
                "description": "Schedule E form for rental and royalty income"
            },
            TaxFormType.SCHEDULEF: {
                "fields": [
                    "farm_name",
                    "farm_address",
                    "farm_phone",
                    "farm_start_date",
                    "farm_end_date",
                    "material_participation",
                    "gross_income",
                    "sales_livestock",
                    "sales_crops",
                    "cooperative_distributions",
                    "agricultural_program_payments",
                    "commodity_credit_corporation_loans",
                    "crop_insurance_proceeds",
                    "other_income",
                    "total_income",
                    "inventory_beginning",
                    "inventory_end",
                    "purchases",
                    "labor_hired",
                    "feed",
                    "seed",
                    "fertilizer",
                    "chemicals",
                    "veterinary",
                    "medicine",
                    "supplies",
                    "custom_hire",
                    "fuel",
                    "utilities",
                    "repairs",
                    "insurance",
                    "rent_lease_vehicles",
                    "rent_lease_other",
                    "interest_mortgage",
                    "interest_other",
                    "taxes",
                    "depreciation",
                    "other_expenses",
                    "total_expenses",
                    "net_profit_loss"
                ],
                "description": "Schedule F form for farm income"
            },
            
            # Deduction Forms
            TaxFormType.SCHEDULEA: {
                "fields": [
                    "medical_dental_expenses",
                    "taxes_paid",
                    "interest_paid",
                    "gifts_to_charity",
                    "casualty_theft_losses",
                    "other_itemized_deductions",
                    "total_itemized_deductions"
                ],
                "description": "Schedule A form for itemized deductions"
            },
            TaxFormType.SCHEDULED: {
                "fields": [
                    "description_of_property",
                    "date_acquired",
                    "date_sold",
                    "sales_price",
                    "cost_basis",
                    "gains_losses",
                    "holding_period",
                    "adjustment_code",
                    "adjustment_amount"
                ],
                "description": "Schedule D form for capital gains and losses"
            },
            TaxFormType.FORM2106: {
                "fields": [
                    "vehicle_expenses",
                    "parking_fees",
                    "tolls",
                    "travel_expenses",
                    "transportation_expenses",
                    "meals_entertainment",
                    "other_expenses",
                    "total_expenses",
                    "reimbursements",
                    "net_expenses"
                ],
                "description": "Form 2106 for employee business expenses"
            },
            TaxFormType.FORM4562: {
                "fields": [
                    "property_description",
                    "date_placed_in_service",
                    "cost_basis",
                    "business_use_percentage",
                    "recovery_period",
                    "convention",
                    "depreciation_method",
                    "depreciation_amount"
                ],
                "description": "Form 4562 for depreciation and amortization"
            },
            TaxFormType.FORM8829: {
                "fields": [
                    "home_address",
                    "part_of_home_used",
                    "total_square_footage",
                    "business_square_footage",
                    "business_percentage",
                    "gross_income",
                    "expenses",
                    "depreciation",
                    "total_expenses"
                ],
                "description": "Form 8829 for home office expenses"
            },
            
            # Credit Forms
            TaxFormType.FORM8862: {
                "fields": [
                    "qualifying_child_name",
                    "qualifying_child_ssn",
                    "qualifying_child_birth_date",
                    "qualifying_child_relationship",
                    "qualifying_child_months_lived",
                    "qualifying_child_support",
                    "qualifying_child_income",
                    "qualifying_child_disability",
                    "qualifying_child_student"
                ],
                "description": "Form 8862 for earned income credit"
            },
            TaxFormType.FORM8880: {
                "fields": [
                    "retirement_contributions",
                    "adjusted_gross_income",
                    "filing_status",
                    "retirement_credit_amount"
                ],
                "description": "Form 8880 for retirement savings contributions credit"
            },
            TaxFormType.FORM8889: {
                "fields": [
                    "hsa_contributions",
                    "hsa_distributions",
                    "hsa_balance",
                    "hsa_earnings",
                    "hsa_penalty"
                ],
                "description": "Form 8889 for health savings accounts"
            },
            TaxFormType.FORM8917: {
                "fields": [
                    "tuition_expenses",
                    "qualified_expenses",
                    "education_credits",
                    "student_name",
                    "student_ssn",
                    "student_birth_date",
                    "student_months_enrolled"
                ],
                "description": "Form 8917 for tuition and fees deduction"
            },
            TaxFormType.FORM8936: {
                "fields": [
                    "vehicle_make",
                    "vehicle_model",
                    "vehicle_year",
                    "vehicle_vin",
                    "vehicle_cost",
                    "vehicle_credit_amount"
                ],
                "description": "Form 8936 for qualified plug-in electric drive motor vehicle credit"
            }
        }
        
        # Industry and profession-specific patterns
        self.industry_patterns = {
            "healthcare": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:doctor|physician|nurse|dentist|therapist)",
                r"(?:i|we) (?:work|practice) in (?:healthcare|medicine|dental|therapy)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:medical|dental|therapy) (?:practice|clinic)",
                r"(?:i|we) (?:provide|offer) (?:medical|healthcare|dental|therapy) (?:services|care)",
                r"(?:i|we) (?:am|are) (?:a|an) (?:healthcare|medical) (?:provider|professional)",
                r"(?:i|we) (?:have|had) (?:medical|healthcare) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:medical|healthcare) (?:equipment|supplies)",
                r"(?:i|we) (?:have|had) (?:malpractice|professional) (?:insurance|coverage)"
            ],
            "technology": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:software|web|mobile|data) (?:developer|engineer)",
                r"(?:i|we) (?:work|develop) in (?:tech|technology|software|it)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:tech|software|it) (?:company|business)",
                r"(?:i|we) (?:provide|offer) (?:tech|software|it) (?:services|consulting)",
                r"(?:i|we) (?:am|are) (?:a|an) (?:programmer|coder|developer|engineer)",
                r"(?:i|we) (?:have|had) (?:tech|software) (?:certifications|licenses)",
                r"(?:i|we) (?:paid|spent) for (?:tech|software) (?:equipment|licenses)",
                r"(?:i|we) (?:have|had) (?:professional|liability) (?:insurance|coverage)"
            ],
            "real_estate": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:realtor|broker|agent|investor)",
                r"(?:i|we) (?:work|practice) in (?:real estate|property|housing)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:real estate|property) (?:business|company)",
                r"(?:i|we) (?:provide|offer) (?:real estate|property) (?:services|consulting)",
                r"(?:i|we) (?:have|had) (?:real estate|property) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:real estate|property) (?:education|training)",
                r"(?:i|we) (?:have|had) (?:real estate|property) (?:investments|holdings)",
                r"(?:i|we) (?:manage|own) (?:rental|investment) (?:properties|units)"
            ],
            "legal": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:lawyer|attorney|paralegal)",
                r"(?:i|we) (?:work|practice) in (?:law|legal|attorney)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:law|legal) (?:practice|firm)",
                r"(?:i|we) (?:provide|offer) (?:legal|attorney) (?:services|consulting)",
                r"(?:i|we) (?:have|had) (?:legal|attorney) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:legal|attorney) (?:education|training)",
                r"(?:i|we) (?:have|had) (?:malpractice|professional) (?:insurance|coverage)",
                r"(?:i|we) (?:work|practice) in (?:criminal|civil|corporate|family) law"
            ],
            "finance": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:financial|investment|banking) (?:advisor|analyst|manager)",
                r"(?:i|we) (?:work|practice) in (?:finance|banking|investment)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:financial|investment) (?:firm|practice)",
                r"(?:i|we) (?:provide|offer) (?:financial|investment) (?:services|advice)",
                r"(?:i|we) (?:have|had) (?:financial|investment) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:financial|investment) (?:education|training)",
                r"(?:i|we) (?:have|had) (?:series|finra) (?:licenses|certifications)",
                r"(?:i|we) (?:work|practice) in (?:wealth|portfolio|risk) management"
            ],
            "education": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:teacher|professor|educator|instructor)",
                r"(?:i|we) (?:work|teach) in (?:education|teaching|academia)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:teaching|education) (?:business|practice)",
                r"(?:i|we) (?:provide|offer) (?:teaching|education) (?:services|tutoring)",
                r"(?:i|we) (?:have|had) (?:teaching|education) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:teaching|education) (?:supplies|materials)",
                r"(?:i|we) (?:have|had) (?:professional|liability) (?:insurance|coverage)",
                r"(?:i|we) (?:work|teach) in (?:public|private|higher) education"
            ],
            "construction": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:contractor|builder|developer)",
                r"(?:i|we) (?:work|practice) in (?:construction|building|development)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:construction|building) (?:company|business)",
                r"(?:i|we) (?:provide|offer) (?:construction|building) (?:services|contracting)",
                r"(?:i|we) (?:have|had) (?:construction|building) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:construction|building) (?:equipment|tools)",
                r"(?:i|we) (?:have|had) (?:contractor|builder) (?:insurance|coverage)",
                r"(?:i|we) (?:work|practice) in (?:residential|commercial|industrial) construction"
            ],
            "retail": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:retailer|shop owner|store owner)",
                r"(?:i|we) (?:work|practice) in (?:retail|sales|merchandising)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:retail|shop|store) (?:business|company)",
                r"(?:i|we) (?:provide|offer) (?:retail|sales) (?:services|products)",
                r"(?:i|we) (?:have|had) (?:retail|sales) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:retail|sales) (?:inventory|equipment)",
                r"(?:i|we) (?:have|had) (?:business|liability) (?:insurance|coverage)",
                r"(?:i|we) (?:work|practice) in (?:online|brick and mortar) retail"
            ],
            "restaurant": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:restaurateur|chef|restaurant owner)",
                r"(?:i|we) (?:work|practice) in (?:restaurant|food|hospitality)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:restaurant|food) (?:business|company)",
                r"(?:i|we) (?:provide|offer) (?:food|dining) (?:services|products)",
                r"(?:i|we) (?:have|had) (?:food|restaurant) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:food|restaurant) (?:equipment|supplies)",
                r"(?:i|we) (?:have|had) (?:business|liability) (?:insurance|coverage)",
                r"(?:i|we) (?:work|practice) in (?:fine dining|casual dining|fast food)"
            ],
            "transportation": [
                r"(?:i|we) (?:am|are) (?:a|an) (?:trucker|driver|transportation provider)",
                r"(?:i|we) (?:work|practice) in (?:transportation|shipping|logistics)",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:trucking|transportation) (?:business|company)",
                r"(?:i|we) (?:provide|offer) (?:transportation|shipping) (?:services|delivery)",
                r"(?:i|we) (?:have|had) (?:transportation|driver) (?:licenses|certifications)",
                r"(?:i|we) (?:paid|spent) for (?:transportation|vehicle) (?:equipment|maintenance)",
                r"(?:i|we) (?:have|had) (?:commercial|liability) (?:insurance|coverage)",
                r"(?:i|we) (?:work|practice) in (?:long haul|local|specialized) transportation"
            ]
        }

        # Natural language patterns for income recognition
        self.income_patterns = {
            "w2": [
                r"(?:i|we) (?:work|am employed|have a job) (?:at|for) (.+)",
                r"(?:my|our) employer is (.+)",
                r"(?:i|we) received (?:a|my|our) w-2 from (.+)",
                r"(?:i|we) work(?:ed)? (?:at|for) (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) paycheck from (.+)",
                r"(?:i|we) (?:am|are) (?:employed|working) by (.+)",
                r"(?:i|we) (?:have|had) (?:a|my|our) job at (.+)",
                r"(?:i|we) (?:earned|made) money from (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) salary from (.+)"
            ],
            "1099r": [
                r"(?:i|we) (?:received|got) (?:a|my|our) (?:retirement|pension) (?:distribution|payment) from (.+)",
                r"(?:i|we) (?:took|withdrew) money from (?:my|our) (?:ira|retirement account) at (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) 1099-r from (.+)",
                r"(?:i|we) (?:have|had) (?:a|my|our) (?:pension|annuity) from (.+)",
                r"(?:i|we) (?:received|got) (?:a|my|our) (?:social security|ssi) (?:benefits|payments)",
                r"(?:i|we) (?:took|made) (?:an|a) (?:early|required) (?:withdrawal|distribution) from (.+)",
                r"(?:i|we) (?:rolled over|transferred) (?:my|our) (?:ira|retirement) to (.+)"
            ],
            "1099div": [
                r"(?:i|we) (?:received|got) (?:dividends|stock payments) from (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) 1099-div from (.+)",
                r"(?:i|we) have (?:stocks|shares) in (.+)",
                r"(?:i|we) (?:own|have) (?:stock|shares) of (.+)",
                r"(?:i|we) (?:got|received) (?:capital gains|investment income) from (.+)",
                r"(?:i|we) (?:sold|disposed of) (?:stock|shares) in (.+)",
                r"(?:i|we) (?:have|had) (?:mutual fund|etf) (?:distributions|payments) from (.+)"
            ],
            "1099int": [
                r"(?:i|we) (?:received|got) (?:interest|bank interest) from (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) 1099-int from (.+)",
                r"(?:i|we) have (?:a|an) (?:savings|checking) account at (.+)",
                r"(?:i|we) (?:earned|made) (?:interest|money) from (.+)",
                r"(?:i|we) (?:have|had) (?:a|an) (?:cd|certificate of deposit) at (.+)",
                r"(?:i|we) (?:got|received) (?:bond|treasury) (?:interest|payments) from (.+)",
                r"(?:i|we) (?:have|had) (?:a|an) (?:money market|high yield) account at (.+)"
            ],
            "1099misc": [
                r"(?:i|we) (?:received|got) (?:a|my|our) 1099-misc from (.+)",
                r"(?:i|we) (?:did|performed) (?:contract|freelance) work for (.+)",
                r"(?:i|we) (?:got|received) (?:rental|royalty) income from (.+)",
                r"(?:i|we) (?:have|had) (?:a|an) (?:side hustle|gig) with (.+)",
                r"(?:i|we) (?:earned|made) money as (?:a|an) (?:consultant|contractor) for (.+)",
                r"(?:i|we) (?:received|got) (?:prize|award) money from (.+)",
                r"(?:i|we) (?:got|received) (?:attorney|legal) fees from (.+)"
            ],
            "1099k": [
                r"(?:i|we) (?:received|got) (?:a|my|our) 1099-k from (.+)",
                r"(?:i|we) (?:sold|sold items) on (?:ebay|amazon|etsy|paypal)",
                r"(?:i|we) (?:got|received) (?:payment|payments) through (.+)",
                r"(?:i|we) (?:have|had) (?:a|an) (?:online|digital) business on (.+)",
                r"(?:i|we) (?:earned|made) money from (?:online|digital) sales on (.+)"
            ],
            "1099b": [
                r"(?:i|we) (?:sold|disposed of) (?:stock|securities) through (.+)",
                r"(?:i|we) (?:got|received) (?:a|my|our) 1099-b from (.+)",
                r"(?:i|we) (?:have|had) (?:stock|securities) (?:trades|transactions) with (.+)",
                r"(?:i|we) (?:sold|sold shares) of (.+)",
                r"(?:i|we) (?:realized|had) (?:capital gains|losses) from (.+)"
            ]
        }

        # Natural language patterns for deduction recognition
        self.deduction_patterns = {
            "mortgage": [
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:house|home|mortgage)",
                r"(?:i|we) (?:pay|paid) (?:mortgage|home loan) (?:interest|payment)",
                r"(?:i|we) (?:bought|purchased) (?:a|my|our) (?:house|home)",
                r"(?:i|we) (?:have|had) (?:a|my|our) (?:home loan|mortgage loan)",
                r"(?:i|we) (?:refinanced|refinance) (?:my|our) (?:house|home|mortgage)",
                r"(?:i|we) (?:pay|paid) (?:points|loan points) on (?:my|our) (?:mortgage|home loan)"
            ],
            "property_tax": [
                r"(?:i|we) (?:paid|pay) (?:property|real estate) tax",
                r"(?:i|we) (?:have|own) (?:a|my|our) (?:house|home|property)",
                r"(?:i|we) (?:got|received) (?:a|my|our) (?:property|real estate) tax bill",
                r"(?:i|we) (?:pay|paid) (?:county|city|state) (?:property|real estate) tax",
                r"(?:i|we) (?:have|had) (?:a|my|our) (?:property|real estate) tax assessment"
            ],
            "charity": [
                r"(?:i|we) (?:donated|gave) (?:to|money to) (.+)",
                r"(?:i|we) (?:gave|donated) (?:clothes|items) to (.+)",
                r"(?:i|we) (?:volunteered|helped) at (.+)",
                r"(?:i|we) (?:contributed|donated) to (?:a|an) (?:charity|nonprofit) (.+)",
                r"(?:i|we) (?:gave|donated) (?:cash|money) to (.+)",
                r"(?:i|we) (?:sponsored|supported) (?:a|an) (?:event|cause) for (.+)",
                r"(?:i|we) (?:donated|gave) (?:a|my|our) (?:car|vehicle) to (.+)"
            ],
            "medical": [
                r"(?:i|we) (?:paid|spent) (?:medical|healthcare|doctor) (?:expenses|bills)",
                r"(?:i|we) (?:have|had) (?:medical|healthcare|doctor) (?:expenses|bills)",
                r"(?:i|we) (?:bought|purchased) (?:medicine|prescription|drugs)",
                r"(?:i|we) (?:paid|spent) for (?:dental|vision|hearing) (?:care|expenses)",
                r"(?:i|we) (?:have|had) (?:health insurance|medical insurance) (?:premiums|payments)",
                r"(?:i|we) (?:paid|spent) for (?:therapy|mental health) (?:services|treatment)",
                r"(?:i|we) (?:bought|purchased) (?:medical|healthcare) (?:equipment|supplies)"
            ],
            "education": [
                r"(?:i|we) (?:paid|spent) for (?:college|university|school) (?:tuition|expenses)",
                r"(?:i|we) (?:have|had) (?:student|education) (?:loans|debt)",
                r"(?:i|we) (?:paid|spent) for (?:books|supplies|materials) for (?:school|college)",
                r"(?:i|we) (?:paid|spent) for (?:online|distance) (?:learning|education)",
                r"(?:i|we) (?:have|had) (?:education|student) (?:expenses|costs)",
                r"(?:i|we) (?:paid|spent) for (?:professional|continuing) (?:education|development)"
            ],
            "business": [
                r"(?:i|we) (?:have|had) (?:business|self-employment) (?:expenses|costs)",
                r"(?:i|we) (?:paid|spent) for (?:business|work) (?:supplies|equipment)",
                r"(?:i|we) (?:have|had) (?:a|my|our) (?:home office|workspace)",
                r"(?:i|we) (?:paid|spent) for (?:business|work) (?:travel|meals)",
                r"(?:i|we) (?:have|had) (?:business|work) (?:insurance|licenses)",
                r"(?:i|we) (?:paid|spent) for (?:business|professional) (?:services|consulting)"
            ],
            "vehicle": [
                r"(?:i|we) (?:use|drive) (?:my|our) (?:car|vehicle) for (?:business|work)",
                r"(?:i|we) (?:paid|spent) for (?:car|vehicle) (?:expenses|costs)",
                r"(?:i|we) (?:have|had) (?:business|work) (?:mileage|travel)",
                r"(?:i|we) (?:paid|spent) for (?:gas|fuel|maintenance) for (?:work|business)",
                r"(?:i|we) (?:use|drive) (?:my|our) (?:car|vehicle) for (?:charity|volunteer) work"
            ],
            "state_tax": [
                r"(?:i|we) (?:paid|pay) (?:state|local) (?:income|sales) tax",
                r"(?:i|we) (?:have|had) (?:state|local) (?:tax|taxes) (?:deductions|credits)",
                r"(?:i|we) (?:paid|spent) for (?:state|local) (?:tax|taxes)"
            ]
        }

        # Natural language patterns for credit recognition
        self.credit_patterns = {
            "child": [
                r"(?:i|we) (?:have|got) (?:a|my|our) (?:child|children|kid|kids)",
                r"(?:i|we) (?:have|got) (?:a|my|our) (?:dependent|child|children)",
                r"(?:i|we) (?:take|care for) (?:care of|care for) (?:a|my|our) (?:child|children|kid|kids)",
                r"(?:i|we) (?:have|got) (?:a|my|our) (?:son|daughter|sons|daughters)",
                r"(?:i|we) (?:pay|spent) for (?:child|day) care",
                r"(?:i|we) (?:have|had) (?:child|dependent) care (?:expenses|costs)",
                r"(?:i|we) (?:adopted|fostered) (?:a|my|our) (?:child|children)"
            ],
            "education": [
                r"(?:i|we) (?:went|go) to (?:college|university|school)",
                r"(?:i|we) (?:paid|spent) (?:tuition|college|education) (?:expenses|costs)",
                r"(?:i|we) (?:have|got) (?:student|education) (?:loans|debt)",
                r"(?:i|we) (?:am|are) (?:a|an) (?:student|graduate student)",
                r"(?:i|we) (?:paid|spent) for (?:books|supplies|materials) for (?:school|college)",
                r"(?:i|we) (?:have|had) (?:education|student) (?:expenses|costs)",
                r"(?:i|we) (?:paid|spent) for (?:online|distance) (?:learning|education)"
            ],
            "retirement": [
                r"(?:i|we) (?:contributed|put money) to (?:my|our) (?:ira|retirement)",
                r"(?:i|we) (?:saved|invested) for (?:retirement|future)",
                r"(?:i|we) (?:have|got) (?:a|an) (?:ira|retirement account)",
                r"(?:i|we) (?:contributed|put money) to (?:my|our) (?:401k|403b|457)",
                r"(?:i|we) (?:have|had) (?:retirement|pension) (?:contributions|savings)",
                r"(?:i|we) (?:saved|invested) in (?:my|our) (?:roth|traditional) ira"
            ],
            "energy": [
                r"(?:i|we) (?:installed|put in) (?:solar|wind) (?:panels|energy)",
                r"(?:i|we) (?:bought|purchased) (?:an|a) (?:electric|hybrid) (?:car|vehicle)",
                r"(?:i|we) (?:made|did) (?:energy|home) (?:improvements|upgrades)",
                r"(?:i|we) (?:installed|put in) (?:energy|efficient) (?:windows|doors)",
                r"(?:i|we) (?:bought|purchased) (?:energy|efficient) (?:appliances|equipment)"
            ],
            "health": [
                r"(?:i|we) (?:have|got) (?:health|medical) (?:insurance|coverage)",
                r"(?:i|we) (?:bought|purchased) (?:health|medical) (?:insurance|coverage)",
                r"(?:i|we) (?:have|got) (?:a|an) (?:hsa|health savings account)",
                r"(?:i|we) (?:contributed|put money) to (?:my|our) (?:hsa|health savings account)",
                r"(?:i|we) (?:paid|spent) for (?:health|medical) (?:insurance|coverage)"
            ],
            "adoption": [
                r"(?:i|we) (?:adopted|fostered) (?:a|my|our) (?:child|children)",
                r"(?:i|we) (?:paid|spent) for (?:adoption|foster) (?:expenses|costs)",
                r"(?:i|we) (?:have|had) (?:adoption|foster) (?:expenses|costs)",
                r"(?:i|we) (?:went|went through) (?:the|an) (?:adoption|foster) (?:process|procedure)"
            ]
        }

    def validate_field(self, field_name: str, value: Any, form_type: TaxFormType) -> tuple[bool, Optional[str]]:
        """Validate a field value against its rules."""
        try:
            validation = self.form_templates[form_type]["validation"][field_name]
            
            # Check required
            if validation.required and (value is None or value == ""):
                return False, f"{field_name} is required"

            # Skip validation if value is empty and not required
            if not validation.required and (value is None or value == ""):
                return True, None

            # Type validation
            if validation.type == "string":
                if not isinstance(value, str):
                    return False, f"{field_name} must be a string"
            elif validation.type == "decimal":
                try:
                    value = Decimal(str(value))
                except:
                    return False, f"{field_name} must be a number"
            elif validation.type == "date":
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
                    return False, f"{field_name} must be in format YYYY-MM-DD"

            # Length validation
            if validation.min_length is not None and len(str(value)) < validation.min_length:
                return False, f"{field_name} must be at least {validation.min_length} characters"
            if validation.max_length is not None and len(str(value)) > validation.max_length:
                return False, f"{field_name} must be at most {validation.max_length} characters"

            # Pattern validation
            if validation.pattern is not None:
                if not re.match(validation.pattern, str(value)):
                    return False, validation.error_message or f"{field_name} format is invalid"

            # Value range validation
            if validation.min_value is not None:
                if Decimal(str(value)) < Decimal(str(validation.min_value)):
                    return False, f"{field_name} must be at least {validation.min_value}"
            if validation.max_value is not None:
                if Decimal(str(value)) > Decimal(str(validation.max_value)):
                    return False, f"{field_name} must be at most {validation.max_value}"

            # Allowed values validation
            if validation.allowed_values is not None:
                if str(value) not in validation.allowed_values:
                    return False, f"{field_name} must be one of: {', '.join(validation.allowed_values)}"

            # Custom validation
            if validation.custom_validation is not None:
                if not validation.custom_validation(value):
                    return False, validation.error_message or f"{field_name} validation failed"

            return True, None

        except Exception as e:
            self.logger.error(f"Validation error for {field_name}: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def start_conversation(self) -> Dict[str, Any]:
        """Start a new tax conversation."""
        return {
            "state": ConversationState.INITIAL,
            "messages": [
                {
                    "type": "bot",
                    "content": "Hi! I'm your AI tax assistant. I'll help you file your taxes in a natural, conversational way. Let's start with your first name.",
                    "input_type": "text"
                }
            ],
            "collected_data": {}
        }

    def process_user_response(self,
                            conversation_id: str,
                            user_response: str,
                            current_state: ConversationState,
                            collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user response and generate next question."""
        try:
            # Check for industry-specific patterns first
            if current_state == ConversationState.COLLECTING_PERSONAL_INFO:
                for industry, patterns in self.industry_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, user_response.lower()):
                            # Store the industry information
                            collected_data["industry"] = industry
                            # Move to deductions collection for industry-specific questions
                            return {
                                "state": ConversationState.COLLECTING_DEDUCTIONS,
                                "message": f"Thanks {collected_data.get('first_name', '')}! Since you're in {industry}, let's talk about your business expenses and deductions.",
                                "collected_data": collected_data
                            }

            # Continue with normal processing if no industry pattern is found
            if current_state == ConversationState.INITIAL:
                return self._handle_initial_state(user_response, collected_data)
            elif current_state == ConversationState.COLLECTING_PERSONAL_INFO:
                return self._handle_personal_info_collection(user_response, collected_data)
            elif current_state == ConversationState.COLLECTING_INCOME:
                return self._handle_income_collection(user_response, collected_data)
            elif current_state == ConversationState.COLLECTING_DEDUCTIONS:
                return self._handle_deductions_collection(user_response, collected_data)
            elif current_state == ConversationState.COLLECTING_CREDITS:
                return self._handle_credits_collection(user_response, collected_data)
            elif current_state == ConversationState.REVIEWING:
                return self._handle_review(user_response, collected_data)
            else:
                raise ValueError(f"Invalid conversation state: {current_state}")
        except Exception as e:
            self.logger.error(f"Error processing user response: {str(e)}")
            return self._generate_error_response(str(e))

    def _handle_initial_state(self, user_response: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the initial state of the conversation."""
        collected_data["first_name"] = user_response.strip()
        return {
            "state": ConversationState.COLLECTING_PERSONAL_INFO,
            "messages": [
                {
                    "type": "bot",
                    "content": f"Nice to meet you, {collected_data['first_name']}! Let's talk about your income. You can tell me about your jobs, investments, or any other money you received last year. What would you like to start with?",
                    "input_type": "text"
                }
            ],
            "collected_data": collected_data
        }

    def _handle_personal_info_collection(self, user_response: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collection of personal information."""
        if not user_response.strip():
            return {
                "state": ConversationState.INITIAL,
                "message": "I didn't catch that. Could you please provide your name?",
                "collected_data": {}
            }
        
        # Store the name
        collected_data["first_name"] = user_response.strip()
        
        # Move to income collection
        return {
            "state": ConversationState.COLLECTING_INCOME,
            "message": f"Nice to meet you, {user_response.strip()}! Let's start with your income information. What types of income did you have this year?",
            "collected_data": collected_data
        }

    def _handle_income_collection(self, user_response: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle income information collection using natural language processing."""
        # Check for income patterns
        for form_type, patterns in self.income_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_response.lower())
                if match:
                    # Extract the entity (e.g., employer name)
                    entity = match.group(1) if len(match.groups()) > 0 else None
                    
                    # Start collecting specific information
                    form_type_enum = TaxFormType(form_type.upper())
                    form_template = self.form_templates[form_type_enum]
                    current_field = form_template["fields"][0]
                    
                    return {
                        "state": ConversationState.COLLECTING_INCOME,
                        "messages": [
                            {
                                "type": "bot",
                                "content": f"I see you mentioned {form_template['description']}. Let me ask you a few questions about that. What is the {current_field}?",
                                "input_type": "text",
                                "validation": form_template["validation"][current_field].__dict__
                            }
                        ],
                        "collected_data": collected_data,
                        "current_form": form_type_enum.value,
                        "current_field": current_field
                    }

        # If no specific income pattern is recognized, ask for clarification
        return {
            "state": ConversationState.COLLECTING_INCOME,
            "messages": [
                {
                    "type": "bot",
                    "content": "I'm not sure I understood. Could you tell me more about your income? For example, you could say 'I work at ABC Company' or 'I received dividends from XYZ Stock'.",
                    "input_type": "text"
                }
            ],
            "collected_data": collected_data
        }

    def _handle_deductions_collection(self, user_response: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deductions collection using natural language processing."""
        # Check for deduction patterns
        for deduction_type, patterns in self.deduction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_response.lower()):
                    # Start collecting specific information about the deduction
                    return {
                        "state": ConversationState.COLLECTING_DEDUCTIONS,
                        "messages": [
                            {
                                "type": "bot",
                                "content": f"I see you mentioned {deduction_type.replace('_', ' ')}. Could you tell me more about that? For example, how much did you spend on {deduction_type.replace('_', ' ')}?",
                                "input_type": "text"
                            }
                        ],
                        "collected_data": collected_data,
                        "current_deduction": deduction_type
                    }

        # If no specific deduction pattern is recognized, ask for clarification
        return {
            "state": ConversationState.COLLECTING_DEDUCTIONS,
            "messages": [
                {
                    "type": "bot",
                    "content": "I'm not sure I understood. Could you tell me more about your deductions? For example, you could say 'I own a house' or 'I donated to charity'.",
                    "input_type": "text"
                }
            ],
            "collected_data": collected_data
        }

    def _handle_credits_collection(self, user_response: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle credits collection using natural language processing."""
        # Check for credit patterns
        for credit_type, patterns in self.credit_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_response.lower()):
                    # Start collecting specific information about the credit
                    return {
                        "state": ConversationState.COLLECTING_CREDITS,
                        "messages": [
                            {
                                "type": "bot",
                                "content": f"I see you mentioned {credit_type.replace('_', ' ')}. Could you tell me more about that? For example, how many children do you have?",
                                "input_type": "text"
                            }
                        ],
                        "collected_data": collected_data,
                        "current_credit": credit_type
                    }

        # If no specific credit pattern is recognized, ask for clarification
        return {
            "state": ConversationState.COLLECTING_CREDITS,
            "messages": [
                {
                    "type": "bot",
                    "content": "I'm not sure I understood. Could you tell me more about your credits? For example, you could say 'I have children' or 'I'm in college'.",
                    "input_type": "text"
                }
            ],
            "collected_data": collected_data
        }

    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate a user-friendly error response."""
        return {
            "state": ConversationState.INITIAL,
            "message": "I apologize, but I encountered an error. Let's start over. What's your name?",
            "collected_data": {},
            "error": error_message
        }

    # ... (rest of the class implementation remains the same) 