"""
📚 Book Recommendation Engine - Streamlit UI
Beautiful, ChatGPT-like interface for personalized book recommendations
"""

import streamlit as st
import uuid
import time
import traceback
import streamlit.components.v1 as components

# Import agent utilities
try:
    from agent import create_agent, chat as agent_chat
except Exception as imp_err:
    create_agent = None
    agent_chat = None
    IMPORT_ERROR = imp_err
else:
    IMPORT_ERROR = None

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="📚 Book Recommendation Engine",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown(
    """
    <style>
    /* Main container */
    .app-container {
        max-width: 1200px;
        margin: 10px auto;
        padding: 0 20px;
    }
    
    /* Header styling */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding: 20px 0;
    }
    
    .title {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        color: #7b8794;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* Chatbox with fixed height and scroll */
    #chatbox {
        border-radius: 16px;
        padding: 24px;
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.03));
        box-shadow: 0 10px 40px rgba(2,6,23,0.08);
        max-height: 65vh;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Scrollbar styling */
    #chatbox::-webkit-scrollbar {
        width: 8px;
    }
    
    #chatbox::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.1);
        border-radius: 10px;
    }
    
    #chatbox::-webkit-scrollbar-thumb {
        background: rgba(102,126,234,0.5);
        border-radius: 10px;
    }
    
    #chatbox::-webkit-scrollbar-thumb:hover {
        background: rgba(102,126,234,0.7);
    }
    
    /* Message bubbles */
    .msg-user {
        margin-left: auto;
        margin-bottom: 16px;
        padding: 14px 18px;
        border-radius: 18px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        word-wrap: break-word;
        line-height: 1.6;
    }
    
    .msg-assistant {
        margin-right: auto;
        margin-bottom: 16px;
        padding: 14px 18px;
        border-radius: 18px;
        background: linear-gradient(180deg, #1a1f2e, #252b3b);
        color: #e6eef8;
        max-width: 85%;
        box-shadow: 0 4px 16px rgba(2,6,23,0.15);
        word-wrap: break-word;
        line-height: 1.6;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .meta {
        font-size: 11px;
        color: rgba(255,255,255,0.5);
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Quick start guide */
    .quick-start {
        background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(102,126,234,0.2);
    }
    
    .quick-start h3 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 18px;
    }
    
    .quick-start ul {
        margin-left: 20px;
        color: #7b8794;
    }
    
    .quick-start li {
        margin-bottom: 8px;
        line-height: 1.5;
    }
    
    /* Input area styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid rgba(102,126,234,0.3);
        background: rgba(255,255,255,0.02);
        color: #e6eef8;
        font-size: 15px;
        padding: 12px;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.4);
    }
    
    /* Status indicators */
    .status-success {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-info {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Small muted text */
    .small-muted {
        color: #98a0a6;
        font-size: 12px;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #7b8794;
    }
    
    .empty-state h2 {
        color: #667eea;
        margin-bottom: 10px;
    }
    
    /* Responsive design */
    @media (max-width: 800px) {
        #chatbox {
            max-height: 55vh;
            padding: 16px;
        }
        .msg-user, .msg-assistant {
            max-width: 90%;
        }
        .title {
            font-size: 24px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# CACHED AGENT INITIALIZER
# =============================================================================

@st.cache_resource(show_spinner=False)
def get_agent_executor_cached():
    """Initialize and cache the agent executor."""
    if create_agent is None:
        raise RuntimeError(f"agent.create_agent import failed: {IMPORT_ERROR}")
    return create_agent()

def ensure_agent_ready():
    """Ensure agent is initialized and ready."""
    if st.session_state.get("agent_ready") and st.session_state.get("agent_executor"):
        return st.session_state["agent_executor"]
    agent_exec = get_agent_executor_cached()
    st.session_state["agent_executor"] = agent_exec
    st.session_state["agent_ready"] = True
    return agent_exec

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

if "last_error" not in st.session_state:
    st.session_state.last_error = None

if "show_quick_start" not in st.session_state:
    st.session_state.show_quick_start = True

# =============================================================================
# HEADER
# =============================================================================

st.markdown('<div class="app-container">', unsafe_allow_html=True)

col_left, col_right = st.columns([5, 1])
with col_left:
    st.markdown(
        '''
        <div class="header">
            <div>
                <div class="title">📚 Book Recommendation Engine</div>
                <div class="subtitle">Personalized book suggestions powered by AI • Get recommendations based on your taste</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

with col_right:
    st.markdown(
        f"<div class='small-muted' style='text-align: right; padding-top: 10px;'>Session: {st.session_state.session_id.split('-')[0]}</div>",
        unsafe_allow_html=True
    )

st.divider()

# =============================================================================
# STATUS SECTION
# =============================================================================

status_col1, status_col2, status_col3 = st.columns([2, 2, 2])

with status_col1:
    if st.session_state.agent_ready:
        st.markdown('<div class="status-success">✓ Agent Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-info">⟳ Initializing...</div>', unsafe_allow_html=True)

with status_col2:
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with status_col3:
    if st.button("💡 Toggle Guide"):
        st.session_state.show_quick_start = not st.session_state.show_quick_start
        st.rerun()

# =============================================================================
# QUICK START GUIDE
# =============================================================================

if st.session_state.show_quick_start and len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="quick-start">
            <h3>📖 How to Get Started</h3>
            <p style="color: #7b8794; margin-bottom: 10px;">Tell me about your reading preferences to get personalized recommendations!</p>
            <ul>
                <li><strong>Favorite Genre:</strong> Sci-fi, mystery, romance, fantasy, thriller, etc.</li>
                <li><strong>Recent Reads:</strong> Share 2-3 books you recently enjoyed</li>
                <li><strong>Mood/Theme:</strong> Light read, deep thinking, fast-paced, emotional, etc.</li>
                <li><strong>Reading Goal:</strong> Entertainment, learning, inspiration, etc.</li>
            </ul>
            <p style="color: #667eea; margin-top: 12px; font-weight: 600;">
                Example: "I love sci-fi and recently read Project Hail Mary and The Martian. Recommend 5 fast-paced space adventure books."
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# AGENT INITIALIZATION
# =============================================================================

chatbox_placeholder = st.empty()

if not st.session_state.agent_ready:
    try:
        with st.spinner("🚀 Initializing book recommendation agent... This may take a moment."):
            ensure_agent_ready()
            st.session_state.agent_ready = True
    except Exception:
        st.session_state.last_error = traceback.format_exc()
        st.error("❌ Agent initialization failed. Please check your API keys in the .env file.")
        
        with st.expander("🔍 View Error Details"):
            st.code(st.session_state.last_error)
        
        chat_html = "<div id='chatbox'><div class='empty-state'><h2>⚠️ Initialization Failed</h2><p>Please check your API keys and try refreshing the page.</p></div></div>"
        chatbox_placeholder.markdown(chat_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# =============================================================================
# CHAT RENDERING FUNCTION
# =============================================================================

def render_chat_html(messages):
    """Render chat messages as HTML."""
    if not messages:
        html_parts = [
            "<div id='chatbox'>",
            "<div class='empty-state'>",
            "<h2>📚 Ready to Discover Your Next Great Read?</h2>",
            "<p>Share your reading preferences below and I'll recommend 5 perfect books for you!</p>",
            "</div>",
            "</div>"
        ]
        return "\n".join(html_parts)
    
    html_parts = ["<div id='chatbox'>"]
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        ts = msg.get("ts", time.time())
        ts_str = time.strftime("%H:%M", time.localtime(ts))
        
        # Convert newlines to <br> for HTML rendering
        safe_content = content.replace("\n", "<br>")
        safe_content = safe_content.replace("**", "<strong>").replace("**", "</strong>")
        
        if role == "user":
            html_parts.append(
                f"<div style='display:flex; justify-content:flex-end;'>"
                f"<div class='msg-user'>{safe_content}"
                f"<div class='meta'>You • {ts_str}</div>"
                f"</div></div>"
            )
        else:
            html_parts.append(
                f"<div style='display:flex; justify-content:flex-start;'>"
                f"<div class='msg-assistant'>{safe_content}"
                f"<div class='meta'>Book Agent • {ts_str}</div>"
                f"</div></div>"
            )
    
    html_parts.append("</div>")
    return "\n".join(html_parts)

# Render initial chat
chatbox_placeholder.markdown(render_chat_html(st.session_state.messages), unsafe_allow_html=True)

# =============================================================================
# INPUT FORM
# =============================================================================

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Tell me about your reading preferences:",
        key="user_input",
        height=120,
        placeholder="Example: I love mystery novels. I recently read 'The Silent Patient' and 'Gone Girl'. I want something dark and suspenseful with plot twists...",
        help="Share your favorite genres, recent reads, mood, and what you're looking for"
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        submit = st.form_submit_button("🔍 Get Recommendations", use_container_width=True)

# =============================================================================
# PROCESS USER INPUT
# =============================================================================

if submit and user_input and user_input.strip():
    text = user_input.strip()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": text, "ts": time.time()})
    chatbox_placeholder.markdown(render_chat_html(st.session_state.messages), unsafe_allow_html=True)
    
    # Add thinking placeholder
    st.session_state.messages.append({"role": "assistant", "content": "🔍 Searching for perfect book recommendations...", "ts": time.time()})
    chatbox_placeholder.markdown(render_chat_html(st.session_state.messages), unsafe_allow_html=True)
    
    # Get agent response
    try:
        agent_exec = st.session_state.get("agent_executor") or ensure_agent_ready()
        start = time.time()
        
        try:
            response = agent_chat(text, agent_exec)
            if response is None:
                response = "I couldn't generate recommendations. Please try rephrasing your preferences."
            elif not isinstance(response, str):
                try:
                    response = str(response)
                except Exception:
                    response = "I received an unexpected response format. Please try again."
        except Exception as e:
            response = f"I encountered an error: {str(e)}. Please try again with different preferences."
        
        # Update last assistant message
        for i in range(len(st.session_state.messages) - 1, -1, -1):
            if st.session_state.messages[i]["role"] == "assistant":
                st.session_state.messages[i]["content"] = response
                st.session_state.messages[i]["ts"] = time.time()
                break
        
        # Re-render chat
        chatbox_placeholder.markdown(render_chat_html(st.session_state.messages), unsafe_allow_html=True)
        
        elapsed = time.time() - start
        st.markdown(
            f"<div style='text-align: right; color: #98a0a6; font-size: 12px; margin-top: 8px;'>"
            f"⚡ Response time: {elapsed:.2f}s</div>",
            unsafe_allow_html=True
        )
        
    except Exception:
        tb = traceback.format_exc()
        st.session_state.last_error = tb
        
        # Update with error message
        for i in range(len(st.session_state.messages) - 1, -1, -1):
            if st.session_state.messages[i]["role"] == "assistant":
                st.session_state.messages[i]["content"] = "⚠️ Failed to get recommendations. Please check the error log below."
                st.session_state.messages[i]["ts"] = time.time()
                break
        
        chatbox_placeholder.markdown(render_chat_html(st.session_state.messages), unsafe_allow_html=True)
        
        with st.expander("🔍 View Error Details"):
            st.code(tb)
    
    # Auto-scroll to bottom
    components.html(
        """
        <script>
        const cb = document.getElementById('chatbox');
        if (cb) { cb.scrollTop = cb.scrollHeight; }
        </script>
        """,
        height=0,
    )

# Auto-scroll on page load
components.html(
    """
    <script>
    const cb = document.getElementById('chatbox');
    if (cb) { cb.scrollTop = cb.scrollHeight; }
    </script>
    """,
    height=0,
)

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown(
    """
    <div style='color: #98a0a6; margin-top: 20px; padding: 20px; font-size: 12px; text-align: center; border-top: 1px solid rgba(255,255,255,0.1);'>
        <p>📚 Powered by LangChain + Groq + Tavily • Built with Streamlit</p>
        <p style='margin-top: 8px;'>Store your API keys in a .env file: GROQ_API_KEY and TAVILY_API_KEY</p>
    </div>
    """,
    unsafe_allow_html=True
)