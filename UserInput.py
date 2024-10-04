import streamlit as st
from langchain_groq import ChatGroq
from langchain_groq.chat_models import ChatMessage
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize the Groq LLM
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.7, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

# Define required parameters
REQUIRED_PARAMETERS = {
    "destination": "travel destination",
    "departure_city": "departure city",
    "departure_date": "departure date",
    "return_date": "return date",
    "num_adults": "number of adults",
    "num_children": "number of children (ages 2-11)",
    "num_infants": "number of infants (under 2)",
    "num_rooms": "number of hotel rooms",
    "budget": "budget for the trip"
}

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "parameters" not in st.session_state:
        st.session_state.parameters = {k: None for k in REQUIRED_PARAMETERS}
    if "confirmed" not in st.session_state:
        st.session_state.confirmed = False
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

def get_chat_response(user_input):
    # Construct the conversation history
    conversation_history = "\n".join([
        f"{'Customer' if msg['role'] == 'user' else 'Agent'}: {msg['content']}"
        for msg in st.session_state.messages
    ])
    
    # Create the prompt for the LLM
    prompt = f"""You are Alex, a friendly travel agent. Your task is to collect travel details from customers in a natural conversation.

Current conversation history:
{conversation_history}

Customer's latest message: {user_input}

Instructions:
1. Maintain a friendly, conversational tone
2. Extract any travel details from the user's message
3. If any information is unclear or missing, ask for clarification
4. Focus on collecting missing information naturally
5. Once all details are collected, summarize and ask for confirmation

Respond in a conversational response. Include any assumptions made in the response. 

Missing parameters: {[k for k, v in st.session_state.parameters.items() if v is None]}"""

    messages = [ChatMessage(role="user", content=prompt)]
    response = llm(messages)
    
    # Split response into conversation part and JSON part
    parts = response.content.split('JSON_DATA:')
    conversation_response = parts[0].strip()
    
    # Extract JSON data
    try:
        json_str = parts[1].strip()
        extracted_params = json.loads(json_str)
    except (IndexError, json.JSONDecodeError):
        extracted_params = st.session_state.parameters.copy()
    
    return conversation_response, extracted_params

def update_parameters(new_params):
    for key, value in new_params.items():
        if value and key in st.session_state.parameters:
            st.session_state.parameters[key] = value

def all_parameters_filled():
    return all(st.session_state.parameters.values())

def handle_user_input():
    user_input = st.session_state.user_input
    if user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        response, new_params = get_chat_response(user_input)
        update_parameters(new_params)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.user_input = ""  # Clear the input field

def main():
    st.title("Travel Booking Assistant")
    
    initialize_session_state()
    
    if not st.session_state.initialized:
        welcome_message = ("Hi! I'm AI Agent, your travel booking assistant. I'm here to help you plan your trip. "
                          "Just tell me about your travel plans, and I'll guide you through the process. "
                          "Where would you like to go?")
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        st.session_state.initialized = True
    
    if st.session_state.confirmed:
        st.write("### Your Confirmed Travel Details")
        for key, value in st.session_state.parameters.items():
            st.write(f"**{REQUIRED_PARAMETERS[key]}**: {value}")
        if st.button("Plan Another Trip"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"You: {message['content']}")
            else:
                st.write(f"AI Agent: {message['content']}")
        
        st.text_area("Tell me about your travel plans:", key="user_input", height=100, on_change=handle_user_input)
        
        if all_parameters_filled():
            st.write("### Please review your travel details:")
            for key, value in st.session_state.parameters.items():
                st.write(f"**{REQUIRED_PARAMETERS[key]}**: {value}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Booking"):
                    st.session_state.confirmed = True
                    st.experimental_rerun()
            with col2:
                if st.button("Make Changes"):
                    change_message = ("I understand you'd like to make some changes. "
                                     "What would you like to modify in your booking?")
                    st.session_state.messages.append({"role": "assistant", "content": change_message})
                    st.experimental_rerun()

if __name__ == "__main__":
    main()