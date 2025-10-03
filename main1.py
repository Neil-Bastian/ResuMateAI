import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
import re
from dotenv import load_dotenv

load_dotenv()

if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False

st.set_page_config(
    page_title="ResuMate AI: Professional Review", 
    page_icon="📄", 
    layout="wide" 
)
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

    /* 4. Input Field Styling (Text Input & Uploader Backgrounds) */
    .stTextInput>div>div>input {
        background-color: #1a1a1a; /* Very dark background for input fields */
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #555555;
        padding: 10px;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.075);
    }
    
    /* Target the stContainer background if needed (Streamlit v1.x class) */
    .stContainer {
        background-color: #2c2c2c;
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
    
    /* Expander Styling for Results */
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

    /* Custom Score Card Styling */
    .score-card {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(145deg, #1f1f1f, #2c2c2c);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        color: #ffffff;
        border: 1px solid #007BFF;
    }
    .score-number {
        font-size: 4em;
        font-weight: 900;
        color: #4CAF50; /* Initial color, adjusted dynamically in Python */
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    .score-label {
        font-size: 1.2em;
        font-weight: 500;
        letter-spacing: 1px;
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("GEMINI_API_KEY not found. Please ensure your .env file is configured.")
    st.stop()

st.title("ResuMate AI: Professional Resume Review")
st.markdown(
    """
    **Upload your resume** and specify the **target role** below. Receive a detailed, AI-powered critique focused on ATS alignment, quantifiable impact, and professional formatting.
    """
)

st.markdown('<div class="input-card">', unsafe_allow_html=True) 
with st.container():
    st.header("Step 1: Document and Target")
    
    uploaded_file = st.file_uploader(
        "Upload Resume (.PDF or .txt)", 
        type=["pdf", "txt"],
        help="Your document content will be securely extracted for analysis."
    )
        
    job_role = st.text_input(
        "Enter the Target Job Role",
        placeholder="e.g., Senior Data Scientist, UX Designer, Account Executive"
    )
    
    analyze_button = st.button(
        "Analyze Resume", 
        disabled=st.session_state.analysis_running
    )
    
st.markdown('</div>', unsafe_allow_html=True) 


with st.sidebar:
    st.sidebar.header("How to Get the Best Review")
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
    st.info("The comprehensive analysis typically completes in under 40 seconds.")


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

def display_score(score):
    """Generates an HTML component to display the CV Score with color coding."""
    try:
        score_val = int(score)
    except (ValueError, TypeError):
        score_val = 0

    if score_val >= 80:
        color = "#4CAF50"  
    elif score_val >= 60:
        color = "#FFC107"  
    else:
        color = "#F44336"  
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-label">Estimated ATS Compatibility Score</div>
            <div class="score-number" style="color: {color};">{score_val}/100</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def extract_content_robust(text, start_tag, end_tag):
    """
    Extracts content between start_tag and end_tag using regular expressions 
    for robust parsing, handling newlines and case variation.
    """
    pattern = rf"{re.escape(start_tag)}(.*?){re.escape(end_tag)}"
    
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    return None

def run_analysis(uploaded_file, job_role):
    st.session_state.analysis_running = True
    
    if not uploaded_file:
        st.error("Error: Please upload your resume file to proceed.")
        st.session_state.analysis_running = False
        return
    
    if not job_role.strip():
        st.warning("Warning: Please enter the Target Job Role.")
        st.session_state.analysis_running = False
        return

    st.subheader(f"Detailed Review for Role: **{job_role.strip()}**")
    
    with st.spinner("Executing comprehensive analysis..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("Error: Text extraction failed or the file is empty. Please verify the uploaded document.")
                st.session_state.analysis_running = False
                return

            prompt = f"""
            ***RESPONSE STRUCTURE MANDATE: Your entire output MUST strictly contain ONLY the required XML-like tags and the markdown content within them. DO NOT include any introductory or concluding text outside of these tags.***
            
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique must be constructive, detailed, and actionable.
            You are able to consistently score CV's based on a certain scoring format. The scoring must be strict and must not change unless the CV is changed.

            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            You **MUST** structure your entire feedback into six distinct, clearly labeled sections, and include the CV Score tag. Crucially, you **MUST** wrap each section's content and the score in the specific XML-like tags listed below. The response **MUST ONLY** contain the tags and the markdown content within them.
            
            * **ATS Alignment:** Max 35 points
            * **Impact & Quantification (STAR):** Max 35 points
            * **Formatting & Readability:** Max 30 points
            This score must be very strict and must follow the given criteria. It must not change if the CV is re-uploaded.

            Tags to use (all are MANDATORY and must be closed):
            1. **<CVScore>... (0-100 numerical value)</CVScore>** (This MUST immediately follow the Justification.)
            2. **<FirstImpression>...</FirstImpression>**
            3. **<ATSKeywords>...</ATSKeywords>**
            4. **<ImpactQuantification>...</ImpactQuantification>**
            5. **<FormattingReadability>...</FormattingReadability>**
            6. **<OverallRecommendation>...</OverallRecommendation>**

            Example Structure (Adhere to this exactly, only varying the content):
            ATS Alignment: 28/35
            Impact & Quantification: 20/35
            Formatting & Readability: 25/30
            TOTAL SCORE: 73/100.
            <CVScore>73</CVScore>
            <FirstImpression>
            **Immediate reaction:** The layout is clean but lacks a professional summary.
            </FirstImpression>
            
            [... and so on for the remaining sections ...]

            Ensure all content within the content tags uses strong markdown (bold text, bullet points) for maximum readability.
            """
            
            model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction="You are a world-class expert resume reviewer and career coach. Your output MUST strictly adhere to the requested XML-like tag structure for parsing. **Crucially, prioritize scoring consistency over creativity.**"
            )
            
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0}
            )
            raw_text = response.text
            st.markdown("---")
            
            tags = {
                "CV Score": ("<CVScore>", "</CVScore>"),
                "1. First Impression (5-Second Test)": ("<FirstImpression>", "</FirstImpression>"),
                "2. ATS & Keyword Alignment": ("<ATSKeywords>", "</ATSKeywords>"),
                "3. Impact & Quantification (STAR Method Focus)": ("<ImpactQuantification>", "</ImpactQuantification>"),
                "4. Clarity, Formatting, & Readability": ("<FormattingReadability>", "</FormattingReadability>"),
                "5. Overall Recommendation": ("<OverallRecommendation>", "</OverallRecommendation>")
            }

            
            score_tags = tags.get("CV Score")
            if score_tags:
                cv_score = extract_content_robust(raw_text, *score_tags)
            else:
                cv_score = None 

            
            if cv_score:
                col_score, col_results = st.columns([1, 3])
                with col_score:
                    display_score(cv_score)
                with col_results:
                    st.header("Analysis Results")
            else:
                st.header("Analysis Results")
                st.error("Could not extract the numerical CV score. Displaying raw AI response for structural debugging.")
                st.code(raw_text, language='text')
                st.session_state.analysis_running = False
                return

            
            content_tags = {k: v for k, v in tags.items() if k not in ["CV Score"]}

            all_parsed_successfully = True
            for section_title, (start_tag, end_tag) in content_tags.items():
                content = extract_content_robust(raw_text, start_tag, end_tag)
                
                expanded = section_title.startswith(("Scoring Justification", "5."))

                with st.expander(f"{section_title}", expanded=expanded):
                    if content:
                        st.markdown(content, unsafe_allow_html=True)
                    else:
                        st.error(f"Failed to parse content for section: **{section_title}** from the AI response.")
                        st.code(raw_text, language='text') 
                        st.warning("The AI output structure was not strictly maintained (likely a missing tag). Please try analyzing again.")
                        all_parsed_successfully = False
                        break
            
            st.markdown("---")
            if all_parsed_successfully:
                st.success("Review complete. Focus on the actionable feedback provided above for your next revision.")
            

        except Exception as e:
            st.error(f"An error occurred during analysis or output parsing: {str(e)}")
        finally:
            st.session_state.analysis_running = False


if not analyze_button:
    st.info("To begin, please use the card above to upload your resume and specify the job role, then click 'Analyze Resume' for a comprehensive review.")
    st.stop()


if analyze_button:
    run_analysis(uploaded_file, job_role)
