import pytest
from src.services.tax_conversation_service import TaxConversationService, ConversationState
from datetime import datetime

@pytest.fixture
def conversation_service():
    return TaxConversationService()

@pytest.fixture
def initial_data():
    return {
        "conversation_id": "test_conv_123",
        "start_time": datetime.now().isoformat(),
        "user_id": "test_user_123",
        "collected_data": {}
    }

def test_initial_greeting(conversation_service, initial_data):
    """Test the initial greeting message"""
    response = conversation_service.start_conversation()
    
    assert response["state"] == ConversationState.INITIAL
    assert len(response["messages"]) == 1
    assert response["messages"][0]["type"] == "bot"
    assert "Hi" in response["messages"][0]["content"]
    assert "first name" in response["messages"][0]["content"].lower()

def test_healthcare_professional(conversation_service, initial_data):
    """Test conversation with a healthcare professional"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="John",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention being a doctor
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I am a doctor and I have my own practice",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "healthcare" in response["collected_data"]["industry"]
    assert "medical equipment" in response["messages"][0]["content"].lower()

def test_technology_professional(conversation_service, initial_data):
    """Test conversation with a technology professional"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="Sarah",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention being a software developer
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I work as a software developer and I have my own tech consulting business",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "technology" in response["collected_data"]["industry"]
    assert "software licenses" in response["messages"][0]["content"].lower()

def test_real_estate_professional(conversation_service, initial_data):
    """Test conversation with a real estate professional"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="Michael",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention being a realtor
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I am a realtor and I own several rental properties",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "real_estate" in response["collected_data"]["industry"]
    assert "real estate licenses" in response["messages"][0]["content"].lower()

def test_restaurant_owner(conversation_service, initial_data):
    """Test conversation with a restaurant owner"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="Lisa",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention being a restaurant owner
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I own a restaurant and I'm the head chef",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "restaurant" in response["collected_data"]["industry"]
    assert "food service licenses" in response["messages"][0]["content"].lower()

def test_transportation_professional(conversation_service, initial_data):
    """Test conversation with a transportation professional"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="David",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention being a trucker
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I am a long-haul trucker and I own my own trucking company",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "transportation" in response["collected_data"]["industry"]
    assert "transportation licenses" in response["messages"][0]["content"].lower()

def test_multiple_industry_mentions(conversation_service, initial_data):
    """Test handling of multiple industry mentions"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="Alex",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention multiple professions
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I am a software developer and I also own a small restaurant",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Should pick up the first mentioned industry
    assert response["state"] == ConversationState.COLLECTING_DEDUCTIONS
    assert "technology" in response["collected_data"]["industry"]

def test_invalid_input(conversation_service, initial_data):
    """Test handling of invalid input"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide empty name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    assert response["state"] == ConversationState.INITIAL
    assert "please provide" in response["messages"][0]["content"].lower()

def test_unknown_profession(conversation_service, initial_data):
    """Test handling of unknown profession"""
    # Start conversation
    response = conversation_service.start_conversation()
    
    # Provide name
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="Tom",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Mention unknown profession
    response = conversation_service.process_user_response(
        conversation_id=initial_data["conversation_id"],
        user_response="I am a professional juggler",
        current_state=response["state"],
        collected_data=response["collected_data"]
    )
    
    # Should continue with normal flow
    assert response["state"] != ConversationState.COLLECTING_DEDUCTIONS
    assert "industry" not in response["collected_data"] 