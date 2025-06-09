import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging

class AuditRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

    def preprocess_features(self, features):
        """
        Preprocess the input features for the model
        """
        try:
            # Convert features to numpy array
            features_array = np.array(features).reshape(1, -1)
            # Scale features
            scaled_features = self.scaler.transform(features_array)
            return scaled_features
        except Exception as e:
            self.logger.error(f"Error preprocessing features: {str(e)}")
            raise

    def predict_audit_risk(self, features):
        """
        Predict the audit risk score based on input features
        Returns a score between 0 and 1, where:
        0 = Very low risk of audit
        1 = Very high risk of audit
        """
        try:
            # Preprocess features
            processed_features = self.preprocess_features(features)
            # Get probability of high risk
            risk_score = self.model.predict_proba(processed_features)[0][1]
            return float(risk_score)
        except Exception as e:
            self.logger.error(f"Error predicting audit risk: {str(e)}")
            raise

    def train(self, X, y):
        """
        Train the model with provided data
        X: Feature matrix
        y: Target labels (0 for no audit, 1 for audit)
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            # Train model
            self.model.fit(X_scaled, y)
            self.logger.info("Model training completed successfully")
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise

    def save_model(self, model_path, scaler_path):
        """
        Save the trained model and scaler
        """
        try:
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            self.logger.info("Model and scaler saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, model_path, scaler_path):
        """
        Load a trained model and scaler
        """
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.logger.info("Model and scaler loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise 