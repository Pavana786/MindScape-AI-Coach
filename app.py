# app.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from streamlit import chat_message, chat_input # Import for the chat feature

# Load environment variables from .env file
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MindScape",
    page_icon="🧠",
    layout="wide"
)

# --- API CONFIGURATION ---
try:
    # Uses the most stable and robust model name for fast, general tasks
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except AttributeError:
    st.error("API Key not found. Please create a .env file with your GOOGLE_API_KEY.")
    st.stop()

# --- AI MODEL INITIALIZATION ---
# Base model for the detailed roadmap generation
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- HELPER FUNCTION FOR PROMPT GENERATION ---
def generate_prompt(current_role, desired_role, experience, skills):
    return f"""
    Act as an expert career strategist and AI learning advisor for the tech industry in Bengaluru, India.
    Today's date is October 8, 2025.

    A professional with the following profile is seeking a personalized reskilling roadmap:
    - Current Role: {current_role}
    - Desired Role: {desired_role}
    - Total Years of Experience: {experience} years
    - Existing Skills: {skills}

    Based on the current job market trends and skill demands in Bengaluru, generate a detailed, actionable 3-month reskilling roadmap. The plan must be structured, practical, and motivating.

    The output should be in Markdown format and must include the following sections:

    ### 1. Skill Gap Analysis
    ### 2. 3-Month Week-by-Week Roadmap
    ### 3. Recommended Learning Resources
    ### 4. Portfolio Project Idea
    ### 5. Resume & LinkedIn Keywords
    """

# --- STREAMLIT USER INTERFACE (WITH TABS) ---

st.title("MindScape 🧠")
st.subheader("Your AI-Powered Career Transition Co-Pilot")

# Create two tabs for the two main features
tab1, tab2 = st.tabs(["🚀 Career Roadmap Generator", "💬 AI Motivation Coach"])

with tab1:
    st.markdown(
        "**Get a structured, week-by-week plan to move from your current role to your desired role.**"
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        current_role = st.text_input(
            "Your Current Job Title", placeholder="e.g., Graphic Designer"
        )
        desired_role = st.text_input(
            "Your Desired Job Title", placeholder="e.g., Frontend Developer"
        )
    with col2:
        experience = st.number_input(
            "Your Years of Experience", min_value=0, max_value=30, step=1
        )
        skills = st.text_area(
            "Your Current Skills (comma-separated)",
            placeholder="e.g., Figma, basic HTML, basic CSS",
        )

    if st.button("✨ Generate My Personalized Roadmap", use_container_width=True):
        if not all([current_role, desired_role, skills]):
            st.warning("Please fill in all the fields before generating the roadmap.")
        else:
            with st.spinner("Crafting your future... Please wait a moment."):
                try:
                    prompt = generate_prompt(current_role, desired_role, experience, skills)
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.header("✨ Your Custom Reskilling Roadmap ✨")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.info("Please try checking your network connection or try rephrasing.")


with tab2:
    st.markdown(
        "**Talk to your personal AI Coach for motivation, interview practice, or career Q&A.**"
    )

    # --- AI COACH SETUP (Conversational Assistant) ---
    
    SYSTEM_INSTRUCTION = (
        "You are 'MindScape Coach,' an empathetic and highly knowledgeable AI career counselor based in Bengaluru. "
        "Your goal is to provide supportive, concise, and actionable advice for professionals during career transitions. "
        "Handle questions about job search strategy, interview preparation, skill gaps, and motivation. "
        "Keep your tone encouraging and professional. Do not give medical or financial advice."
    )

    # Initialize chat session with the personality
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = genai.GenerativeModel(
            MODEL_NAME, # Use the stable model for chat too
            system_instruction=SYSTEM_INSTRUCTION
        ).start_chat()
        
        st.session_state.messages = [{"role": "model", "content": "Hello! I'm your MindScape Coach. Tell me, how can I support you in your career journey today?"}]
    
    # Display previous messages
    for msg in st.session_state.messages:
        chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if prompt := chat_input("Ask your coach a question..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_message("user").write(prompt)

        # Send to AI
        with st.spinner("Coach is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                
                # Add AI response to history
                ai_response = response.text
                st.session_state.messages.append({"role": "model", "content": ai_response})
                chat_message("model").write(ai_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("The coach lost connection. Please try restarting the app or try rephrasing.")