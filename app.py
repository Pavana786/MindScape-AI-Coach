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
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except AttributeError:
    st.error("API Key not found. Please create a .env file with your GOOGLE_API_KEY.")
    st.stop()

# --- AI MODEL INITIALIZATION ---
## CORRECTED MODEL NAME ##
MODEL_NAME = 'gemini-2.5-flash' # Using the stable, working model
model = genai.GenerativeModel(MODEL_NAME)

# --- HELPER FUNCTION FOR PROMPT GENERATION (UPDATED) ---
def generate_prompt(current_role, desired_role, experience, skills, age, emotional_state):
    return f"""
    Act as an expert career strategist and a highly empathetic AI learning advisor for the tech industry in Bengaluru, India.

    A professional has the following profile:
    - Current Role: {current_role}
    - Desired Role: {desired_role}
    - Total Years of Experience: {experience} years
    - Existing Skills: {skills}
    - Age: {age}
    - Current Emotional State: "{emotional_state}"

    Your task is to generate a detailed, actionable 3-month reskilling roadmap.
    **Crucially, you must tailor the tone and recommendations based on the user's emotional state.** For example, if they are feeling "anxious" or "burnt out," the plan should start with smaller, more manageable goals and include advice for managing stress. If they are "excited," the plan can be more aggressive.

    The output must be in Markdown and include these sections:

    ### 1. Empathetic Opening & Skill Gap Analysis
    Start with a supportive opening that acknowledges their emotional state before analyzing the skill gap.

    ### 2. Personalized 3-Month Week-by-Week Roadmap
    - **Month 1: Foundational Skills & Confidence Building:** Focus on core concepts and quick wins.
    - **Month 2: Advanced Topics & Specialization:** Deeper knowledge.
    - **Month 3: Portfolio Project & Interview Prep:** A capstone project and job application prep.
    The pacing must be adjusted based on their emotional state.

    ### 3. Recommended Learning Resources
    Provide 3-5 specific, high-quality online courses, books, or tutorials.

    ### 4. Portfolio Project Idea
    Suggest a concrete project idea impressive to recruiters in Bengaluru.

    ### 5. Resume & LinkedIn Keywords
    List 5-7 essential keywords for their resume and LinkedIn profile.
    """

# --- STREAMLIT USER INTERFACE (UPDATED) ---

st.title("MindScape 🧠")
st.subheader("Your AI-Powered Career Transition Co-Pilot")

tab1, tab2 = st.tabs(["🚀 Career Roadmap Generator", "💬 AI Motivation Coach"])

with tab1:
    st.markdown(
        "**Get a structured, week-by-week plan to move from your current role to your desired role.**"
    )
    st.markdown("---")

    # Use columns for a cleaner layout
    col1, col2 = st.columns(2)

    with col1:
        current_role = st.text_input("Your Current Job Title", placeholder="e.g., Graphic Designer")
        desired_role = st.text_input("Your Desired Job Title", placeholder="e.g., Frontend Developer")
        age = st.number_input("Your Age", min_value=18, max_value=70, step=1, value=25)

    with col2:
        experience = st.number_input("Your Years of Experience", min_value=0, max_value=50, step=1)
        emotional_state = st.selectbox(
            "How are you feeling about this career transition?",
            ("Excited and Eager", "Hopeful but a little nervous", "Feeling Anxious", "Feeling Burnt Out", "Just Curious")
        )
        skills = st.text_area("Your Current Skills (comma-separated)", placeholder="e.g., Figma, basic HTML")

    if st.button("✨ Generate My Personalized Roadmap", use_container_width=True):
        if not all([current_role, desired_role, skills]):
            st.warning("Please fill in all the required fields before generating the roadmap.")
        else:
            with st.spinner("Crafting your personalized future... Please wait."):
                try:
                    prompt = generate_prompt(current_role, desired_role, experience, skills, age, emotional_state)
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

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = genai.GenerativeModel(
            ## CORRECTED MODEL NAME ##
            MODEL_NAME, # Use the stable model for chat too
            system_instruction=SYSTEM_INSTRUCTION
        ).start_chat()
        st.session_state.messages = [{"role": "model", "content": "Hello! I'm your MindScape Coach. How can I support your career journey today?"}]

    for msg in st.session_state.messages:
        chat_message(msg["role"]).write(msg["content"])

    if prompt := chat_input("Ask your coach a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_message("user").write(prompt)

        with st.spinner("Coach is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                ai_response = response.text
                st.session_state.messages.append({"role": "model", "content": ai_response})
                chat_message("model").write(ai_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("The coach lost connection. Please try again.")