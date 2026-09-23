import streamlit as st

def apply_theme():
    # Scoped Professional minimalistic enterprise UI theme
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            /* Global Font */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif !important;
            }
            
            /* Page Background */
            .stApp, .block-container {
                background-color: #F8F9FB;
                color: #111827;
            }
            
            /* Remove top padding and hide Streamlit top bar/footer */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
            }
            header[data-testid="stHeader"] {
                display: none !important;
            }
            footer {
                display: none !important;
            }
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {
                color: #111827 !important;
                font-family: 'Inter', sans-serif !important;
            }
            
            /* Sidebar styling */
            div[data-testid="stSidebar"] {
                background-color: #111827;
                color: #FFFFFF !important;
            }
            div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] span, div[data-testid="stSidebar"] a, div[data-testid="stSidebar"] label {
                color: #FFFFFF !important;
            }
            div[data-testid="stSidebarNav"] li div:hover {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
            div[data-testid="stSidebarNav"] li a[aria-current="page"] div {
                background-color: #2563EB !important;
                border-radius: 4px;
            }
            
            /* Buttons */
            .stButton > button {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 0.5rem 1rem !important;
                font-weight: 500 !important;
            }
            .stButton > button:hover {
                background-color: #1D4ED8 !important;
            }
            .stButton > button p {
                color: #FFFFFF !important;
            }
            
            /* Text Inputs (TextInput, TextArea, ChatInput) */
            [data-testid="stTextInput"] > div > div,
            [data-testid="stTextArea"] > div > div {
                background-color: #FFFFFF !important;
                border: 1px solid #E5E7EB !important;
                border-radius: 8px !important;
            }
            [data-testid="stChatInput"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E5E7EB !important;
                border-radius: 8px !important;
                outline: none !important;
            }
            [data-testid="stTextInput"] > div > div:hover,
            [data-testid="stTextInput"] > div > div:focus-within,
            [data-testid="stTextArea"] > div > div:hover,
            [data-testid="stTextArea"] > div > div:focus-within,
            [data-testid="stChatInput"]:hover,
            [data-testid="stChatInput"]:focus-within {
                border-color: #2563EB !important;
                outline: none !important;
                box-shadow: none !important;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stTextArea"] textarea,
            [data-testid="stChatInput"] textarea {
                color: #111827 !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #111827 !important;
            }
            [data-testid="stTextInput"] input::placeholder,
            [data-testid="stTextArea"] textarea::placeholder,
            [data-testid="stChatInput"] textarea::placeholder {
                color: #6B7280 !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #6B7280 !important;
            }
            
            /* Selectbox Specific Styling */
            /* Closed selectbox background */
            [data-baseweb="select"] > div {
                background-color: #FFFFFF !important;
                border-color: #E5E7EB !important;
                border-radius: 8px !important;
            }
            [data-baseweb="select"] > div:hover,
            [data-baseweb="select"] > div:focus-within {
                border-color: #2563EB !important;
                outline: none !important;
                box-shadow: none !important;
            }
            /* Closed selectbox text - strictly scoped to value container to avoid breaking icons */
            [data-baseweb="select"] [class*="ValueContainer"],
            [data-baseweb="select"] [class*="singleValue"],
            [data-baseweb="select"] [class*="ValueContainer"] span {
                color: #111827 !important;
                -webkit-text-fill-color: #111827 !important;
            }
            /* Placeholder text */
            [data-baseweb="select"] [class*="placeholder"] {
                color: #6B7280 !important;
                -webkit-text-fill-color: #6B7280 !important;
            }
            /* Dropdown menu background */
            [role="listbox"] {
                background-color: #FFFFFF !important;
                border-radius: 8px !important;
                border: 1px solid #E5E7EB !important;
            }
            /* Dropdown option text */
            [role="option"] {
                color: #111827 !important;
            }
            /* Hovered option background */
            [role="option"]:hover {
                background-color: #EFF6FF !important;
            }
            /* Selected option background */
            [role="option"][aria-selected="true"] {
                background-color: #DBEAFE !important;
                color: #111827 !important;
            }
            
            /* Alerts text color (Base rule for readability) */
            div[data-testid="stAlert"] {
                border-radius: 8px !important;
            }
            div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
                color: #111827 !important;
            }
            
            /* Alerts targeted by type (using SVG presence as a heuristic if supported) */
            div[data-testid="stAlert"]:has(svg) {
                border: none !important;
            }
            /* Info */
            div[data-testid="stAlert"]:has(div[class*="info"]) {
                background-color: #EFF6FF !important;
            }
            div[data-testid="stAlert"]:has(div[class*="info"]) div[data-testid="stMarkdownContainer"] p {
                color: #1E3A8A !important;
            }
            /* Warning */
            div[data-testid="stAlert"]:has(div[class*="warning"]) {
                background-color: #FFF7ED !important;
            }
            div[data-testid="stAlert"]:has(div[class*="warning"]) div[data-testid="stMarkdownContainer"] p {
                color: #9A3412 !important;
            }
            /* Error */
            div[data-testid="stAlert"]:has(div[class*="error"]) {
                background-color: #FEF2F2 !important;
            }
            div[data-testid="stAlert"]:has(div[class*="error"]) div[data-testid="stMarkdownContainer"] p {
                color: #991B1B !important;
            }
            /* Success */
            div[data-testid="stAlert"]:has(div[class*="success"]) {
                background-color: #F0FDF4 !important;
            }
            div[data-testid="stAlert"]:has(div[class*="success"]) div[data-testid="stMarkdownContainer"] p {
                color: #166534 !important;
            }
            
            /* Dataframes */
            div[data-testid="stDataFrame"] {
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            
            /* Default Text Color for Markdown outside of specific widgets */
            .stMarkdown p, .stMarkdown li {
                color: #111827;
            }
            
            /* Chat message */
            .stChatMessage {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 1rem;
                color: #111827 !important;
            }
            .stChatMessage div[data-testid="stMarkdownContainer"] p, 
            .stChatMessage div[data-testid="stMarkdownContainer"] li,
            .stChatMessage div[data-testid="stMarkdownContainer"] span,
            .stChatMessage div[data-testid="stMarkdownContainer"] strong,
            .stChatMessage div[data-testid="stMarkdownContainer"] em,
            .stChatMessage div[data-testid="stMarkdownContainer"] code {
                color: #111827 !important;
            }
            
        </style>
    """, unsafe_allow_html=True)
