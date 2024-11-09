import streamlit as st
from s import create_teacher
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'teacher' not in st.session_state:
        try:
            # Try to get API key from secrets
            api_key = st.secrets.get("GOOGLE_API_KEY")
            if not api_key:
                st.error("🔑 Google API Key not found in secrets. Please configure it in Streamlit Cloud.")
                st.stop()
            st.session_state.teacher = create_teacher(api_key)
            # Add welcome message
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hello! I'm your Socratic Teacher. I'll help you learn through thoughtful questions and discussion. What topic would you like to explore today?"
            })
        except Exception as e:
            st.error(f"❌ Error initializing teacher: {str(e)}")
            st.stop()

def display_chat_message(message, is_user=False):
    """Display a chat message with typing animation for assistant"""
    with st.chat_message("user" if is_user else "assistant"):
        if is_user:
            st.write(message)
        else:
            # Simulate typing for assistant messages
            message_placeholder = st.empty()
            full_response = message
            for i in range(len(full_response) + 1):
                message_placeholder.markdown(full_response[:i] + "▌")
                time.sleep(0.01)
            message_placeholder.markdown(full_response)

def main():
    st.set_page_config(
        page_title="AI Socratic Teacher",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    try:
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
            - Ask for clarification if needed
            """)
            
            # Clear conversation button
            if st.button("Clear Conversation", type="secondary"):
                st.session_state.messages = []
                if hasattr(st.session_state, 'teacher'):
                    st.session_state.teacher.clear_memory()
                st.rerun()

        # Display chat messages
        for message in st.session_state.messages:
            display_chat_message(
                message["content"], 
                is_user=(message["role"] == "user")
            )

        # Chat input
        if prompt := st.chat_input(
            "What would you like to learn about?",
            disabled=not hasattr(st.session_state, 'teacher')
        ):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message(prompt, is_user=True)
            
            try:
                # Get AI response
                with st.spinner("Thinking..."):
                    response = st.session_state.teacher.get_response(prompt)
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_chat_message(response)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please refresh the page and try again.")

if __name__ == "__main__":
    main()
