import streamlit as st
from groclake.modellake import ModelLake

# Initialize Groclake modules and load API key from Streamlit secrets
model_lake = ModelLake(api_key=st.secrets["API_KEY"])

# Customization settings
CHATBOT_NAME = "Traveler's Buddy"
CHATBOT_DESCRIPTION = "I am your virtual travel guide, here to assist you with exploring the world."
CHATBOT_INSTRUCTIONS = (
    "Provide helpful and accurate travel information, suggest popular destinations, recommend local cuisine, "
    "and share cultural or safety tips specific to different regions."
)
CONVERSATION_STARTERS = [
    "What are the best places to visit in Rajasthan?",
    "Can you suggest famous street food in Delhi?",
    "What should I pack for a trip to Ladakh?",
    "Are there any cultural festivals happening in India this month?",
    "What are the top beaches to visit in Goa?"
]

# Streamlit page configuration
st.set_page_config(page_title=CHATBOT_NAME, page_icon="🌍", layout="wide")

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "stored_conversations" not in st.session_state:
    st.session_state.stored_conversations = []
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

# Background image
background_image = "https://img.freepik.com/free-photo/flat-lay-hat-notebook-arrangement_23-2148786126.jpg"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({background_image});
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for previous chats
with st.sidebar:
    st.title("Previous Chats")
    
    # New Chat button
    if st.button("New Chat"):
        st.session_state.conversation_history = []
        st.session_state.current_conversation_id = None
        st.rerun()
    
    # Display stored conversations
    for idx, conversation in enumerate(st.session_state.stored_conversations):
        # Get the first user message as the title, or use default title
        title = next((msg["content"][:30] + "..." for msg in conversation if msg["role"] == "user"), f"Conversation {idx + 1}")
        if st.button(title, key=f"conv_{idx}"):
            st.session_state.conversation_history = conversation.copy()
            st.session_state.current_conversation_id = idx
            st.rerun()

# Main chat interface
st.title(CHATBOT_NAME)
st.write(f"**Description:** {CHATBOT_DESCRIPTION}")
# st.write(f"**Instructions:** {CHATBOT_INSTRUCTIONS}")

# Create columns for conversation starters
st.write("### Conversation Starters")
st.write(", ".join(CONVERSATION_STARTERS))

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style='
                    background-color: rgba(186, 216, 182, 0.7);  /* BAD8B6 with 70% opacity */
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    backdrop-filter: blur(5px);
                    -webkit-backdrop-filter: blur(5px);
                    border: 1px solid rgba(186, 216, 182, 0.3);
                '>
                    <div style='display: flex; align-items: center;'>
                        <div style='margin-right: 10px;'>👤</div>
                        <div style='color: rgba(0, 0, 0, 0.87);'>{message['content']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='
                    background-color: rgba(225, 234, 205, 0.7);  /* E1EACD with 70% opacity */
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    backdrop-filter: blur(5px);
                    -webkit-backdrop-filter: blur(5px);
                    border: 1px solid rgba(225, 234, 205, 0.3);
                '>
                    <div style='display: flex; align-items: center;'>
                        <div style='margin-right: 10px;'>🤖</div>
                        <div style='color: rgba(0, 0, 0, 0.87);'>{message['content']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Input container at the bottom
input_container = st.container()
with input_container:
    # Create a form to handle the input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your query (or 'exit' to end):", 
                                 placeholder="Ask me anything about traveling in India...")
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            if user_input.strip().lower() == "exit":
                if len(st.session_state.conversation_history) > 0:
                    # Only store if there are messages
                    if st.session_state.current_conversation_id is None:
                        st.session_state.stored_conversations.append(st.session_state.conversation_history.copy())
                    st.session_state.conversation_history = []
                    st.session_state.current_conversation_id = None
                st.rerun()
            else:
                # Add user message
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                
                # Get bot response
                try:
                    payload = {
                        "messages": st.session_state.conversation_history,
                        "token_size": 1024
                    }
                    response = model_lake.chat_complete(payload=payload)
                    bot_reply = response.get('answer', "Sorry, I couldn't process that.")
                    
                    # Add bot response
                    st.session_state.conversation_history.append({"role": "assistant", "content": bot_reply})
                    
                    # If this is a new conversation, store it
                    if st.session_state.current_conversation_id is None and len(st.session_state.conversation_history) == 2:
                        st.session_state.stored_conversations.append(st.session_state.conversation_history.copy())
                        st.session_state.current_conversation_id = len(st.session_state.stored_conversations) - 1
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                
                st.rerun()
