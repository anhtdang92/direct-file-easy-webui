import numpy as np
import logging
from typing import Dict, List, Any

class TaxFeatureExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """
        Extract features from tax data for audit risk assessment
        Returns a list of numerical features
        """
        try:
            features = []
            
            # Income-related features
            features.extend(self._extract_income_features(tax_data))
            
            # Deduction-related features
            features.extend(self._extract_deduction_features(tax_data))
            
            # Business-related features
            features.extend(self._extract_business_features(tax_data))
            
            # Investment-related features
            features.extend(self._extract_investment_features(tax_data))
            
            # Red flag features
            features.extend(self._extract_red_flag_features(tax_data))
            
            return features
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            raise

    def _extract_income_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """Extract features related to income"""
        features = []
        
        # Total income
        total_income = tax_data.get('total_income', 0)
        features.append(total_income)
        
        # Income from multiple sources
        income_sources = len(tax_data.get('income_sources', []))
        features.append(income_sources)
        
        # Income volatility (if historical data available)
        income_history = tax_data.get('income_history', [])
        if income_history:
            income_std = np.std(income_history)
            features.append(income_std)
        else:
            features.append(0)
            
        return features

    def _extract_deduction_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """Extract features related to deductions"""
        features = []
        
        # Total deductions
        total_deductions = tax_data.get('total_deductions', 0)
        features.append(total_deductions)
        
        # Deduction to income ratio
        total_income = tax_data.get('total_income', 1)  # Avoid division by zero
        deduction_ratio = total_deductions / total_income
        features.append(deduction_ratio)
        
        # Number of itemized deductions
        itemized_deductions = len(tax_data.get('itemized_deductions', []))
        features.append(itemized_deductions)
        
        return features

    def _extract_business_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """Extract features related to business income/expenses"""
        features = []
        
        # Business income
        business_income = tax_data.get('business_income', 0)
        features.append(business_income)
        
        # Business expenses
        business_expenses = tax_data.get('business_expenses', 0)
        features.append(business_expenses)
        
        # Business expense to income ratio
        if business_income > 0:
            expense_ratio = business_expenses / business_income
        else:
            expense_ratio = 0
        features.append(expense_ratio)
        
        return features

    def _extract_investment_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """Extract features related to investments"""
        features = []
        
        # Investment income
        investment_income = tax_data.get('investment_income', 0)
        features.append(investment_income)
        
        # Capital gains/losses
        capital_gains = tax_data.get('capital_gains', 0)
        features.append(capital_gains)
        
        # Number of investment transactions
        investment_transactions = len(tax_data.get('investment_transactions', []))
        features.append(investment_transactions)
        
        return features

    def _extract_red_flag_features(self, tax_data: Dict[str, Any]) -> List[float]:
        """Extract features that might be red flags for audits"""
        features = []
        
        # Home office deduction
        home_office_deduction = tax_data.get('home_office_deduction', 0)
        features.append(home_office_deduction)
        
        # Vehicle expenses
        vehicle_expenses = tax_data.get('vehicle_expenses', 0)
        features.append(vehicle_expenses)
        
        # Meal and entertainment expenses
        meal_entertainment = tax_data.get('meal_entertainment_expenses', 0)
        features.append(meal_entertainment)
        
        # Charitable contributions
        charitable_contributions = tax_data.get('charitable_contributions', 0)
        features.append(charitable_contributions)
        
        return features 