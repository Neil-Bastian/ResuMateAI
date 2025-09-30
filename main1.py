import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Page Configuration and Professional Styling ---
st.set_page_config(
    page_title="ResuMate AI: Professional Review", 
    page_icon="📄", 
    layout="wide" 
)

# Custom CSS for a clean, card-based interface
st.markdown("""
<style>
    /* Main Background: Very light gray to give contrast for white containers */
    .reportview-container .main {
        background-color: #f8f9fa; 
    }
    
    /* Input Container (Card) Styling */
    .input-card {
        padding: 30px;
        border-radius: 12px;
        background-color: #ffffff; /* White card background */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        border-left: 5px solid #007BFF; /* Accent border */
    }

    /* Header/Title Style */
    .css-1aumxm4 {
        color: #1a1a1a; 
        text-align: left;
        padding-top: 15px;
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
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 6px 15px rgba(0, 123, 255, 0.4);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #1a1a1a;
        font-size: 18px;
        background-color: #e9ecef; /* Light gray header */
        border-radius: 6px;
        padding: 10px;
        border-left: 4px solid #007BFF;
    }
    .streamlit-expanderContent {
        padding-left: 15px;
        padding-top: 10px;
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


# --- Input Definitions (Moved to Main Area) ---
with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.header("Step 1: Document and Target")
    
    # Use columns to align the uploader and text input nicely
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
        
    st.markdown("---")
    analyze_button = st.button("Analyze Resume")
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Sidebar (Now for Instructions/Info) ---
with st.sidebar:
    st.header("Review Guidelines")
    st.markdown(
        """
        Our analysis provides a critique from the perspective of a senior recruiter with 15 years of industry experience.

        **Review Areas:**
        * **First Impression:** The immediate 5-second assessment.
        * **ATS Alignment:** Optimization for Applicant Tracking Systems.
        * **Quantifiable Impact:** Strengthening bullet points with the STAR method.
        * **Readability:** Formatting and layout assessment.
        """
    )
    st.markdown("---")
    st.info("The detailed analysis typically completes in under 30 seconds.")


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
    

# --- Main Logic and Output Area ---
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

            # LLM Prompt (Using the same efficient XML-like tag structure for reliable parsing)
            prompt = f"""
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique must be constructive, detailed, and actionable.
            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            You MUST structure your entire feedback into five distinct, clearly labeled sections. **Crucially, you must wrap each section's content in specific XML-like tags.** The response MUST only contain the tags and the markdown content within them. Do not include the section number or title within the markdown content inside the tags, as the application will provide the title.

            Tags to use:
            1. <FirstImpression>...</FirstImpression>
            2. <ATSKeywords>...</ATSKeywords>
            3. <ImpactQuantification>...</ImpactQuantification>
            4. <FormattingReadability>...</FormattingReadability>
            5. <OverallRecommendation>...</OverallRecommendation>

            Example Structure:
            <FirstImpression>
            **Immediate reaction:** The layout is clean but lacks a professional summary.
            * **Strength:** Strong quantifiable results are evident.
            * **Weakness:** Too much focus on duties rather than achievements.
            </FirstImpression>
            
            [... and so on for the remaining sections ...]

            Ensure all content within the tags uses strong markdown (bold text, bullet points) for maximum readability.
            """
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a world-class expert resume reviewer and career coach. Your output MUST strictly adhere to the requested XML-like tag structure for parsing."
            )
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # --- Parsing and Output Presentation using Expanders ---
            st.markdown("---")
            st.header("Analysis Results")
            
            # Define tags for parsing
            tags = {
                "1. First Impression (5-Second Test)": ("<FirstImpression>", "</FirstImpression>"),
                "2. ATS & Keyword Alignment": ("<ATSKeywords>", "</ATSKeywords>"),
                "3. Impact & Quantification (STAR Method Focus)": ("<ImpactQuantification>", "</ImpactQuantification>"),
                "4. Clarity, Formatting, & Readability": ("<FormattingReadability>", "</FormattingReadability>"),
                "5. Overall Recommendation": ("<OverallRecommendation>", "</OverallRecommendation>")
            }

            def extract_content(text, start_tag, end_tag):
                start_index = text.find(start_tag) + len(start_tag)
                end_index = text.find(end_tag)
                if start_index > len(start_tag) - 1 and end_index != -1:
                    return text[start_index:end_index].strip()
                return "Analysis content could not be found for this section. Please try rerunning the analysis."

            # Iterate through the defined sections and display in expanders
            for section_title, (start_tag, end_tag) in tags.items():
                content = extract_content(raw_text, start_tag, end_tag)
                
                # Expand the Overall Recommendation by default
                expanded = True if section_title.startswith("5.") else False

                with st.expander(f"{section_title}", expanded=expanded):
                    st.markdown(content, unsafe_allow_html=True)
            
            st.markdown("---")
            st.success("Review complete. Focus on the actionable feedback provided above for your next revision.")

elif not analyze_button and not uploaded_file and not job_role:
    # Initial landing state instruction
    st.info("To begin, use the sections above to upload your resume and specify the job role. Click 'Analyze Resume' for a comprehensive review.")
