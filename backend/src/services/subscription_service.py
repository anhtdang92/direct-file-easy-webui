from typing import Dict, Any, List
from datetime import datetime, timedelta

class SubscriptionService:
    def __init__(self):
        self.tiers = {
            "free": {
                "max_tokens_per_month": 10000,
                "available_models": ["gpt-3.5-turbo"],
                "max_documents_per_month": 5,
                "features": [
                    "Basic document analysis",
                    "Standard processing time",
                    "Email support"
                ],
                "price": 0
            },
            "basic": {
                "max_tokens_per_month": 100000,
                "available_models": ["gpt-3.5-turbo", "claude-3-sonnet"],
                "max_documents_per_month": 20,
                "features": [
                    "Advanced document analysis",
                    "Priority processing",
                    "Priority support",
                    "Custom recommendations"
                ],
                "price": 49.99
            },
            "premium": {
                "max_tokens_per_month": 1000000,
                "available_models": ["gpt-3.5-turbo", "gpt-4", "claude-3-opus", "claude-3-sonnet"],
                "max_documents_per_month": 50,
                "features": [
                    "All Basic features",
                    "Real-time processing",
                    "Dedicated support",
                    "API access",
                    "Custom solutions",
                    "Team management"
                ],
                "price": 149.99
            }
        }

    def get_tier_info(self, tier: str) -> Dict[str, Any]:
        """Get information about a specific tier."""
        return self.tiers.get(tier, {})

    def get_all_tiers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available tiers."""
        return self.tiers

    def is_model_available(self, tier: str, model: str) -> bool:
        """Check if a model is available for a specific tier."""
        tier_info = self.get_tier_info(tier)
        return model in tier_info.get("available_models", [])

    def get_token_limit(self, tier: str) -> int:
        """Get the token limit for a specific tier."""
        tier_info = self.get_tier_info(tier)
        return tier_info.get("max_tokens_per_month", 0)

    def get_document_limit(self, tier: str) -> int:
        """Get the document limit for a specific tier."""
        tier_info = self.get_tier_info(tier)
        return tier_info.get("max_documents_per_month", 0)

    def get_features(self, tier: str) -> List[str]:
        """Get the features available for a specific tier."""
        tier_info = self.get_tier_info(tier)
        return tier_info.get("features", [])

    def get_price(self, tier: str) -> float:
        """Get the price for a specific tier."""
        tier_info = self.get_tier_info(tier)
        return tier_info.get("price", 0)

    def calculate_remaining_tokens(self, tier: str, tokens_used: int, last_reset: datetime) -> int:
        """Calculate remaining tokens for the current month."""
        if datetime.now() - last_reset > timedelta(days=30):
            return self.get_token_limit(tier)
        return max(0, self.get_token_limit(tier) - tokens_used)

    def recommend_tier_upgrade(self, current_tier: str, tokens_used: int, documents_processed: int) -> Dict[str, Any]:
        """Recommend a tier upgrade based on usage."""
        current_limit = self.get_token_limit(current_tier)
        current_doc_limit = self.get_document_limit(current_tier)
        
        if tokens_used > current_limit * 0.8 or documents_processed > current_doc_limit * 0.8:
            for tier, info in self.tiers.items():
                if info["max_tokens_per_month"] > current_limit and info["max_documents_per_month"] > current_doc_limit:
                    return {
                        "recommended_tier": tier,
                        "current_tier": current_tier,
                        "reasons": [
                            f"Token usage at {tokens_used}/{current_limit}",
                            f"Documents processed at {documents_processed}/{current_doc_limit}"
                        ],
                        "benefits": info["features"]
                    }
        return {} 