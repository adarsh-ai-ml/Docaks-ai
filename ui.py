import requests
import streamlit as st
import os
import base64
from urllib.parse import quote
from ingestion import create_or_update_vectorstore
from config import PDF_DIR

# PAGE CONFIGURATION

st.set_page_config(
    page_title="DOCaks AI Assistant",
    page_icon="❋",
    layout="wide"
)



# CUSTOM DESIGN


st.markdown("""
<style>

/* MAIN APPLICATION */
.stApp {
    background: #0b0f19 !important;
    color: #e5e7eb;
}

/* MAIN CONTENT */
.main .block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263247;
}

[data-testid="stSidebar"] h1 {
    color: #a78bfa;
}

[data-testid="stSidebar"] p {
    color: #aab4c5;
}

/* HEADINGS */
h1, h2, h3 {
    color: #f3f4f6 !important;
    font-weight: 700 !important;
}

/* NORMAL TEXT */
.stMarkdown p {
    color: #cbd5e1;
}

/* DOCaks PREMIUM GLOWING TAGLINE */
.DOCaks-tagline {
    color: #C4B5FD !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase;
    text-shadow:
        0 0 5px rgba(167, 139, 250, 0.8),
        0 0 12px rgba(139, 92, 246, 0.7),
        0 0 25px rgba(139, 92, 246, 0.45);
}

/* PDF KNOWLEDGE POPOVER */
[data-testid="stPopover"] > button {
    background: linear-gradient(135deg, #171c35, #202044) !important;
    color: #C4B5FD !important;
    border: 1px solid #8B5CF6 !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 750 !important;
    letter-spacing: 1px !important;
}

/* PDF KNOWLEDGE BUTTON */
[data-testid="stPopover"] button {
    background: linear-gradient(135deg, #171c35, #30245c) !important;
    color: #C4B5FD !important;
    border: 1px solid #8B5CF6 !important;
    border-radius: 10px !important;
    font-weight: 750 !important;
    letter-spacing: 1.2px !important;
    box-shadow: 0 0 14px rgba(139, 92, 246, 0.25) !important;
}

[data-testid="stPopover"] button:hover {
    background: #6D28D9 !important;
    color: white !important;
}

/* DOCaks PREMIUM CHAT INPUT */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 8px 0 !important;
}

[data-testid="stChatInput"] > div {
    background: linear-gradient(135deg, #151d2e, #202044) !important;
    border: 1.5px solid #8B5CF6 !important;
    border-radius: 18px !important;
    padding: 5px 10px !important;
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.16) !important;
    transition: all 0.25s ease !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border: 1.5px solid #C4B5FD !important;
    box-shadow: 0 0 18px rgba(139, 92, 246, 0.25) !important;
    outline: none !important;
}

[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #AAB4C5 !important;
}

/* PURPLE SEND BUTTON */
[data-testid="stChatInputSubmitButton"] {
    background: #8B5CF6 !important;
    color: #FFFFFF !important;
    border-color: #A78BFA !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: #6D28D9 !important;
}

/* AI RESPONSE TEXT */
[data-testid="stChatMessage"] p {
    color: #E2E8F0;
    font-size: 15px;
    line-height: 1.75;
}

[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #FFFFFF;
    font-weight: 700;
    letter-spacing: 0.3px;
}

[data-testid="stChatMessage"] strong {
    color: #C4B5FD;
    font-weight: 700;
}

[data-testid="stChatMessage"] a {
    color: #A78BFA;
}



/* PREMIUM DOCaks BUTTONS */

.stButton > button {
    background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 55%, #4F46E5 100%);
    color: #FFFFFF !important;
    border: 1px solid rgba(196, 181, 253, 0.35) !important;
    border-radius: 12px;
    padding: 0.65rem 1.4rem;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 14px rgba(109, 40, 217, 0.25);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #A78BFA 0%, #7C3AED 55%, #6366F1 100%);
    color: #FFFFFF !important;
    border: 1px solid #C4B5FD !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
}

.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(109, 40, 217, 0.2);
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: #151d2e;
    border: 1px dashed #596987;
    border-radius: 12px;
    padding: 12px;
}

/* EXPANDERS */
[data-testid="stExpander"] {
    background: #151d2e;
    border: 1px solid #263247;
    border-radius: 10px;
}

/* DIVIDERS */
hr {
    border-color: #263247;
}

/* TOP HEADER */
[data-testid="stHeader"] {
    background: transparent;
}

/* CHAT MESSAGE TEXT */
[data-testid="stChatMessage"] p {
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.7;
}

/* CHAT AVATAR */
[data-testid="stChatMessageAvatar"] {
    background: #293653;
    border-radius: 50%;
}

/* SOURCE EXPANDER */
[data-testid="stExpander"] summary {
    color: #c4b5fd;
    font-weight: 600;
}

/* CHAT INPUT TEXT */
[data-testid="stChatInput"] textarea {
    color: #ffffff;
    caret-color: #a78bfa;
}

/* DOCaks FULL MAIN BACKGROUND IMAGE */

.stApp {
    background-image:
        linear-gradient(
            rgba(5, 8, 18, 0.35),
            rgba(5, 8, 18, 0.35)
        ),
        url("assets/docaks_background.png") !important;

    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

</style>
""", unsafe_allow_html=True)

# DOCaks FULL BACKGROUND IMAGE

with open("assets/docaks_background.png", "rb") as image_file:
    background_image = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(
                rgba(5, 8, 18, 0.35),
                rgba(5, 8, 18, 0.35)
            ),
            url("data:image/png;base64,{background_image}") !important;

        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# SESSION STATE

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

def format_source(source):

    if isinstance(source, dict):

        file_name = source.get("file", "Unknown")
        page = source.get("page")

        if page is not None:
            return f"{file_name} (Page {page})"

        return file_name

    return str(source)

# SIDEBAR

with st.sidebar:

  
    st.html("""
<div style="
    position: relative;
    overflow: hidden;
    padding: 20px 12px 16px;
    margin-bottom: 16px;
    border-radius: 23px;
    border: 1px solid rgba(167,139,250,0.65);
    background: linear-gradient(135deg,#171044 0%,#090D22 55%,#25105B 100%);
    box-shadow: 0 0 22px rgba(124,58,237,0.28),
                inset 0 0 25px rgba(139,92,246,0.12);
">
    <div style="
        display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
text-align:center;
gap:10px;
        position:relative;
        z-index:2;
    ">
        <div style="width:76px; min-width:76px;">
            <svg viewBox="0 0 100 100" width="76" height="76">
                <defs>
                    <linearGradient id="docaksOrb" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#E9B5FF"/>
                        <stop offset="50%" stop-color="#9333EA"/>
                        <stop offset="100%" stop-color="#5B21B6"/>
                    </linearGradient>
                </defs>
                <ellipse cx="50" cy="50" rx="43" ry="17"
                    transform="rotate(-32 50 50)"
                    fill="none" stroke="#A855F7" stroke-width="4"/>
                <path d="M48 8 C75 12 91 37 77 65 C67 84 42 96 23 79 C42 79 57 62 57 43 C57 28 51 17 48 8Z"
                    fill="url(#docaksOrb)"/>
                <path d="M35 30 C16 38 12 63 29 78 C38 85 49 85 58 79 C39 78 31 61 35 30Z"
                    fill="#A78BFA"/>
                <path d="M50 35 L55 45 L65 50 L55 55 L50 65 L45 55 L35 50 L45 45Z"
                    fill="#FFFFFF"/>
            </svg>
        </div>

        <div style="text-align:center;">
            <div style="
                color:#FFFFFF;
                font-size:27px;
                font-weight:850;
                letter-spacing:0.5px;
                white-space:nowrap;
            ">DOCaks <span style="color:#B65CFF;">AI</span></div>

            <div style="
                color:#D8C8FF;
                font-size:9px;
                font-weight:700;
                letter-spacing:2px;
                margin-top:5px;
                white-space:nowrap;
            ">DOCUMENT INTELLIGENCE</div>
        </div>
    </div>

    <div style="
        height:2px;
        margin-top:17px;
        background:linear-gradient(90deg,transparent,#A855F7,#E9B5FF,#7C3AED,transparent);
        box-shadow:0 0 10px #9333EA;
    "></div>

    <div style="
        text-align:center;
        color:#D8B4FE;
        font-size:11px;
        font-weight:700;
        letter-spacing:3px;
        margin-top:13px;
    ">✦ &nbsp; ASK&nbsp; · &nbsp; DISCOVER&nbsp; · &nbsp; ACHIEVE &nbsp; ✦</div>
</div>
""")


    st.divider()

        # SIDEBAR NAVIGATION

    st.markdown("""
    <div style="
        color: #C4B5FD;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 15px 0 12px 5px;
    ">
        NAVIGATION
    </div>
    """, unsafe_allow_html=True)

    if st.button("⌂   Home", key="nav_home", use_container_width=True):
        st.session_state.active_page = "Home"

    if st.button("▣   Document Library", key="nav_library", use_container_width=True):
        st.session_state.active_page = "Document Library"

    if st.button("⚙   System Info", key="nav_system", use_container_width=True):
        st.session_state.active_page = "System Info"

    if st.button("ⓘ   About", key="nav_about", use_container_width=True):
        st.session_state.active_page = "About"

    st.divider()

    st.markdown("### ⚙️ System Architecture")

    st.markdown("""
<div style="
    background: #192235;
    border: 1px solid #303b59;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
">
    <div style="color:#94a3b8;font-size:11px;">LANGUAGE MODEL</div>
    <div style="color:#c4b5fd;font-size:15px;font-weight:700;">Qwen 2.5</div>
</div>

<div style="
    background: #192235;
    border: 1px solid #303b59;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
">
    <div style="color:#94a3b8;font-size:11px;">VECTOR DATABASE</div>
    <div style="color:#c4b5fd;font-size:15px;font-weight:700;">ChromaDB</div>
</div>

<div style="
    background: #192235;
    border: 1px solid #303b59;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
">
    <div style="color:#94a3b8;font-size:11px;">EMBEDDINGS</div>
    <div style="color:#c4b5fd;font-size:15px;font-weight:700;">MiniLM</div>
</div>

<div style="
    background: #192235;
    border: 1px solid #303b59;
    border-radius: 12px;
    padding: 14px;
">
    <div style="color:#94a3b8;font-size:11px;">RETRIEVAL</div>
    <div style="color:#c4b5fd;font-size:15px;font-weight:700;">Semantic Search</div>
</div>
""", unsafe_allow_html=True)


    st.divider()


    st.markdown("""
<div style="
    color: #e2e8f0;
    font-size: 18px;
    font-weight: 700;
    margin: 20px 0 12px 0;
">
    📄 Document Center
</div>
""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("⬆️ Upload & Index Documents", use_container_width=True):

        if not uploaded_files:
            st.warning("Please select PDF files.")

        else:
            files_to_upload = [
                (
                    "files",
                    (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                )
                for uploaded_file in uploaded_files
            ]

            try:
                with st.spinner("Uploading and indexing PDFs..."):

                    response = requests.post(
                        "http://127.0.0.1:8000/upload",
                        files=files_to_upload,
                        timeout=300
                    )

                    response.raise_for_status()
                    data = response.json()

                st.success(data["message"])

                for filename in data["uploaded_files"]:
                    st.write(f"📄 {filename}")

            except requests.exceptions.RequestException as error:
                st.error(f"PDF upload failed: {error}")

            except Exception as error:
                st.error(f"Something went wrong: {error}")

           

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# PAGE NAVIGATION

active_page = st.session_state.active_page


# DOCUMENT LIBRARY PAGE

if active_page == "Document Library":

    st.title("📚 Document Library")

    st.caption("Manage and access your uploaded PDF documents.")

    pdf_files = []

    if PDF_DIR.exists():
        pdf_files = sorted([
            file for file in os.listdir(PDF_DIR)
            if file.lower().endswith(".pdf")
        ])

    st.metric("Total Documents", len(pdf_files))

    search_query = st.text_input(
        "Search Documents",
        placeholder="Enter PDF filename..."
    )

    filtered_files = [
        file for file in pdf_files
        if search_query.lower() in file.lower()
    ]

    if filtered_files:

        for index, pdf_file in enumerate(filtered_files):

            with st.container(border=True):

                col1, col2, col3 = st.columns([4, 1, 1])

                with col1:
                    st.markdown(f"📄 **{pdf_file}**")

                with col2:

                    file_path = PDF_DIR / pdf_file

                    with open(file_path, "rb") as pdf:
                        st.download_button(
                            "Download",
                            data=pdf.read(),
                            file_name=pdf_file,
                            mime="application/pdf",
                            key=f"download_{index}"
                        )

                    with col3:

                     if st.button(
                        "Delete",
                        key=f"delete_{index}",
                        type="secondary"
                    ):

                        try:
                            response = requests.delete(
                                f"http://127.0.0.1:8000/pdf/{quote(pdf_file)}"
                            )

                            if response.status_code == 200:
                                st.success(f"{pdf_file} deleted successfully!")
                                st.rerun()
                            else:
                                st.error(response.json().get("detail", "Delete failed."))

                        except requests.exceptions.RequestException as error:
                            st.error(f"API connection failed: {error}")

    else:
        st.info("No matching PDF documents found.")

    st.stop()


# SYSTEM INFO PAGE

elif active_page == "System Info":

    st.title("⚙️ System Information")

    st.caption("Technical overview of the DOCaks AI architecture.")

    st.markdown("### AI Technology Stack")

    st.markdown("""
    - **Language Model:** Qwen 2.5
    - **Vector Database:** ChromaDB
    - **Embedding Model:** MiniLM
    - **Retrieval:** Semantic Search
    - **Framework:** Streamlit and FastAPI
    """)

    st.stop()


# ABOUT PAGE

elif active_page == "About":

    st.title("✦ About DOCaks AI")

    st.markdown("""
    ### Your Documents. Understood. Instantly.

    DOCaks AI is an AI-powered document intelligence
    application designed to help users interact with
    their PDF documents using natural language.

    **Core Capabilities**

    - PDF document ingestion
    - Semantic search
    - Retrieval-Augmented Generation (RAG)
    - Context-grounded AI responses
    - Document source references
    """)

    st.stop()


# MAIN INTERFACE


st.components.v1.html("""


<div class="docaks-stage" style="
background:linear-gradient(120deg,#171c35,#202044,#111827);
border:1px solid #8B5CF6;
border-radius:22px;
padding:42px 38px;
font-family:Arial,sans-serif;
">
<div style="color:#C4B5FD;font-size:12px;font-weight:800;letter-spacing:4px;">
✦ AI POWERED DOCUMENT INTELLIGENCE
</div>
<div style="color:white;font-size:46px;font-weight:850;margin-top:15px;">
DOCaks <span style="color:#A78BFA;">AI</span>
</div>
<div style="color:#C4B5FD;font-size:18px;margin-top:12px;">
Your Documents. Understood. Instantly.
</div>
<div style="color:#AAB4C5;font-size:14px;margin-top:12px;">
Transform your PDFs into knowledge. Ask questions, discover insights and get intelligent answers grounded in your documents.
</div>
</div>
""", height=300)


st.divider()


if not st.session_state.messages:

    st.html("""
    <div style="
        border: 1px solid #303b59;
        border-radius: 18px;
                background:
            radial-gradient(ellipse at top left, rgba(55,150,255,.25), transparent 38%),
            radial-gradient(ellipse at top right, rgba(140,90,255,.22), transparent 38%),
            radial-gradient(ellipse at bottom left, rgba(40,110,220,.22), transparent 38%),
            radial-gradient(ellipse at bottom right, rgba(130,70,230,.22), transparent 38%),
                        linear-gradient(135deg, #17243a 0%, #18213a 50%, #151d30 100%);

        box-shadow:
            0 18px 35px rgba(0,0,0,.40),
            0 7px 20px rgba(65,130,255,.16),
            inset 0 2px 3px rgba(255,255,255,.16),
            inset 0 -5px 12px rgba(0,0,0,.35);
        padding: 35px 25px;
        text-align: center;
        margin: 25px 0;
    ">
        <div style="font-size: 42px; margin-bottom: 12px;">✦</div>
        <div style="
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        ">
            Welcome to DOCaks AI Assistant
        </div>
        <div style="
            color: #aab4c5;
            font-size: 15px;
        ">
            Upload your PDF documents and start asking questions.
            Get answers based on your documents with source references.
        </div>
    </div>
    """)


# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

   with st.chat_message(
    message["role"],
    avatar="🤖" if message["role"] == "assistant" else "👤"
):

        st.markdown(message["content"])

        if message.get("sources"):

            with st.expander("📚 View Sources"):

                for source in message["sources"]:
                    st.write(f"📄 {format_source(source)}")


# USER INPUT


with st.popover("📎 PDF KNOWLEDGE"):

    st.markdown("### Your PDF Library")

    pdf_files = []

    if PDF_DIR.exists():
        pdf_files = sorted([
            file for file in os.listdir(PDF_DIR)
            if file.lower().endswith(".pdf")
        ])

        if pdf_files:

         st.caption(f"{len(pdf_files)} documents available")

         for pdf_file in pdf_files:

            pdf_url = f"http://localhost:8000/pdf/{quote(pdf_file)}"

            st.markdown(
                f'<a href="{pdf_url}" target="_blank" '
                f'style="color:#C4B5FD; text-decoration:none; '
                f'font-size:14px;">📄 {pdf_file}</a>',
                unsafe_allow_html=True
            )

    else:
        st.info("No PDF documents uploaded yet.")

question = st.chat_input("✦ Ask anything about your documents...")


if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):

        try:

            with st.spinner("Searching documents and generating answer..."):

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"question": question},
                    timeout=180
                )

                response.raise_for_status()

                data = response.json()

            answer = data["answer"]
            sources = data.get("sources", [])

            st.markdown(answer)

            if sources:

                with st.expander("📚 View Sources"):

                    for source in sources:
                        st.write(f"📄 {format_source(source)}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        except requests.exceptions.RequestException as error:

            error_message = f"Backend connection failed: {error}"

            st.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "sources": []
            })

        except Exception as error:

            error_message = f"Something went wrong: {error}"

            st.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "sources": []
            })

            # FOOTER

st.markdown("""
<div style="
    text-align: center;
    padding: 25px 10px 10px 10px;
    margin-top: 40px;
    border-top: 1px solid #263247;
    color: #64748b;
    font-size: 12px;
">
    Powered by Qwen 2.5 · ChromaDB · MiniLM
    <br>
    Local PDF Intelligence Assistant
</div>
""", unsafe_allow_html=True)