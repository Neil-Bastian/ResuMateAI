import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Page Configuration and Styling (Dark Theme) ---
st.set_page_config(
    page_title="ResuMate AI: Professional Review", 
    page_icon="📄", 
    layout="wide" 
)

# Custom CSS for a professional Dark Theme
st.markdown("""
<style>
    /* Main Background: Dark Blue/Gray */
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .reportview-container .main {
        background-color: #1a1a1a; 
    }
    
    /* Header/Title Style: White text against dark background */
    .css-1aumxm4 {
        color: #ffffff; 
        text-align: left;
        font-size: 3rem;
    }
    
    /* Subheader/Description */
    .stMarkdown {
        color: #cccccc;
    }

    /* Input Labels: Ensure labels are visible */
    label {
        color: #ffffff !important; 
    }

    /* Input Field Styling (File Uploader & Text Input) */
    .stTextInput>div>div>input, .stFileUploader>div>div>div>div {
        background-color: #2c2c2c; /* Darker input background */
        color: #ffffff;
        border-radius: 8px;
        border: 1px solid #555555;
        padding: 10px;
    }

    /* Button Styling (Primary Action Blue) */
    .stButton>button {
        font-size: 16px;
        font-weight: 600;
        color: white;
        background-color: #007BFF; 
        border-radius: 6px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    
    /* Analysis Results Headers */
    h3 {
        color: #007BFF;
        border-bottom: 1px solid #555555;
        padding-bottom: 5px;
    }
    
    /* Info/Error Boxes */
    div[data-testid="stNotification"] {
        background-color: #333333;
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
    "Upload your resume and specify the target role below. Receive a detailed, AI-powered critique focused on ATS alignment, quantifiable impact, and professional formatting."
)


# --- Input Definitions ---
st.markdown("---") 
uploaded_file = st.file_uploader(
    "Upload Resume (.PDF or .txt)", 
    type=["pdf", "txt"],
    help="Your document content will be securely extracted for analysis."
)
job_role = st.text_input(
    "Enter the Target Job Role",
    placeholder="e.g., Senior Data Scientist, UX Designer"
)
analyze_button = st.button("Analyze Resume")


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
    return "" # Added return for clarity
    

# --- Main Logic and Output Area ---
if analyze_button and uploaded_file:
    if not job_role.strip():
        st.warning("Please enter the Job Role you are targeting.")
        st.stop()

    st.markdown("---")

    with st.spinner("Analyzing your resume... Please wait."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("Could not extract text from the file or the file is empty. Please try another file.")
                st.stop()

            prompt = f"""
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique should be constructive, detailed, and actionable.
            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            Please structure your feedback into the following sections:
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
            
            st.markdown("---")
            st.markdown("### Analysis Results")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# Added a check for initial state if the button hasn't been pressed yet
elif not analyze_button:
    st.info("Upload your document and specify the role to begin the analysis.")
