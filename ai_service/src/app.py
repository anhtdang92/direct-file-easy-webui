from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import os
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from .document_processor import DocumentProcessor
from .tax_analyzer import TaxAnalyzer
from .cache import CacheMiddleware, get_cache, init_cache_warmup, get_cache_warmup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define response models with examples
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current server timestamp")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-03-20T10:30:00Z"
            }
        }

class ProcessResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the processed document")
    status: str = Field(..., description="Processing status")
    text: str = Field(..., description="Extracted text from the document")
    confidence: float = Field(..., description="OCR confidence score")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")
    metadata: Dict[str, Any] = Field(..., description="Additional document metadata")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "success",
                "text": "Form W-2 Wage and Tax Statement\\nEmployer: ABC Corp\\nEmployee: John Doe\\nWages: $50,000",
                "confidence": 0.95,
                "processing_time": 2.5,
                "metadata": {
                    "file_type": "pdf",
                    "page_count": 1,
                    "document_type": "W-2",
                    "year": 2023
                }
            }
        }

class TaxRecommendation(BaseModel):
    category: str = Field(..., description="Category of the recommendation (e.g., Tax Filing, Investment Strategy)")
    items: List[str] = Field(..., description="List of specific recommendations for this category")

class TaxBracket(BaseModel):
    rate: float = Field(..., description="Tax rate for this bracket (as decimal)")
    min_income: float = Field(..., description="Minimum income for this bracket")
    max_income: Optional[float] = Field(None, description="Maximum income for this bracket (None for highest bracket)")

class TaxCalculation(BaseModel):
    taxable_income: float = Field(..., description="Total taxable income")
    effective_tax_rate: float = Field(..., description="Effective tax rate (as decimal)")
    marginal_tax_rate: float = Field(..., description="Marginal tax rate (as decimal)")
    tax_brackets: List[TaxBracket] = Field(..., description="Applicable tax brackets")
    total_tax: float = Field(..., description="Total tax liability")
    credits: Dict[str, float] = Field(..., description="Available tax credits")
    deductions: Dict[str, float] = Field(..., description="Available deductions")
    estimated_refund: Optional[float] = Field(None, description="Estimated tax refund")
    estimated_payment: Optional[float] = Field(None, description="Estimated tax payment due")
    alternative_minimum_tax: Optional[float] = Field(None, description="Alternative Minimum Tax calculation")
    self_employment_tax: Optional[float] = Field(None, description="Self-employment tax if applicable")
    state_tax_liability: Optional[float] = Field(None, description="State tax liability")
    local_tax_liability: Optional[float] = Field(None, description="Local tax liability")
    foreign_tax_credit: Optional[float] = Field(None, description="Foreign tax credit amount")
    net_investment_income_tax: Optional[float] = Field(None, description="Net Investment Income Tax (NIIT)")
    medicare_surtax: Optional[float] = Field(None, description="Additional Medicare Tax (0.9% on high earners)")
    kiddie_tax: Optional[float] = Field(None, description="Kiddie tax calculation if applicable")
    estimated_tax_penalties: Optional[float] = Field(None, description="Estimated tax underpayment penalties")
    tax_equivalency_yield: Optional[float] = Field(None, description="Tax-equivalency yield for tax-exempt investments")
    marginal_tax_rate_by_income_source: Optional[Dict[str, float]] = Field(None, description="Marginal tax rates by income source")
    tax_loss_carryforward: Optional[float] = Field(None, description="Tax loss carryforward amount")
    tax_gain_carryforward: Optional[float] = Field(None, description="Tax gain carryforward amount")

class InvestmentCalculation(BaseModel):
    cost_basis: float = Field(..., description="Total cost basis")
    current_value: float = Field(..., description="Current market value")
    realized_gains: float = Field(..., description="Realized capital gains")
    unrealized_gains: float = Field(..., description="Unrealized capital gains")
    qualified_dividends: float = Field(..., description="Qualified dividend income")
    ordinary_dividends: float = Field(..., description="Ordinary dividend income")
    tax_efficiency_score: float = Field(..., description="Tax efficiency score (0-1)")
    wash_sale_adjustments: Optional[float] = Field(None, description="Wash sale loss adjustments")
    foreign_tax_paid: Optional[float] = Field(None, description="Foreign taxes paid on investments")
    investment_expenses: Optional[float] = Field(None, description="Investment-related expenses")
    tax_lot_details: Optional[List[Dict[str, Any]]] = Field(None, description="Details of individual tax lots")
    portfolio_turnover: Optional[float] = Field(None, description="Portfolio turnover rate")
    tax_loss_carryforward: Optional[float] = Field(None, description="Tax loss carryforward amount")
    tax_gain_carryforward: Optional[float] = Field(None, description="Tax gain carryforward amount")
    investment_income_tax: Optional[float] = Field(None, description="Tax on investment income")
    capital_gains_tax: Optional[float] = Field(None, description="Tax on capital gains")
    qualified_dividend_tax: Optional[float] = Field(None, description="Tax on qualified dividends")
    ordinary_dividend_tax: Optional[float] = Field(None, description="Tax on ordinary dividends")
    investment_expense_deductions: Optional[float] = Field(None, description="Deductible investment expenses")
    tax_lot_optimization: Optional[Dict[str, Any]] = Field(None, description="Tax lot optimization recommendations")
    wash_sale_analysis: Optional[Dict[str, Any]] = Field(None, description="Wash sale analysis and recommendations")
    portfolio_tax_efficiency: Optional[Dict[str, float]] = Field(None, description="Tax efficiency metrics by asset class")
    tax_loss_harvesting_opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Potential tax loss harvesting opportunities")
    tax_gain_deferral_opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Potential tax gain deferral opportunities")
    investment_tax_credits: Optional[Dict[str, float]] = Field(None, description="Available investment-related tax credits")
    tax_equivalent_yield: Optional[Dict[str, float]] = Field(None, description="Tax-equivalent yields by investment type")
    tax_optimization_recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Investment tax optimization recommendations")

class RetirementCalculation(BaseModel):
    total_contributions: float = Field(..., description="Total retirement contributions")
    employer_match: float = Field(..., description="Employer matching contributions")
    catch_up_contributions: Optional[float] = Field(None, description="Catch-up contributions if eligible")
    roth_conversion_opportunity: Optional[Dict[str, Any]] = Field(None, description="Roth conversion analysis and opportunity")
    backdoor_roth_eligibility: Optional[Dict[str, Any]] = Field(None, description="Backdoor Roth IRA eligibility and analysis")
    mega_backdoor_roth_eligibility: Optional[Dict[str, Any]] = Field(None, description="Mega backdoor Roth eligibility and analysis")
    hsa_contribution_limit: Optional[float] = Field(None, description="HSA contribution limit")
    ira_contribution_limit: Optional[float] = Field(None, description="IRA contribution limit")
    retirement_income_projection: Optional[Dict[str, Any]] = Field(None, description="Projected retirement income analysis")
    required_minimum_distributions: Optional[Dict[str, Any]] = Field(None, description="RMD calculations and requirements")
    retirement_tax_optimization: Optional[Dict[str, Any]] = Field(None, description="Retirement tax optimization strategies")
    retirement_contribution_timing: Optional[Dict[str, Any]] = Field(None, description="Optimal contribution timing analysis")
    retirement_account_rollover: Optional[Dict[str, Any]] = Field(None, description="Retirement account rollover analysis")
    retirement_income_tax_bracket: Optional[Dict[str, Any]] = Field(None, description="Projected retirement tax bracket")
    retirement_tax_credits: Optional[Dict[str, float]] = Field(None, description="Available retirement-related tax credits")
    retirement_tax_deductions: Optional[Dict[str, float]] = Field(None, description="Available retirement-related deductions")
    retirement_tax_penalties: Optional[Dict[str, float]] = Field(None, description="Potential retirement-related tax penalties")
    retirement_tax_planning: Optional[Dict[str, Any]] = Field(None, description="Comprehensive retirement tax planning strategy")

class TaxFormCalculation(BaseModel):
    form_1040: Dict[str, Any] = Field(..., description="Form 1040 calculations and data")
    schedule_a: Optional[Dict[str, Any]] = Field(None, description="Schedule A (Itemized Deductions) calculations")
    schedule_b: Optional[Dict[str, Any]] = Field(None, description="Schedule B (Interest and Dividends) calculations")
    schedule_c: Optional[Dict[str, Any]] = Field(None, description="Schedule C (Business Income) calculations")
    schedule_d: Optional[Dict[str, Any]] = Field(None, description="Schedule D (Capital Gains) calculations")
    schedule_e: Optional[Dict[str, Any]] = Field(None, description="Schedule E (Rental Income) calculations")
    schedule_f: Optional[Dict[str, Any]] = Field(None, description="Schedule F (Farm Income) calculations")
    form_8949: Optional[Dict[str, Any]] = Field(None, description="Form 8949 (Sales of Capital Assets) calculations")
    form_8960: Optional[Dict[str, Any]] = Field(None, description="Form 8960 (Net Investment Income Tax) calculations")
    form_8962: Optional[Dict[str, Any]] = Field(None, description="Form 8962 (Premium Tax Credit) calculations")
    form_8889: Optional[Dict[str, Any]] = Field(None, description="Form 8889 (Health Savings Accounts) calculations")
    form_8606: Optional[Dict[str, Any]] = Field(None, description="Form 8606 (Nondeductible IRAs) calculations")
    form_8915: Optional[Dict[str, Any]] = Field(None, description="Form 8915 (Qualified Disaster Distributions) calculations")
    form_8915_e: Optional[Dict[str, Any]] = Field(None, description="Form 8915-E (Coronavirus Distributions) calculations")
    form_8915_f: Optional[Dict[str, Any]] = Field(None, description="Form 8915-F (Disaster Distributions) calculations")
    form_8915_g: Optional[Dict[str, Any]] = Field(None, description="Form 8915-G (Disaster Distributions) calculations")
    form_8915_h: Optional[Dict[str, Any]] = Field(None, description="Form 8915-H (Disaster Distributions) calculations")
    form_8915_i: Optional[Dict[str, Any]] = Field(None, description="Form 8915-I (Disaster Distributions) calculations")
    form_8915_j: Optional[Dict[str, Any]] = Field(None, description="Form 8915-J (Disaster Distributions) calculations")
    form_8915_k: Optional[Dict[str, Any]] = Field(None, description="Form 8915-K (Disaster Distributions) calculations")
    form_8915_l: Optional[Dict[str, Any]] = Field(None, description="Form 8915-L (Disaster Distributions) calculations")
    form_8915_m: Optional[Dict[str, Any]] = Field(None, description="Form 8915-M (Disaster Distributions) calculations")
    form_8915_n: Optional[Dict[str, Any]] = Field(None, description="Form 8915-N (Disaster Distributions) calculations")
    form_8915_o: Optional[Dict[str, Any]] = Field(None, description="Form 8915-O (Disaster Distributions) calculations")
    form_8915_p: Optional[Dict[str, Any]] = Field(None, description="Form 8915-P (Disaster Distributions) calculations")
    form_8915_q: Optional[Dict[str, Any]] = Field(None, description="Form 8915-Q (Disaster Distributions) calculations")
    form_8915_r: Optional[Dict[str, Any]] = Field(None, description="Form 8915-R (Disaster Distributions) calculations")
    form_8915_s: Optional[Dict[str, Any]] = Field(None, description="Form 8915-S (Disaster Distributions) calculations")
    form_8915_t: Optional[Dict[str, Any]] = Field(None, description="Form 8915-T (Disaster Distributions) calculations")
    form_8915_u: Optional[Dict[str, Any]] = Field(None, description="Form 8915-U (Disaster Distributions) calculations")
    form_8915_v: Optional[Dict[str, Any]] = Field(None, description="Form 8915-V (Disaster Distributions) calculations")
    form_8915_w: Optional[Dict[str, Any]] = Field(None, description="Form 8915-W (Disaster Distributions) calculations")
    form_8915_x: Optional[Dict[str, Any]] = Field(None, description="Form 8915-X (Disaster Distributions) calculations")
    form_8915_y: Optional[Dict[str, Any]] = Field(None, description="Form 8915-Y (Disaster Distributions) calculations")
    form_8915_z: Optional[Dict[str, Any]] = Field(None, description="Form 8915-Z (Disaster Distributions) calculations")

class TaxOptimizationStrategy(BaseModel):
    name: str = Field(..., description="Name of the tax optimization strategy")
    description: str = Field(..., description="Detailed description of the strategy")
    potential_savings: float = Field(..., description="Estimated potential tax savings")
    implementation_steps: List[str] = Field(..., description="Step-by-step implementation instructions")
    risk_level: str = Field(..., description="Risk level (Low/Medium/High)")
    time_horizon: str = Field(..., description="Time horizon for implementation")
    documentation_required: List[str] = Field(..., description="Required documentation")
    eligibility_criteria: List[str] = Field(..., description="Eligibility criteria")
    limitations: List[str] = Field(..., description="Strategy limitations")
    tax_forms_affected: List[str] = Field(..., description="Affected tax forms")
    tax_year_applicability: List[int] = Field(..., description="Applicable tax years")
    state_specific_considerations: Optional[Dict[str, Any]] = Field(None, description="State-specific considerations")
    alternative_strategies: Optional[List[Dict[str, Any]]] = Field(None, description="Alternative strategies to consider")
    tax_law_changes: Optional[Dict[str, Any]] = Field(None, description="Relevant tax law changes")
    implementation_timeline: Optional[Dict[str, Any]] = Field(None, description="Detailed implementation timeline")
    cost_benefit_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost-benefit analysis")
    tax_impact_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed tax impact analysis")
    compliance_requirements: Optional[Dict[str, Any]] = Field(None, description="Compliance requirements")
    audit_risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Audit risk assessment")
    documentation_retention: Optional[Dict[str, Any]] = Field(None, description="Documentation retention requirements")
    tax_planning_opportunities: Optional[Dict[str, Any]] = Field(None, description="Related tax planning opportunities")
    tax_credits_available: Optional[Dict[str, Any]] = Field(None, description="Available tax credits")
    tax_deductions_available: Optional[Dict[str, Any]] = Field(None, description="Available tax deductions")
    tax_exemptions_available: Optional[Dict[str, Any]] = Field(None, description="Available tax exemptions")
    tax_deferral_opportunities: Optional[Dict[str, Any]] = Field(None, description="Tax deferral opportunities")
    tax_avoidance_opportunities: Optional[Dict[str, Any]] = Field(None, description="Tax avoidance opportunities")
    tax_mitigation_opportunities: Optional[Dict[str, Any]] = Field(None, description="Tax mitigation opportunities")
    tax_optimization_opportunities: Optional[Dict[str, Any]] = Field(None, description="Tax optimization opportunities")
    tax_planning_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax planning strategies")
    tax_optimization_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax optimization strategies")
    tax_mitigation_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax mitigation strategies")
    tax_avoidance_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax avoidance strategies")
    tax_deferral_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax deferral strategies")
    tax_credits_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax credits strategies")
    tax_deductions_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax deductions strategies")
    tax_exemptions_strategies: Optional[Dict[str, Any]] = Field(None, description="Related tax exemptions strategies")
    tax_planning_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax planning tools")
    tax_optimization_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax optimization tools")
    tax_mitigation_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax mitigation tools")
    tax_avoidance_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax avoidance tools")
    tax_deferral_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax deferral tools")
    tax_credits_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax credits tools")
    tax_deductions_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax deductions tools")
    tax_exemptions_tools: Optional[Dict[str, Any]] = Field(None, description="Related tax exemptions tools")

class AnalyzeResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the processed document")
    doc_type: str = Field(..., description="Type of document analyzed")
    analysis: Dict[str, Any] = Field(..., description="Analysis results including extracted values and calculations")
    tax_calculations: TaxCalculation = Field(..., description="Detailed tax calculations")
    investment_calculations: Optional[InvestmentCalculation] = Field(None, description="Investment-related calculations if applicable")
    retirement_calculations: Optional[RetirementCalculation] = Field(None, description="Retirement-related calculations if applicable")
    tax_optimization_strategies: List[TaxOptimizationStrategy] = Field(..., description="Recommended tax optimization strategies")
    recommendations: List[TaxRecommendation] = Field(..., description="Detailed tax recommendations organized by category")
    confidence: float = Field(..., description="Confidence score of the analysis (0-1)")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "doc_type": "W-2",
                "analysis": {
                    "wages": 75000.00,
                    "federal_tax": 15000.00,
                    "state_tax": 3750.00,
                    "social_security": 4650.00,
                    "medicare": 1088.00,
                    "estimated_tax_rate": 20.00,
                    "has_retirement_plan": true,
                    "has_health_insurance": true
                },
                "tax_calculations": {
                    "taxable_income": 75000.00,
                    "effective_tax_rate": 0.20,
                    "marginal_tax_rate": 0.22,
                    "tax_brackets": [
                        {
                            "rate": 0.10,
                            "min_income": 0.00,
                            "max_income": 11000.00
                        },
                        {
                            "rate": 0.12,
                            "min_income": 11000.00,
                            "max_income": 44725.00
                        },
                        {
                            "rate": 0.22,
                            "min_income": 44725.00,
                            "max_income": 95375.00
                        }
                    ],
                    "total_tax": 15000.00,
                    "credits": {
                        "retirement_savings": 200.00,
                        "child_tax_credit": 0.00,
                        "education_credit": 0.00
                    },
                    "deductions": {
                        "standard_deduction": 13850.00,
                        "retirement_contributions": 5000.00,
                        "health_insurance": 2400.00
                    },
                    "estimated_refund": 500.00,
                    "estimated_payment": None,
                    "alternative_minimum_tax": 0.00,
                    "self_employment_tax": 0.00,
                    "state_tax_liability": 3750.00,
                    "local_tax_liability": 0.00,
                    "foreign_tax_credit": 0.00,
                    "net_investment_income_tax": 0.00
                },
                "investment_calculations": {
                    "cost_basis": 50000.00,
                    "current_value": 55000.00,
                    "realized_gains": 2000.00,
                    "unrealized_gains": 3000.00,
                    "qualified_dividends": 1000.00,
                    "ordinary_dividends": 500.00,
                    "tax_efficiency_score": 0.85,
                    "wash_sale_adjustments": 0.00,
                    "foreign_tax_paid": 0.00,
                    "investment_expenses": 200.00,
                    "tax_lot_details": [
                        {
                            "purchase_date": "2023-01-15",
                            "purchase_price": 100.00,
                            "quantity": 100,
                            "current_value": 110.00
                        }
                    ],
                    "portfolio_turnover": 0.15,
                    "tax_loss_carryforward": 0.00,
                    "tax_gain_carryforward": 0.00
                },
                "retirement_calculations": {
                    "total_contributions": 5000.00,
                    "employer_match": 2500.00,
                    "tax_deferred_amount": 5000.00,
                    "tax_free_amount": 0.00,
                    "projected_balance": 75000.00,
                    "required_minimum_distribution": None,
                    "catch_up_contributions": 0.00,
                    "roth_conversion_opportunity": 10000.00,
                    "backdoor_roth_opportunity": true,
                    "mega_backdoor_roth_opportunity": false,
                    "hsa_contribution_limit": 3650.00,
                    "ira_contribution_limit": 6000.00,
                    "roth_ira_contribution_limit": 6000.00,
                    "retirement_income_projection": {
                        "social_security": 25000.00,
                        "pension": 0.00,
                        "investment_income": 30000.00,
                        "part_time_work": 0.00
                    }
                },
                "tax_optimization_strategies": [
                    {
                        "name": "Roth Conversion",
                        "description": "Convert Traditional IRA to Roth IRA",
                        "potential_savings": 2200.00,
                        "implementation_steps": [
                            "Review current tax bracket",
                            "Calculate optimal conversion amount",
                            "Execute conversion with custodian",
                            "Pay taxes on conversion amount",
                            "File Form 8606"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Immediate",
                        "documentation_required": [
                            "Form 8606",
                            "Conversion confirmation from custodian",
                            "Tax payment documentation"
                        ],
                        "eligibility_criteria": [
                            "Must have Traditional IRA balance",
                            "Must have funds to pay conversion tax",
                            "Must be under income limits for direct Roth contributions"
                        ],
                        "limitations": [
                            "Must pay taxes on conversion amount",
                            "May affect Medicare premiums"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 8606"],
                        "tax_year_applicability": [2023],
                        "state_specific_considerations": {
                            "state_tax_treatment": "Varies by state",
                            "state_tax_impact": "May have state tax implications"
                        }
                    },
                    {
                        "name": "Tax-Loss Harvesting",
                        "description": "Sell losing positions and purchase similar but not identical securities",
                        "potential_savings": 440.00,
                        "implementation_steps": [
                            "Identify losing positions",
                            "Find similar replacement securities",
                            "Execute trades",
                            "Document cost basis",
                            "Track wash sale period"
                        ],
                        "risk_level": "Medium",
                        "time_horizon": "Short-term",
                        "documentation_required": [
                            "Trade confirmations",
                            "Cost basis records",
                            "Wash sale documentation"
                        ],
                        "eligibility_criteria": [
                            "Must have taxable investment account",
                            "Must have losing positions",
                            "Must be able to find suitable replacement securities"
                        ],
                        "limitations": [
                            "Must wait 30 days to repurchase",
                            "May affect investment strategy"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 8949"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Qualified Charitable Distribution (QCD)",
                        "description": "Direct IRA distribution to charity for those over 70.5",
                        "potential_savings": 1800.00,
                        "implementation_steps": [
                            "Verify age eligibility",
                            "Identify qualified charities",
                            "Contact IRA custodian",
                            "Execute QCD",
                            "Document distribution"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Annual",
                        "documentation_required": [
                            "IRA distribution records",
                            "Charity acknowledgment",
                            "QCD documentation"
                        ],
                        "eligibility_criteria": [
                            "Must be 70.5 or older",
                            "Must have Traditional IRA",
                            "Must be charitably inclined"
                        ],
                        "limitations": [
                            "Maximum $100,000 per year",
                            "Must be direct to charity",
                            "Cannot receive benefit in return"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Donor-Advised Fund (DAF) Contribution",
                        "description": "Contribute appreciated securities to a DAF",
                        "potential_savings": 1500.00,
                        "implementation_steps": [
                            "Identify appreciated securities",
                            "Select DAF provider",
                            "Transfer securities",
                            "Document contribution",
                            "Plan future grants"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Immediate",
                        "documentation_required": [
                            "Transfer records",
                            "DAF contribution acknowledgment",
                            "Cost basis documentation"
                        ],
                        "eligibility_criteria": [
                            "Must have appreciated securities",
                            "Must be charitably inclined",
                            "Must meet DAF minimum contribution"
                        ],
                        "limitations": [
                            "Minimum contribution requirements",
                            "Cannot reclaim contributed assets",
                            "Must make grants within timeframe"
                        ],
                        "tax_forms_affected": ["Form 1040", "Schedule A"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Health Savings Account (HSA) Optimization",
                        "description": "Maximize HSA contributions and investment growth",
                        "potential_savings": 1200.00,
                        "implementation_steps": [
                            "Verify HDHP eligibility",
                            "Calculate maximum contribution",
                            "Set up payroll deductions",
                            "Invest HSA funds",
                            "Document medical expenses"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Annual",
                        "documentation_required": [
                            "HDHP documentation",
                            "Contribution records",
                            "Medical expense receipts"
                        ],
                        "eligibility_criteria": [
                            "Must have HDHP coverage",
                            "No other health coverage",
                            "Not enrolled in Medicare"
                        ],
                        "limitations": [
                            "Annual contribution limits",
                            "Must have HDHP",
                            "Cannot contribute after Medicare"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 8889"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Backdoor Roth IRA",
                        "description": "Contribute to Traditional IRA and convert to Roth",
                        "potential_savings": 900.00,
                        "implementation_steps": [
                            "Contribute to Traditional IRA",
                            "Wait for settlement",
                            "Convert to Roth IRA",
                            "File Form 8606",
                            "Document conversion"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Annual",
                        "documentation_required": [
                            "Contribution records",
                            "Conversion records",
                            "Form 8606"
                        ],
                        "eligibility_criteria": [
                            "Must have earned income",
                            "Must be under age 70.5",
                            "No existing Traditional IRA balances"
                        ],
                        "limitations": [
                            "Annual contribution limits",
                            "Pro-rata rule considerations",
                            "Must have no existing Traditional IRA"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 8606"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Mega Backdoor Roth",
                        "description": "After-tax 401(k) contributions converted to Roth",
                        "potential_savings": 1100.00,
                        "implementation_steps": [
                            "Verify plan allows after-tax contributions",
                            "Verify in-service distributions",
                            "Make after-tax contributions",
                            "Convert to Roth",
                            "Document conversion"
                        ],
                        "risk_level": "Medium",
                        "time_horizon": "Annual",
                        "documentation_required": [
                            "401(k) plan documents",
                            "Contribution records",
                            "Conversion records"
                        ],
                        "eligibility_criteria": [
                            "Must have 401(k) plan",
                            "Plan must allow after-tax contributions",
                            "Plan must allow in-service distributions"
                        ],
                        "limitations": [
                            "Plan-specific limits",
                            "Total contribution limits",
                            "Plan feature availability"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                        "tax_year_applicability": [2023]
                    },
                    {
                        "name": "Tax-Efficient Asset Location",
                        "description": "Optimize asset placement across account types",
                        "potential_savings": 800.00,
                        "implementation_steps": [
                            "Review all investment accounts",
                            "Identify tax-inefficient holdings",
                            "Analyze current asset location",
                            "Develop relocation plan",
                            "Execute trades"
                        ],
                        "risk_level": "Low",
                        "time_horizon": "Ongoing",
                        "documentation_required": [
                            "Account statements",
                            "Trade records",
                            "Cost basis documentation"
                        ],
                        "eligibility_criteria": [
                            "Must have multiple account types",
                            "Must have tax-inefficient holdings",
                            "Must have flexibility to move assets"
                        ],
                        "limitations": [
                            "Account transfer restrictions",
                            "Trading costs",
                            "Market timing considerations"
                        ],
                        "tax_forms_affected": ["Form 1040", "Form 8949"],
                        "tax_year_applicability": [2023]
                    }
                ],
                "recommendations": [
                    {
                        "category": "Tax Filing",
                        "items": [
                            "Report wages on Form 1040, Line 1",
                            "Include federal tax withheld on Line 25a",
                            "Report state tax on Schedule A if itemizing",
                            "Verify social security and medicare amounts match your records"
                        ]
                    }
                ],
                "confidence": 0.95,
                "processing_time": 1.3
            }
        }
    }

class CacheStatsResponse(BaseModel):
    cache: Dict[str, Any] = Field(..., description="Cache statistics")
    warmup: Optional[Dict[str, Any]] = Field(None, description="Cache warmup statistics")

    class Config:
        schema_extra = {
            "example": {
                "cache": {
                    "hits": 1500,
                    "misses": 300,
                    "size": 50,
                    "max_size": 1000,
                    "ttl": 3600
                },
                "warmup": {
                    "enabled": True,
                    "interval": 300,
                    "endpoints": {
                        "/public/tax-rates": {
                            "total_attempts": 100,
                            "successful_attempts": 98,
                            "failed_attempts": 2,
                            "last_success": "2024-03-20T10:25:00Z"
                        }
                    }
                }
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    timestamp: datetime = Field(..., description="Error timestamp")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid file type. Only PDF, JPG, JPEG, and PNG files are supported.",
                "code": "INVALID_FILE_TYPE",
                "timestamp": "2024-03-20T10:30:00Z"
            }
        }

# Initialize FastAPI app with enhanced documentation
app = FastAPI(
    title="Tax Document Analysis API",
    description="""
    A comprehensive API for processing and analyzing tax documents.
    
    ## Features
    * Document processing with OCR
    * Tax document analysis
    * Intelligent caching system
    * Real-time processing status
    
    ## Authentication
    All endpoints require authentication using JWT tokens.
    
    ## Rate Limiting
    * 100 requests per minute for authenticated users
    * 10 requests per minute for unauthenticated users
    
    ## Caching
    * Intelligent caching with configurable TTL
    * Automatic cache warming for frequently accessed endpoints
    * Cache invalidation support
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Documents",
            "description": "Document processing and analysis operations"
        },
        {
            "name": "Cache",
            "description": "Cache management operations"
        },
        {
            "name": "System",
            "description": "System health and status operations"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache and middleware
cache = get_cache()
app.add_middleware(CacheMiddleware, cache=cache)

# Initialize cache warmup
cache_warmup = init_cache_warmup(app, cache)

# Initialize processors
document_processor = DocumentProcessor()
tax_analyzer = TaxAnalyzer()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Start cache warming on application startup."""
    await cache_warmup.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop cache warming on application shutdown."""
    await cache_warmup.stop()

@app.post(
    "/process",
    response_model=ProcessResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid file type or format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid file type. Only PDF, JPG, JPEG, and PNG files are supported.",
                        "code": "INVALID_FILE_TYPE",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        },
        413: {
            "model": ErrorResponse,
            "description": "File too large",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File size exceeds maximum limit of 10MB",
                        "code": "FILE_TOO_LARGE",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to process document: OCR engine error",
                        "code": "PROCESSING_ERROR",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["Documents"],
    summary="Process a tax document",
    description="""
    Process a tax document using OCR and extract relevant information.
    
    - Supports PDF, JPG, JPEG, and PNG files
    - Maximum file size: 10MB
    - Returns extracted text and metadata
    
    ## Supported Document Types
    
    ### W-2 Form
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@w2_form.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "success",
        "text": "Form W-2 Wage and Tax Statement\\nEmployer: ABC Corp\\nEmployee: John Doe\\nWages: $50,000\\nFederal Tax: $7,500\\nState Tax: $2,500\\nSocial Security: $3,100\\nMedicare: $725",
        "confidence": 0.95,
        "processing_time": 2.5,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "W-2",
            "year": 2023,
            "employer_ein": "12-3456789",
            "employee_ssn": "XXX-XX-1234"
        }
    }
    ```
    
    ### 1099-R Form (Retirement Distributions)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_r.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "990e8400-e29b-41d4-a716-446655440004",
        "status": "success",
        "text": "Form 1099-R\\nPayer: Retirement Solutions Inc.\\nRecipient: John Doe\\nGross distribution: $45,000\\nTaxable amount: $40,000\\nFederal tax withheld: $10,000\\nDistribution code: 7\\nIRA/SEP/Simple: Yes",
        "confidence": 0.94,
        "processing_time": 2.2,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-R",
            "year": 2023,
            "payer_tin": "44-5566778",
            "recipient_tin": "XXX-XX-1234",
            "distribution_code": "7",
            "is_ira": true
        }
    }
    ```
    
    ### 1099-G Form (Government Payments)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_g.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "aa0e8400-e29b-41d4-a716-446655440005",
        "status": "success",
        "text": "Form 1099-G\\nPayer: State of California\\nRecipient: Jane Smith\\nUnemployment compensation: $15,000\\nState tax withheld: $1,500\\nLocal tax withheld: $0\\nTax year: 2023",
        "confidence": 0.93,
        "processing_time": 2.0,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-G",
            "year": 2023,
            "payer_tin": "55-6677889",
            "recipient_tin": "XXX-XX-5678",
            "payment_type": "unemployment",
            "state": "CA"
        }
    }
    ```
    
    ### 1099-K Form (Payment Card Transactions)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_k.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "bb0e8400-e29b-41d4-a716-446655440006",
        "status": "success",
        "text": "Form 1099-K\\nPayer: Payment Processor LLC\\nRecipient: John Doe\\nGross amount: $35,000\\nNumber of transactions: 250\\nPayment card transactions: $30,000\\nThird-party network transactions: $5,000",
        "confidence": 0.92,
        "processing_time": 2.3,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-K",
            "year": 2023,
            "payer_tin": "66-7788990",
            "recipient_tin": "XXX-XX-1234",
            "transaction_count": 250,
            "payment_types": ["card", "network"]
        }
    }
    ```
    
    ### 1099-SA Form (HSA Distributions)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_sa.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "cc0e8400-e29b-41d4-a716-446655440007",
        "status": "success",
        "text": "Form 1099-SA\\nPayer: Health Savings Bank\\nRecipient: Jane Smith\\nGross distribution: $8,000\\nEarnings on excess contributions: $100\\nDistribution code: 1\\nHSA account: Yes",
        "confidence": 0.95,
        "processing_time": 1.9,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-SA",
            "year": 2023,
            "payer_tin": "77-8899001",
            "recipient_tin": "XXX-XX-5678",
            "distribution_code": "1",
            "is_hsa": true
        }
    }
    ```
    
    ### 1099-B Form (Broker Transactions)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_b.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "dd0e8400-e29b-41d4-a716-446655440008",
        "status": "success",
        "text": "Form 1099-B\\nPayer: Investment Broker LLC\\nRecipient: John Doe\\nDescription: AAPL Stock\\nDate acquired: 01/15/2022\\nDate sold: 12/15/2023\\nProceeds: $15,000\\nCost basis: $10,000\\nWash sale: No\\nShort-term: Yes",
        "confidence": 0.94,
        "processing_time": 2.4,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-B",
            "year": 2023,
            "payer_tin": "88-9900112",
            "recipient_tin": "XXX-XX-1234",
            "security_type": "stock",
            "holding_period": "short_term",
            "wash_sale": false
        }
    }
    ```
    
    ### 1099-C Form (Cancellation of Debt)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_c.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "ee0e8400-e29b-41d4-a716-446655440009",
        "status": "success",
        "text": "Form 1099-C\\nPayer: ABC Bank\\nRecipient: Jane Smith\\nAmount of debt: $25,000\\nDate of cancellation: 12/31/2023\\nInterest included: $2,500\\nFair market value: $0\\nInsolvent: Yes",
        "confidence": 0.93,
        "processing_time": 2.1,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-C",
            "year": 2023,
            "payer_tin": "99-0011223",
            "recipient_tin": "XXX-XX-5678",
            "debt_type": "credit_card",
            "is_insolvent": true,
            "interest_included": true
        }
    }
    ```
    
    ### 1099-Q Form (Qualified Education Program Payments)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_q.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "ff0e8400-e29b-41d4-a716-446655440010",
        "status": "success",
        "text": "Form 1099-Q\\nPayer: Education Savings Trust\\nRecipient: John Doe\\nGross distribution: $12,000\\nEarnings: $2,000\\nQualified education expenses: $10,000\\nAccount type: 529 Plan",
        "confidence": 0.95,
        "processing_time": 2.0,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-Q",
            "year": 2023,
            "payer_tin": "00-1122334",
            "recipient_tin": "XXX-XX-1234",
            "account_type": "529",
            "is_qualified": true,
            "beneficiary": "Student Name"
        }
    }
    ```
    
    ### 1099-MISC Form (Miscellaneous Income)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_misc.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "gg0e8400-e29b-41d4-a716-446655440011",
        "status": "success",
        "text": "Form 1099-MISC\\nPayer: Consulting Services Inc.\\nRecipient: John Doe\\nNon-employee compensation: $35,000\\nRents: $12,000\\nPrizes and awards: $5,000\\nAttorney fees: $0\\nFederal tax withheld: $3,500",
        "confidence": 0.94,
        "processing_time": 2.2,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-MISC",
            "year": 2023,
            "payer_tin": "11-2233445",
            "recipient_tin": "XXX-XX-1234",
            "income_types": ["non_employee_comp", "rents", "prizes"],
            "is_business": true
        }
    }
    ```
    
    ### 1099-NEC Form (Non-Employee Compensation)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_nec.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "hh0e8400-e29b-41d4-a716-446655440012",
        "status": "success",
        "text": "Form 1099-NEC\\nPayer: Tech Solutions LLC\\nRecipient: Jane Smith\\nNon-employee compensation: $45,000\\nFederal tax withheld: $4,500\\nState tax withheld: $2,250\\nLocal tax withheld: $0",
        "confidence": 0.95,
        "processing_time": 2.1,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-NEC",
            "year": 2023,
            "payer_tin": "22-3344556",
            "recipient_tin": "XXX-XX-5678",
            "is_contractor": true,
            "state": "CA"
        }
    }
    ```
    
    ### 1099-PATR Form (Taxable Distributions Received From Cooperatives)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_patr.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "ii0e8400-e29b-41d4-a716-446655440013",
        "status": "success",
        "text": "Form 1099-PATR\\nPayer: Farmers Cooperative\\nRecipient: John Doe\\nTotal patronage dividends: $8,000\\nQualified payments: $6,000\\nNonqualified payments: $2,000\\nPer-unit retain allocations: $1,000",
        "confidence": 0.93,
        "processing_time": 2.0,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-PATR",
            "year": 2023,
            "payer_tin": "33-4455667",
            "recipient_tin": "XXX-XX-1234",
            "cooperative_type": "agricultural",
            "has_qualified_payments": true
        }
    }
    ```
    
    ### 1099-S Form (Proceeds from Real Estate Transactions)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_s.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "jj0e8400-e29b-41d4-a716-446655440014",
        "status": "success",
        "text": "Form 1099-S\\nPayer: Real Estate Title Co.\\nRecipient: John Doe\\nGross proceeds: $450,000\\nAddress: 123 Main St, City, State 12345\\nDate of closing: 12/15/2023\\nProperty type: Residential\\nBasis: $300,000\\nAdjusted basis: $320,000",
        "confidence": 0.95,
        "processing_time": 2.3,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-S",
            "year": 2023,
            "payer_tin": "44-5566778",
            "recipient_tin": "XXX-XX-1234",
            "property_type": "residential",
            "is_primary_residence": true,
            "state": "CA"
        }
    }
    ```
    
    ### 1099-LTC Form (Long-Term Care and Accelerated Death Benefits)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_ltc.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "kk0e8400-e29b-41d4-a716-446655440015",
        "status": "success",
        "text": "Form 1099-LTC\\nPayer: Health Insurance Co.\\nRecipient: Jane Smith\\nGross benefits: $25,000\\nPer diem payments: $15,000\\nQualified long-term care: $10,000\\nChronically ill: Yes\\nPeriod of service: 01/01/2023 - 12/31/2023",
        "confidence": 0.94,
        "processing_time": 2.1,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-LTC",
            "year": 2023,
            "payer_tin": "55-6677889",
            "recipient_tin": "XXX-XX-5678",
            "is_chronically_ill": true,
            "benefit_type": "long_term_care"
        }
    }
    ```
    
    ### 1099-OID Form (Original Issue Discount)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_oid.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "ll0e8400-e29b-41d4-a716-446655440016",
        "status": "success",
        "text": "Form 1099-OID\\nPayer: Investment Bank\\nRecipient: John Doe\\nOriginal issue discount: $5,000\\nInterest income: $2,000\\nEarly withdrawal penalty: $0\\nDescription: Corporate Bond XYZ\\nIssue date: 01/01/2023\\nMaturity date: 01/01/2028",
        "confidence": 0.93,
        "processing_time": 2.2,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-OID",
            "year": 2023,
            "payer_tin": "66-7788990",
            "recipient_tin": "XXX-XX-1234",
            "instrument_type": "corporate_bond",
            "term": "5_years"
        }
    }
    ```
    
    ### 1099-A Form (Acquisition or Abandonment of Secured Property)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_a.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "mm0e8400-e29b-41d4-a716-446655440017",
        "status": "success",
        "text": "Form 1099-A\\nPayer: ABC Mortgage Co.\\nRecipient: John Doe\\nProperty address: 456 Oak St, City, State 12345\\nDate of acquisition: 12/31/2023\\nBalance of principal: $250,000\\nFair market value: $200,000\\nDescription: Foreclosure\\nPersonal liability: Yes",
        "confidence": 0.94,
        "processing_time": 2.2,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-A",
            "year": 2023,
            "payer_tin": "77-8899001",
            "recipient_tin": "XXX-XX-1234",
            "property_type": "residential",
            "acquisition_type": "foreclosure",
            "has_personal_liability": true
        }
    }
    ```
    
    ### 1099-CAP Form (Changes in Corporate Control and Capital Structure)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_cap.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "nn0e8400-e29b-41d4-a716-446655440018",
        "status": "success",
        "text": "Form 1099-CAP\\nPayer: XYZ Corporation\\nRecipient: John Doe\\nCash received: $50,000\\nStock received: 1000 shares\\nFair market value: $75,000\\nDate of change: 12/15/2023\\nDescription: Merger with ABC Corp",
        "confidence": 0.95,
        "processing_time": 2.3,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-CAP",
            "year": 2023,
            "payer_tin": "88-9900112",
            "recipient_tin": "XXX-XX-1234",
            "transaction_type": "merger",
            "has_cash_component": true,
            "has_stock_component": true
        }
    }
    ```
    
    ### 1099-H Form (Health Coverage Tax Credit)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_h.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "oo0e8400-e29b-41d4-a716-446655440019",
        "status": "success",
        "text": "Form 1099-H\\nPayer: State Health Exchange\\nRecipient: Jane Smith\\nAdvance payments: $3,600\\nCoverage months: 12\\nMonthly premium: $300\\nQualified health plan: Yes\\nCoverage type: Family",
        "confidence": 0.93,
        "processing_time": 2.1,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-H",
            "year": 2023,
            "payer_tin": "99-0011223",
            "recipient_tin": "XXX-XX-5678",
            "coverage_type": "family",
            "is_qualified_plan": true,
            "state": "CA"
        }
    }
    ```
    
    ### 1099-MA Form (Medicare Advantage MSA)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_ma.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "pp0e8400-e29b-41d4-a716-446655440020",
        "status": "success",
        "text": "Form 1099-MA\\nPayer: Medicare Advantage MSA\\nRecipient: John Doe\\nTotal contributions: $3,000\\nTotal distributions: $2,500\\nQualified medical expenses: $2,200\\nNon-qualified distributions: $300\\nAccount type: Individual\\nTax year: 2023",
        "confidence": 0.94,
        "processing_time": 2.2,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-MA",
            "year": 2023,
            "payer_tin": "66-7788990",
            "recipient_tin": "XXX-XX-1234",
            "account_type": "individual",
            "has_qualified_expenses": true,
            "has_non_qualified_distributions": true
        }
    }
    ```
    
    ### 1099-QA Form (Distributions from ABLE Accounts)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_qa.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "qq0e8400-e29b-41d4-a716-446655440021",
        "status": "success",
        "text": "Form 1099-QA\\nPayer: State ABLE Program\\nRecipient: Jane Smith\\nTotal contributions: $15,000\\nTotal distributions: $12,000\\nQualified disability expenses: $10,000\\nNon-qualified distributions: $2,000\\nAccount type: ABLE\\nTax year: 2023",
        "confidence": 0.95,
        "processing_time": 2.3,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-QA",
            "year": 2023,
            "payer_tin": "55-6677889",
            "recipient_tin": "XXX-XX-5678",
            "account_type": "able",
            "has_qualified_expenses": true,
            "has_non_qualified_distributions": true,
            "state": "NY"
        }
    }
    ```
    
    ### 1099-RB Form (Distributions From an MEP)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/process" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@1099_rb.pdf" \\
         -F "cache=true"
    
    # Example Response
    {
        "document_id": "rr0e8400-e29b-41d4-a716-446655440022",
        "status": "success",
        "text": "Form 1099-RB\\nPayer: Multiple Employer Plan\\nRecipient: John Doe\\nGross distribution: $50,000\\nTaxable amount: $45,000\\nEmployee contributions: $5,000\\nDistribution code: 7\\nIRA/SEP/SIMPLE: No\\nTax year: 2023",
        "confidence": 0.93,
        "processing_time": 2.1,
        "metadata": {
            "file_type": "pdf",
            "page_count": 1,
            "document_type": "1099-RB",
            "year": 2023,
            "payer_tin": "44-5566778",
            "recipient_tin": "XXX-XX-1234",
            "distribution_code": "7",
            "is_ira": false,
            "has_employee_contributions": true
        }
    }
    ```
    """
)
async def process_document(
    file: UploadFile = File(..., description="The tax document to process"),
    cache: bool = Query(True, description="Whether to cache the results")
) -> ProcessResponse:
    """Process a tax document."""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise HTTPException(
                status_code=400,
                detail={
                    "detail": "Invalid file type",
                    "code": "INVALID_FILE_TYPE",
                    "timestamp": datetime.now()
                }
            )
        
        # Save file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document
        result = document_processor.process_document(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return ProcessResponse(
            document_id=str(uuid.uuid4()),
            status="success",
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "code": "PROCESSING_ERROR",
                "timestamp": datetime.now()
            }
        )

@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        200: {
            "description": "Successful analysis",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "aa0e8400-e29b-41d4-a716-446655440000",
                        "doc_type": "W-2",
                        "analysis": {
                            "wages": 75000.00,
                            "federal_tax": 15000.00,
                            "state_tax": 3750.00,
                            "social_security": 4650.00,
                            "medicare": 1088.00,
                            "estimated_tax_rate": 20.00,
                            "has_retirement_plan": true,
                            "has_health_insurance": true
                        },
                        "tax_calculations": {
                            "taxable_income": 75000.00,
                            "effective_tax_rate": 0.20,
                            "marginal_tax_rate": 0.22,
                            "tax_brackets": [
                                {
                                    "rate": 0.10,
                                    "min_income": 0.00,
                                    "max_income": 11000.00
                                },
                                {
                                    "rate": 0.12,
                                    "min_income": 11000.00,
                                    "max_income": 44725.00
                                },
                                {
                                    "rate": 0.22,
                                    "min_income": 44725.00,
                                    "max_income": 95375.00
                                }
                            ],
                            "total_tax": 15000.00,
                            "credits": {
                                "retirement_savings": 200.00,
                                "child_tax_credit": 0.00,
                                "education_credit": 0.00
                            },
                            "deductions": {
                                "standard_deduction": 13850.00,
                                "retirement_contributions": 5000.00,
                                "health_insurance": 2400.00
                            },
                            "estimated_refund": 500.00,
                            "estimated_payment": None,
                            "alternative_minimum_tax": 0.00,
                            "self_employment_tax": 0.00,
                            "state_tax_liability": 3750.00,
                            "local_tax_liability": 0.00,
                            "foreign_tax_credit": 0.00,
                            "net_investment_income_tax": 0.00
                        },
                        "investment_calculations": {
                            "cost_basis": 50000.00,
                            "current_value": 55000.00,
                            "realized_gains": 2000.00,
                            "unrealized_gains": 3000.00,
                            "qualified_dividends": 1000.00,
                            "ordinary_dividends": 500.00,
                            "tax_efficiency_score": 0.85,
                            "wash_sale_adjustments": 0.00,
                            "foreign_tax_paid": 0.00,
                            "investment_expenses": 200.00,
                            "tax_lot_details": [
                                {
                                    "purchase_date": "2023-01-15",
                                    "purchase_price": 100.00,
                                    "quantity": 100,
                                    "current_value": 110.00
                                }
                            ],
                            "portfolio_turnover": 0.15,
                            "tax_loss_carryforward": 0.00,
                            "tax_gain_carryforward": 0.00
                        },
                        "retirement_calculations": {
                            "total_contributions": 5000.00,
                            "employer_match": 2500.00,
                            "tax_deferred_amount": 5000.00,
                            "tax_free_amount": 0.00,
                            "projected_balance": 75000.00,
                            "required_minimum_distribution": None,
                            "catch_up_contributions": 0.00,
                            "roth_conversion_opportunity": 10000.00,
                            "backdoor_roth_opportunity": true,
                            "mega_backdoor_roth_opportunity": false,
                            "hsa_contribution_limit": 3650.00,
                            "ira_contribution_limit": 6000.00,
                            "roth_ira_contribution_limit": 6000.00,
                            "retirement_income_projection": {
                                "social_security": 25000.00,
                                "pension": 0.00,
                                "investment_income": 30000.00,
                                "part_time_work": 0.00
                            }
                        },
                        "tax_optimization_strategies": [
                            {
                                "name": "Roth Conversion",
                                "description": "Convert Traditional IRA to Roth IRA",
                                "potential_savings": 2200.00,
                                "implementation_steps": [
                                    "Review current tax bracket",
                                    "Calculate optimal conversion amount",
                                    "Execute conversion with custodian",
                                    "Pay taxes on conversion amount",
                                    "File Form 8606"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Immediate",
                                "documentation_required": [
                                    "Form 8606",
                                    "Conversion confirmation from custodian",
                                    "Tax payment documentation"
                                ],
                                "eligibility_criteria": [
                                    "Must have Traditional IRA balance",
                                    "Must have funds to pay conversion tax",
                                    "Must be under income limits for direct Roth contributions"
                                ],
                                "limitations": [
                                    "Must pay taxes on conversion amount",
                                    "May affect Medicare premiums"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 8606"],
                                "tax_year_applicability": [2023],
                                "state_specific_considerations": {
                                    "state_tax_treatment": "Varies by state",
                                    "state_tax_impact": "May have state tax implications"
                                }
                            },
                            {
                                "name": "Tax-Loss Harvesting",
                                "description": "Sell losing positions and purchase similar but not identical securities",
                                "potential_savings": 440.00,
                                "implementation_steps": [
                                    "Identify losing positions",
                                    "Find similar replacement securities",
                                    "Execute trades",
                                    "Document cost basis",
                                    "Track wash sale period"
                                ],
                                "risk_level": "Medium",
                                "time_horizon": "Short-term",
                                "documentation_required": [
                                    "Trade confirmations",
                                    "Cost basis records",
                                    "Wash sale documentation"
                                ],
                                "eligibility_criteria": [
                                    "Must have taxable investment account",
                                    "Must have losing positions",
                                    "Must be able to find suitable replacement securities"
                                ],
                                "limitations": [
                                    "Must wait 30 days to repurchase",
                                    "May affect investment strategy"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 8949"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Qualified Charitable Distribution (QCD)",
                                "description": "Direct IRA distribution to charity for those over 70.5",
                                "potential_savings": 1800.00,
                                "implementation_steps": [
                                    "Verify age eligibility",
                                    "Identify qualified charities",
                                    "Contact IRA custodian",
                                    "Execute QCD",
                                    "Document distribution"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Annual",
                                "documentation_required": [
                                    "IRA distribution records",
                                    "Charity acknowledgment",
                                    "QCD documentation"
                                ],
                                "eligibility_criteria": [
                                    "Must be 70.5 or older",
                                    "Must have Traditional IRA",
                                    "Must be charitably inclined"
                                ],
                                "limitations": [
                                    "Maximum $100,000 per year",
                                    "Must be direct to charity",
                                    "Cannot receive benefit in return"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Donor-Advised Fund (DAF) Contribution",
                                "description": "Contribute appreciated securities to a DAF",
                                "potential_savings": 1500.00,
                                "implementation_steps": [
                                    "Identify appreciated securities",
                                    "Select DAF provider",
                                    "Transfer securities",
                                    "Document contribution",
                                    "Plan future grants"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Immediate",
                                "documentation_required": [
                                    "Transfer records",
                                    "DAF contribution acknowledgment",
                                    "Cost basis documentation"
                                ],
                                "eligibility_criteria": [
                                    "Must have appreciated securities",
                                    "Must be charitably inclined",
                                    "Must meet DAF minimum contribution"
                                ],
                                "limitations": [
                                    "Minimum contribution requirements",
                                    "Cannot reclaim contributed assets",
                                    "Must make grants within timeframe"
                                ],
                                "tax_forms_affected": ["Form 1040", "Schedule A"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Health Savings Account (HSA) Optimization",
                                "description": "Maximize HSA contributions and investment growth",
                                "potential_savings": 1200.00,
                                "implementation_steps": [
                                    "Verify HDHP eligibility",
                                    "Calculate maximum contribution",
                                    "Set up payroll deductions",
                                    "Invest HSA funds",
                                    "Document medical expenses"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Annual",
                                "documentation_required": [
                                    "HDHP documentation",
                                    "Contribution records",
                                    "Medical expense receipts"
                                ],
                                "eligibility_criteria": [
                                    "Must have HDHP coverage",
                                    "No other health coverage",
                                    "Not enrolled in Medicare"
                                ],
                                "limitations": [
                                    "Annual contribution limits",
                                    "Must have HDHP",
                                    "Cannot contribute after Medicare"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 8889"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Backdoor Roth IRA",
                                "description": "Contribute to Traditional IRA and convert to Roth",
                                "potential_savings": 900.00,
                                "implementation_steps": [
                                    "Contribute to Traditional IRA",
                                    "Wait for settlement",
                                    "Convert to Roth IRA",
                                    "File Form 8606",
                                    "Document conversion"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Annual",
                                "documentation_required": [
                                    "Contribution records",
                                    "Conversion records",
                                    "Form 8606"
                                ],
                                "eligibility_criteria": [
                                    "Must have earned income",
                                    "Must be under age 70.5",
                                    "No existing Traditional IRA balances"
                                ],
                                "limitations": [
                                    "Annual contribution limits",
                                    "Pro-rata rule considerations",
                                    "Must have no existing Traditional IRA"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 8606"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Mega Backdoor Roth",
                                "description": "After-tax 401(k) contributions converted to Roth",
                                "potential_savings": 1100.00,
                                "implementation_steps": [
                                    "Verify plan allows after-tax contributions",
                                    "Verify in-service distributions",
                                    "Make after-tax contributions",
                                    "Convert to Roth",
                                    "Document conversion"
                                ],
                                "risk_level": "Medium",
                                "time_horizon": "Annual",
                                "documentation_required": [
                                    "401(k) plan documents",
                                    "Contribution records",
                                    "Conversion records"
                                ],
                                "eligibility_criteria": [
                                    "Must have 401(k) plan",
                                    "Plan must allow after-tax contributions",
                                    "Plan must allow in-service distributions"
                                ],
                                "limitations": [
                                    "Plan-specific limits",
                                    "Total contribution limits",
                                    "Plan feature availability"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                                "tax_year_applicability": [2023]
                            },
                            {
                                "name": "Tax-Efficient Asset Location",
                                "description": "Optimize asset placement across account types",
                                "potential_savings": 800.00,
                                "implementation_steps": [
                                    "Review all investment accounts",
                                    "Identify tax-inefficient holdings",
                                    "Analyze current asset location",
                                    "Develop relocation plan",
                                    "Execute trades"
                                ],
                                "risk_level": "Low",
                                "time_horizon": "Ongoing",
                                "documentation_required": [
                                    "Account statements",
                                    "Trade records",
                                    "Cost basis documentation"
                                ],
                                "eligibility_criteria": [
                                    "Must have multiple account types",
                                    "Must have tax-inefficient holdings",
                                    "Must have flexibility to move assets"
                                ],
                                "limitations": [
                                    "Account transfer restrictions",
                                    "Trading costs",
                                    "Market timing considerations"
                                ],
                                "tax_forms_affected": ["Form 1040", "Form 8949"],
                                "tax_year_applicability": [2023]
                            }
                        ],
                        "recommendations": [
                            {
                                "category": "Tax Filing",
                                "items": [
                                    "Report wages on Form 1040, Line 1",
                                    "Include federal tax withheld on Line 25a",
                                    "Report state tax on Schedule A if itemizing",
                                    "Verify social security and medicare amounts match your records"
                                ]
                            }
                        ],
                        "confidence": 0.95,
                        "processing_time": 1.3
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    description="""
    Analyze processed document data and extract tax-relevant information.
    
    - Supports W-2 and 1099 forms
    - Returns analysis results and recommendations
    - Includes confidence scores and processing time
    - Provides detailed tax calculations
    - Includes investment and retirement calculations
    - Offers tax optimization strategies
    
    ## Document Type Examples
    
    ### W-2 Form Analysis (with Detailed Tax Calculations)
    ```bash
    # Example Request
    curl -X POST "http://localhost:8000/analyze" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: application/json" \\
         -d '{
             "doc_type": "W-2",
             "text": "Form W-2\\nEmployer: ABC Corp\\nEmployee: John Doe\\nWages: $75,000\\nFederal tax: $15,000\\nState tax: $3,750\\nSocial security: $4,650\\nMedicare: $1,088\\nRetirement plan: Yes\\nHealth insurance: Yes",
             "cache": true
         }'
    
    # Example Response
    {
        "document_id": "aa0e8400-e29b-41d4-a716-446655440000",
        "doc_type": "W-2",
        "analysis": {
            "wages": 75000.00,
            "federal_tax": 15000.00,
            "state_tax": 3750.00,
            "social_security": 4650.00,
            "medicare": 1088.00,
            "estimated_tax_rate": 20.00,
            "has_retirement_plan": true,
            "has_health_insurance": true
        },
        "tax_calculations": {
            "taxable_income": 75000.00,
            "effective_tax_rate": 0.20,
            "marginal_tax_rate": 0.22,
            "tax_brackets": [
                {
                    "rate": 0.10,
                    "min_income": 0.00,
                    "max_income": 11000.00
                },
                {
                    "rate": 0.12,
                    "min_income": 11000.00,
                    "max_income": 44725.00
                },
                {
                    "rate": 0.22,
                    "min_income": 44725.00,
                    "max_income": 95375.00
                }
            ],
            "total_tax": 15000.00,
            "credits": {
                "retirement_savings": 200.00,
                "child_tax_credit": 0.00,
                "education_credit": 0.00
            },
            "deductions": {
                "standard_deduction": 13850.00,
                "retirement_contributions": 5000.00,
                "health_insurance": 2400.00
            },
            "estimated_refund": 500.00,
            "estimated_payment": null,
            "alternative_minimum_tax": 0.00,
            "self_employment_tax": 0.00,
            "state_tax_liability": 3750.00,
            "local_tax_liability": 0.00,
            "foreign_tax_credit": 0.00,
            "net_investment_income_tax": 0.00
        },
        "investment_calculations": {
            "cost_basis": 50000.00,
            "current_value": 55000.00,
            "realized_gains": 2000.00,
            "unrealized_gains": 3000.00,
            "qualified_dividends": 1000.00,
            "ordinary_dividends": 500.00,
            "tax_efficiency_score": 0.85,
            "wash_sale_adjustments": 0.00,
            "foreign_tax_paid": 0.00,
            "investment_expenses": 200.00,
            "tax_lot_details": [
                {
                    "purchase_date": "2023-01-15",
                    "purchase_price": 100.00,
                    "quantity": 100,
                    "current_value": 110.00
                }
            ],
            "portfolio_turnover": 0.15,
            "tax_loss_carryforward": 0.00,
            "tax_gain_carryforward": 0.00
        },
        "retirement_calculations": {
            "total_contributions": 5000.00,
            "employer_match": 2500.00,
            "tax_deferred_amount": 5000.00,
            "tax_free_amount": 0.00,
            "projected_balance": 75000.00,
            "required_minimum_distribution": null,
            "catch_up_contributions": 0.00,
            "roth_conversion_opportunity": 10000.00,
            "backdoor_roth_opportunity": true,
            "mega_backdoor_roth_opportunity": false,
            "hsa_contribution_limit": 3650.00,
            "ira_contribution_limit": 6000.00,
            "roth_ira_contribution_limit": 6000.00,
            "retirement_income_projection": {
                "social_security": 25000.00,
                "pension": 0.00,
                "investment_income": 30000.00,
                "part_time_work": 0.00
            }
        },
        "tax_optimization_strategies": [
            {
                "name": "Roth Conversion",
                "description": "Convert Traditional IRA to Roth IRA",
                "potential_savings": 2200.00,
                "implementation_steps": [
                    "Review current tax bracket",
                    "Calculate optimal conversion amount",
                    "Execute conversion with custodian",
                    "Pay taxes on conversion amount",
                    "File Form 8606"
                ],
                "risk_level": "Low",
                "time_horizon": "Immediate",
                "documentation_required": [
                    "Form 8606",
                    "Conversion confirmation from custodian",
                    "Tax payment documentation"
                ],
                "eligibility_criteria": [
                    "Must have Traditional IRA balance",
                    "Must have funds to pay conversion tax",
                    "Must be under income limits for direct Roth contributions"
                ],
                "limitations": [
                    "Must pay taxes on conversion amount",
                    "May affect Medicare premiums"
                ],
                "tax_forms_affected": ["Form 1040", "Form 8606"],
                "tax_year_applicability": [2023],
                "state_specific_considerations": {
                    "state_tax_treatment": "Varies by state",
                    "state_tax_impact": "May have state tax implications"
                }
            },
            {
                "name": "Tax-Loss Harvesting",
                "description": "Sell losing positions and purchase similar but not identical securities",
                "potential_savings": 440.00,
                "implementation_steps": [
                    "Identify losing positions",
                    "Find similar replacement securities",
                    "Execute trades",
                    "Document cost basis",
                    "Track wash sale period"
                ],
                "risk_level": "Medium",
                "time_horizon": "Short-term",
                "documentation_required": [
                    "Trade confirmations",
                    "Cost basis records",
                    "Wash sale documentation"
                ],
                "eligibility_criteria": [
                    "Must have taxable investment account",
                    "Must have losing positions",
                    "Must be able to find suitable replacement securities"
                ],
                "limitations": [
                    "Must wait 30 days to repurchase",
                    "May affect investment strategy"
                ],
                "tax_forms_affected": ["Form 1040", "Form 8949"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Qualified Charitable Distribution (QCD)",
                "description": "Direct IRA distribution to charity for those over 70.5",
                "potential_savings": 1800.00,
                "implementation_steps": [
                    "Verify age eligibility",
                    "Identify qualified charities",
                    "Contact IRA custodian",
                    "Execute QCD",
                    "Document distribution"
                ],
                "risk_level": "Low",
                "time_horizon": "Annual",
                "documentation_required": [
                    "IRA distribution records",
                    "Charity acknowledgment",
                    "QCD documentation"
                ],
                "eligibility_criteria": [
                    "Must be 70.5 or older",
                    "Must have Traditional IRA",
                    "Must be charitably inclined"
                ],
                "limitations": [
                    "Maximum $100,000 per year",
                    "Must be direct to charity",
                    "Cannot receive benefit in return"
                ],
                "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Donor-Advised Fund (DAF) Contribution",
                "description": "Contribute appreciated securities to a DAF",
                "potential_savings": 1500.00,
                "implementation_steps": [
                    "Identify appreciated securities",
                    "Select DAF provider",
                    "Transfer securities",
                    "Document contribution",
                    "Plan future grants"
                ],
                "risk_level": "Low",
                "time_horizon": "Immediate",
                "documentation_required": [
                    "Transfer records",
                    "DAF contribution acknowledgment",
                    "Cost basis documentation"
                ],
                "eligibility_criteria": [
                    "Must have appreciated securities",
                    "Must be charitably inclined",
                    "Must meet DAF minimum contribution"
                ],
                "limitations": [
                    "Minimum contribution requirements",
                    "Cannot reclaim contributed assets",
                    "Must make grants within timeframe"
                ],
                "tax_forms_affected": ["Form 1040", "Schedule A"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Health Savings Account (HSA) Optimization",
                "description": "Maximize HSA contributions and investment growth",
                "potential_savings": 1200.00,
                "implementation_steps": [
                    "Verify HDHP eligibility",
                    "Calculate maximum contribution",
                    "Set up payroll deductions",
                    "Invest HSA funds",
                    "Document medical expenses"
                ],
                "risk_level": "Low",
                "time_horizon": "Annual",
                "documentation_required": [
                    "HDHP documentation",
                    "Contribution records",
                    "Medical expense receipts"
                ],
                "eligibility_criteria": [
                    "Must have HDHP coverage",
                    "No other health coverage",
                    "Not enrolled in Medicare"
                ],
                "limitations": [
                    "Annual contribution limits",
                    "Must have HDHP",
                    "Cannot contribute after Medicare"
                ],
                "tax_forms_affected": ["Form 1040", "Form 8889"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Backdoor Roth IRA",
                "description": "Contribute to Traditional IRA and convert to Roth",
                "potential_savings": 900.00,
                "implementation_steps": [
                    "Contribute to Traditional IRA",
                    "Wait for settlement",
                    "Convert to Roth IRA",
                    "File Form 8606",
                    "Document conversion"
                ],
                "risk_level": "Low",
                "time_horizon": "Annual",
                "documentation_required": [
                    "Contribution records",
                    "Conversion records",
                    "Form 8606"
                ],
                "eligibility_criteria": [
                    "Must have earned income",
                    "Must be under age 70.5",
                    "No existing Traditional IRA balances"
                ],
                "limitations": [
                    "Annual contribution limits",
                    "Pro-rata rule considerations",
                    "Must have no existing Traditional IRA"
                ],
                "tax_forms_affected": ["Form 1040", "Form 8606"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Mega Backdoor Roth",
                "description": "After-tax 401(k) contributions converted to Roth",
                "potential_savings": 1100.00,
                "implementation_steps": [
                    "Verify plan allows after-tax contributions",
                    "Verify in-service distributions",
                    "Make after-tax contributions",
                    "Convert to Roth",
                    "Document conversion"
                ],
                "risk_level": "Medium",
                "time_horizon": "Annual",
                "documentation_required": [
                    "401(k) plan documents",
                    "Contribution records",
                    "Conversion records"
                ],
                "eligibility_criteria": [
                    "Must have 401(k) plan",
                    "Plan must allow after-tax contributions",
                    "Plan must allow in-service distributions"
                ],
                "limitations": [
                    "Plan-specific limits",
                    "Total contribution limits",
                    "Plan feature availability"
                ],
                "tax_forms_affected": ["Form 1040", "Form 1099-R"],
                "tax_year_applicability": [2023]
            },
            {
                "name": "Tax-Efficient Asset Location",
                "description": "Optimize asset placement across account types",
                "potential_savings": 800.00,
                "implementation_steps": [
                    "Review all investment accounts",
                    "Identify tax-inefficient holdings",
                    "Analyze current asset location",
                    "Develop relocation plan",
                    "Execute trades"
                ],
                "risk_level": "Low",
                "time_horizon": "Ongoing",
                "documentation_required": [
                    "Account statements",
                    "Trade records",
                    "Cost basis documentation"
                ],
                "eligibility_criteria": [
                    "Must have multiple account types",
                    "Must have tax-inefficient holdings",
                    "Must have flexibility to move assets"
                ],
                "limitations": [
                    "Account transfer restrictions",
                    "Trading costs",
                    "Market timing considerations"
                ],
                "tax_forms_affected": ["Form 1040", "Form 8949"],
                "tax_year_applicability": [2023]
            }
        ],
        "recommendations": [
            {
                "category": "Tax Filing",
                "items": [
                    "Report wages on Form 1040, Line 1",
                    "Include federal tax withheld on Line 25a",
                    "Report state tax on Schedule A if itemizing",
                    "Verify social security and medicare amounts match your records"
                ]
            }
        ],
        "confidence": 0.95,
        "processing_time": 1.3
    }
    ```
    """
)
async def analyze_document(
    doc_type: str = Body(..., description="Type of document to analyze"),
    text: str = Body(..., description="Processed document text"),
    cache: bool = Query(True, description="Whether to cache the results")
) -> AnalyzeResponse:
    """Analyze processed document data."""
    try:
        result = tax_analyzer.analyze_document(doc_type, text)
        return AnalyzeResponse(
            document_id=str(uuid.uuid4()),
            doc_type=doc_type,
            analysis=result.get("analysis", {}),
            recommendations=result.get("recommendations", []),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0)
        )
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "code": "ANALYSIS_ERROR",
                "timestamp": datetime.now()
            }
        )

@app.post(
    "/cache/invalidate",
    response_model=Dict[str, str],
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to invalidate cache: Invalid path",
                        "code": "CACHE_ERROR",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["Cache"],
    summary="Invalidate cache for a specific path",
    description="""
    Invalidate the cache for a specific API path.
    
    ## Example Request
    ```bash
    curl -X POST "http://localhost:8000/cache/invalidate" \\
         -H "Authorization: Bearer {token}" \\
         -H "Content-Type: application/json" \\
         -d '{"path": "/public/tax-rates"}'
    ```
    
    ## Example Response
    ```json
    {
        "status": "success",
        "message": "Cache invalidated for /public/tax-rates"
    }
    ```
    """
)
async def invalidate_cache(
    path: str = Body(..., description="API path to invalidate")
) -> Dict[str, str]:
    """Invalidate cache for a specific path."""
    try:
        cache = get_cache()
        cache.delete(path)
        return {"status": "success", "message": f"Cache invalidated for {path}"}
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "code": "CACHE_ERROR",
                "timestamp": datetime.now()
            }
        )

@app.get(
    "/cache/stats",
    response_model=CacheStatsResponse,
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to get cache statistics",
                        "code": "CACHE_ERROR",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["Cache"],
    summary="Get cache statistics",
    description="""
    Get statistics about the cache system and warmup process.
    
    ## Example Request
    ```bash
    curl -X GET "http://localhost:8000/cache/stats" \\
         -H "Authorization: Bearer {token}"
    ```
    
    ## Example Response
    ```json
    {
        "cache": {
            "hits": 1500,
            "misses": 300,
            "size": 50,
            "max_size": 1000,
            "ttl": 3600
        },
        "warmup": {
            "enabled": true,
            "interval": 300,
            "endpoints": {
                "/public/tax-rates": {
                    "total_attempts": 100,
                    "successful_attempts": 98,
                    "failed_attempts": 2,
                    "last_success": "2024-03-20T10:25:00Z"
                }
            }
        }
    }
    ```
    """
)
async def get_cache_stats() -> CacheStatsResponse:
    """Get cache statistics."""
    try:
        cache = get_cache()
        warmup = get_cache_warmup()
        return CacheStatsResponse(
            cache=cache.get_stats(),
            warmup=warmup.get_stats() if warmup else None
        )
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "code": "CACHE_ERROR",
                "timestamp": datetime.now()
            }
        )

@app.post(
    "/cache/warm",
    response_model=Dict[str, Any],
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cache warmup not initialized",
                        "code": "CACHE_ERROR",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["Cache"],
    summary="Manually trigger cache warming",
    description="""
    Manually trigger the cache warming process for all configured endpoints.
    
    ## Example Request
    ```bash
    curl -X POST "http://localhost:8000/cache/warm" \\
         -H "Authorization: Bearer {token}"
    ```
    
    ## Example Response
    ```json
    {
        "status": "success",
        "message": "Cache warming triggered",
        "stats": {
            "enabled": true,
            "interval": 300,
            "endpoints": {
                "/public/tax-rates": {
                    "total_attempts": 100,
                    "successful_attempts": 98,
                    "failed_attempts": 2,
                    "last_success": "2024-03-20T10:25:00Z"
                }
            }
        }
    }
    ```
    """
)
async def warm_cache() -> Dict[str, Any]:
    """Manually trigger cache warming."""
    try:
        warmup = get_cache_warmup()
        if not warmup:
            raise HTTPException(
                status_code=500,
                detail={
                    "detail": "Cache warmup not initialized",
                    "code": "CACHE_ERROR",
                    "timestamp": datetime.now()
                }
            )
        
        # Trigger warmup
        await warmup._warmup_endpoints()
        
        return {
            "status": "success",
            "message": "Cache warming triggered",
            "stats": warmup.get_stats()
        }
    except Exception as e:
        logger.error(f"Error warming cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "code": "CACHE_ERROR",
                "timestamp": datetime.now()
            }
        )

@app.get(
    "/health",
    response_model=HealthResponse,
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service unavailable",
                        "code": "SERVICE_ERROR",
                        "timestamp": "2024-03-20T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["System"],
    summary="Health check endpoint",
    description="""
    Check the health status of the API service.
    
    ## Example Request
    ```bash
    curl -X GET "http://localhost:8000/health"
    ```
    
    ## Example Response
    ```json
    {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-03-20T10:30:00Z"
    }
    ```
    """
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 