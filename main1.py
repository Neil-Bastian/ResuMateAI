import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Resume Critiquer",
    page_icon="📃",
    layout="centered"
)

st.markdown("""
    <style>
        /* Main page background */
        .stApp {
            background-color: #f9fafb;
        }

        /* Title styling */
        h1 {
            text-align: center;
            font-weight: 700;
            color: #1a202c;
        }

        /* Subtitle */
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #4a5568;
            margin-bottom: 25px;
        }

        /* File uploader & inputs */
        .stFileUploader, .stTextInput {
            background: #ffffff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
        }

        /* Button styling */
        div.stButton > button {
            background-color: #2563eb;
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 10px 20px;
            transition: 0.2s;
        }
        div.stButton > button:hover {
            background-color: #1d4ed8;
            transform: scale(1.02);
        }

        /* Results section */
        .result-card {
            background: #ffffff;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
            margin-top: 25px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📃 AI Resume Critiquer")
st.markdown("<p class='subtitle'>Upload your resume and get expert AI-powered feedback tailored to your target role.</p>", unsafe_allow_html=True)

]GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

uploaded_file = st.file_uploader("Upload your resume (.PDF or .TXT)", type=["pdf", "txt"])
job_role = st.text_input(" Enter the Job Role you are targeting")
analyze_button = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_file(file):
    bfile = file.read()
    if file.type == "application/pdf":
        return extract_text_from_pdf(bfile)
    elif file.type == "text/plain":
        result = chardet.detect(bfile)
        encoding = result.get('encoding', 'utf-8')
        return bfile.decode(encoding)

if analyze_button and uploaded_file:
    if not job_role.strip():
        st.warning("Please enter the Job Role you are targeting.")
        st.stop()

    with st.spinner("Analyzing your resume... Please wait."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("❌ Could not extract text from the file or the file is empty. Please try another file.")
                st.stop()

            prompt = f"""
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique should be constructive, detailed, and actionable.
            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            Please structure your feedback into the following sections:
            1.  **First Impression (5-Second Test):**
            2.  **ATS & Keyword Alignment:**
            3.  **Impact & Quantification:**
            4.  **Clarity, Formatting, and Readability:**
            5.  **Overall Recommendation:**
            """
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a world-class expert resume reviewer and career coach."
            )
            response = model.generate_content(prompt)

            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            st.markdown("###  Analysis Results")
            st.markdown(response.text)
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f" An error occurred during analysis: {str(e)}")
