import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Page Configuration and Professional Styling (Dark Theme Fix) ---
st.set_page_config(
    page_title="ResuMate AI: Professional Review", 
    page_icon="📄", 
    layout="wide" 
)

# Custom CSS for a clean, professional Dark Theme that makes inputs blend
st.markdown("""
<style>
    /* 1. Main Background: Dark Blue/Gray */
    .stApp, .reportview-container .main {
        background-color: #1a1a1a; 
        color: #ffffff;
    }
    
    /* 2. Header/Title Style */
    .css-1aumxm4 {
        color: #ffffff; /* White title */
        text-align: left;
        padding-top: 15px;
    
    }

    /* 3. Input Field Styling (Text Input & Uploader Backgrounds) */
    .stTextInput>div>div>input {
        background-color: #1a1a1a; /* Very dark background for input fields */
        color: #ffffff;
        border-radius: 8px;
        border: 1px solid #555555;
        padding: 12px 35px;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.075);
        margin-top: 20px;
    }
    
    /* Ensure all text/labels inside the card are white */
    label, h2, h3, p {
        color: #ffffff !important;
    }

    /* Button Styling (Primary Action Blue) */
    .stButton>button {
        font-size: 18px;
        font-weight: 600;
        color: white;
        background-color: #007BFF; 
        border-radius: 8px;
        padding: 12px 35px;
        border: none;
        width: 100%; /* Full width for better alignment */
        transition: all 0.3s ease;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 6px 15px rgba(0, 123, 255, 0.4);
    }
    
    /* Expander Styling for Results (If used later) */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #eeeeee;
        font-size: 18px;
        background-color: #2c2c2c; 
        border-radius: 6px;
        padding: 10px;
        border-left: 4px solid #007BFF;
    }
    .streamlit-expanderContent {
        background-color: #1a1a1a;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


# --- API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("GEMINI_API_KEY not found. Please ensure your .env file is configured.")
    st.stop()


# --- Header Section ---
st.title("ResuMate AI: Professional Resume Review")
st.markdown(
    """
    **Upload your resume** and specify the **target role** below. Receive a detailed, AI-powered critique focused on ATS alignment, quantifiable impact, and professional formatting.
    """
)


# --- Input Definitions (Main Area Card) ---
# Inputs are placed in the main area to ensure the page is not empty
with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.header("Step 1: Document and Target")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume (.PDF or .txt)", 
            type=["pdf", "txt"],
            help="Your document content will be securely extracted for analysis."
        )
        
    with col2:
        job_role = st.text_input(
            "Enter the Target Job Role",
            placeholder="e.g., Senior Data Scientist, UX Designer, Account Executive"
        )
        
    analyze_button = st.button("Analyze Resume")
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Sidebar (Help/Instructions) ---
with st.sidebar:
    st.header("How to Get the Best Review")
    st.markdown(
        """
        The quality of the feedback depends on the detail provided:

        **1. Resume Format:**
        * Use clean PDF files; complex graphics can complicate text extraction.
        * Plain `.txt` files offer the highest reliability.

        **2. Target Role:**
        * Be as **specific as possible** (e.g., "Senior Digital Marketing Manager").
        * The AI uses this role for a deep **keyword alignment** check against industry standards.

        **3. Review Sections:**
        The analysis covers **ATS scoring**, **quantifiable achievement** critiques, and formatting.
        """
    )
    st.markdown("---")
    st.info("The comprehensive analysis typically completes in under 30 seconds.")


# --- Text Extraction Functions ---
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
    return ""


# --- Conditional Logic for Analysis or Initial State ---

# 1. Handle the Initial Landing State (before analysis is clicked)
if not analyze_button:
    st.info("To begin, please use the card above to upload your resume and specify the job role, then click 'Analyze Resume' for a comprehensive review.")
    st.stop()


# 2. Main Analysis Logic (Only runs if analyze_button is True)
if analyze_button:
    
    if not uploaded_file:
        st.error("Error: Please upload your resume file to proceed.")
        st.stop()
    
    if not job_role.strip():
        st.warning("Warning: Please enter the Target Job Role.")
        st.stop()

    st.subheader(f"Detailed Review for Role: **{job_role.strip()}**")
    
    with st.spinner("Executing comprehensive analysis..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("Error: Text extraction failed or the file is empty. Please verify the uploaded document.")
                st.stop()

            # LLM Prompt (using the simple markdown output structure requested in the original file)
            prompt = f"""
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique must be constructive, detailed, and actionable.
            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            Please structure your feedback into the following sections, using clear markdown headings (H3) for each section:
            1.  **First Impression (5-Second Test):** Your immediate impression of the candidate. What stands out, for better or worse?
            2.  **ATS & Keyword Alignment:** Analyze how well the resume is optimized for Applicant Tracking Systems (ATS). Compare keywords from the resume against the likely requirements for the '{job_role}' role. List critical keywords that are present and suggest any that are missing.
            3.  **Impact & Quantification:** Review the bullet points. Identify 3-5 examples that could be stronger and rewrite them to be more impactful using the STAR (Situation, Task, Action, Result) method. Emphasize adding metrics and quantifiable achievements.
            4.  **Clarity, Formatting, and Readability:** Comment on the structure and layout. Is it easy to read? Are there any formatting issues?
            5.  **Overall Recommendation:** Provide a final summary and a recommendation. Based on the resume, would you recommend this candidate for an interview? Why or why not?
            """
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a world-class expert resume reviewer and career coach. Format your output using clear markdown with bold text and bullet points."
            )
            response = model.generate_content(prompt)
            
            # --- Output Presentation ---
            st.markdown("---")
            st.header("Analysis Results")
            st.markdown(response.text)
            st.markdown("---")
            st.success("Review complete. Focus on the actionable feedback provided above for your next revision.")

        except Exception as e:
            st.error(f"An error occurred during analysis or output parsing: {str(e)}")



