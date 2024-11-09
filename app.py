import streamlit as st
from s import create_teacher
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'teacher' not in st.session_state:
        # Initialize teacher with API key from secrets
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.session_state.teacher = create_teacher(api_key)

def main():
    st.set_page_config(
        page_title="AI Socratic Teacher",
        page_icon="🎓",
        layout="centered"
    )

    # Initialize session state
    initialize_session_state()

    # Header
    st.header("🎓 AI Socratic Teacher", divider="rainbow")
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        ## About
        Welcome to the AI Socratic Teacher! This application uses the Socratic method 
        to guide you through learning any topic through thoughtful questions and dialogue.
        
        ### How it works:
        1. Enter your topic or question
        2. Engage in a dialogue with the AI teacher
        3. Learn through guided discovery
        
        ### Tips:
        - Be specific about what you want to learn
        - Take time to think about each question
        - Explain your reasoning in your answers
        """)
        
        # Clear conversation button
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.teacher.clear_memory()
            st.rerun()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to learn about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            # Get AI response
            with st.spinner("Thinking..."):
                response = st.session_state.teacher.get_response(prompt)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # Rerun to update the chat display
        st.rerun()

if __name__ == "__main__":
    main()
