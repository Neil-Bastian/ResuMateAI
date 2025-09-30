import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ResuMate AI: Your Resume Coach", 
    page_icon="📃", 
    layout="wide" 
)

st.markdown("""
<style>
    .reportview-container .main {
        background-color: #f0f2f6; 
    }
    .stButton>button {
        font-size: 18px;
        font-weight: bold;
        color: white;
        background-color: #007BFF;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .css-1aumxm4 {
        color: #333333;
        text-align: center;
    }
    .markdown-text-container h3 {
        color: #CC0000;
    }
</style>
""", unsafe_allow_html=True)

st.title("ResuMate AI: Professional Resume Review")
st.markdown(
    """
    **Upload your resume** and the **target job role** to receive an in-depth, AI-powered critique focused on ATS compatibility, impact, formatting, and overall interview readiness.
    """, 
    unsafe_allow_html=True
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("GEMINI_API_KEY not found. Please ensure your .env file is configured.")
    st.stop()


with st.sidebar:
    st.header("Input Parameters")
    uploaded_file = st.file_uploader(
        "Upload your resume in .PDF or .txt format", 
        type=["pdf", "txt"],
        help="Text will be extracted from the uploaded file for analysis."
    )
    job_role = st.text_input(
        "Enter the Job Role you are targeting",
        placeholder="e.g., Senior Data Scientist, UX Designer"
    )
    
    st.markdown("---")
    analyze_button = st.button("Analyze Resume")
    st.markdown("---")
    st.info("Analysis may take up to 30 seconds.")


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
    

if analyze_button:
    if not uploaded_file:
        st.error("Please upload your resume file to proceed.")
        st.stop()
    
    if not job_role.strip():
        st.warning("Please enter the Job Role you are targeting.")
        st.stop()

    st.subheader(f"Analyzing for Role: **{job_role.strip()}**")
    
    with st.spinner("Analyzing your resume..."):
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

            Please structure your feedback into the following sections, using clear markdown headings (H3) for each section:
            
            ### 1. First Impression (5-Second Test)
            Your immediate impression of the candidate. What stands out, for better or worse?
            
            ### 2. ATS and Keyword Alignment
            Analyze how well the resume is optimized for Applicant Tracking Systems (ATS). Compare keywords from the resume against the likely requirements for the '{job_role}' role. List critical keywords that are present and suggest any that are missing.
            
            ### 3. Impact and Quantification
            Review the bullet points. Identify 3-5 examples that could be stronger and rewrite them to be more impactful using the STAR (Situation, Task, Action, Result) method. Emphasize adding metrics and quantifiable achievements.
            
            ### 4. Clarity, Formatting, and Readability
            Comment on the structure and layout. Is it easy to read? Are there any formatting issues?
            
            ### 5. Overall Recommendation
            Provide a final summary and a recommendation. Based on the resume, would you recommend this candidate for an interview? Why or why not?
            """
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a world-class expert resume reviewer and career coach. Format your output using clear markdown with bold text and bullet points."
            )
            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.header("Analysis Results")
            st.markdown(response.text)
            st.markdown("---")

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

elif not analyze_button and not uploaded_file and not job_role:
    st.info("Use the sidebar to upload your resume and enter your target job role, then click 'Analyze Resume' to begin.")




