import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Groq LLM
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.3, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

# Initialize the search tool
search_tool = DuckDuckGoSearchRun()

# Define agents
sight_suggester = Agent(
    role='Sight Suggester',
    goal='Suggest interesting sights and attractions to visit based on the traveler\'s preferences',
    backstory='You are an experienced travel expert with knowledge of global attractions.',
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[search_tool]
)

transport_planner = Agent(
    role='Transport Planner',
    goal='Suggest suitable ways of transportation for the traveler',
    backstory='You are a transportation expert with knowledge of various modes of travel.',
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[search_tool]
)

accommodation_finder = Agent(
    role='Accommodation Finder',
    goal='Suggest appropriate places to stay based on the traveler\'s preferences and budget',
    backstory='You are an accommodation specialist with knowledge of various lodging options.',
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[search_tool]
)

legal_advisor = Agent(
    role='Legal Advisor',
    goal='Review and advise on legal limitations and requirements for the traveler',
    backstory='You are a legal expert specializing in international travel regulations.',
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[search_tool]
)

summary_writer = Agent(
    role='Summary Writer',
    goal='Generate a comprehensive summary of the travel plan',
    backstory='You are a skilled writer able to concisely summarize complex information.',
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Define tasks
def create_tasks(traveler_persona):
    return [
        Task(
            description=f"Suggest 5 interesting sights to visit for a traveler with the following persona: {traveler_persona}",
            agent=sight_suggester
        ),
        Task(
            description=f"Suggest suitable ways of transportation for a traveler with the following persona: {traveler_persona}",
            agent=transport_planner
        ),
        Task(
            description=f"Suggest where to sleep (hotels, AirBnbs, open air, etc) for a traveler with the following persona: {traveler_persona}",
            agent=accommodation_finder
        ),
        Task(
            description=f"Review legal limitations and requirements for the proposed travel plan for a traveler with the following persona: {traveler_persona}",
            agent=legal_advisor
        ),
        Task(
            description="Generate a summary of the conversation summarizing the travel plan",
            agent=summary_writer
        )
    ]

# Function to run the Travel Planner
def run_travel_planner(traveler_persona):
    tasks = create_tasks(traveler_persona)
    
    crew = Crew(
        agents=[sight_suggester, transport_planner, accommodation_finder, legal_advisor, summary_writer],
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    return result

# Streamlit UI
def main():
    st.title("AI Travel Planner")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Describe your travel persona/scenario"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = run_travel_planner(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
