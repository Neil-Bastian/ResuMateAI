import streamlit as st
import PyPDF2
import io
import os
import chardet
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ResuMate AI: Professional Review", 
    page_icon="📄", 
    layout="wide" 
)

st.markdown("""
<style>
    /* Main Background */
    .reportview-container .main {
        background-color: #ffffff; /* Pure white background */
    }
    
    /* Header/Title Style */
    .css-1aumxm4 {
        color: #1a1a1a; /* Dark gray for a professional look */
        text-align: left;
        padding-bottom: 0px;
        margin-bottom: 0px;
    }

    /* Subheader/Description */
    .stMarkdown p {
        font-size: 16px;
        color: #555555;
    }

    /* Button Styling (Primary Action Blue) */
    .stButton>button {
        font-size: 18px;
        font-weight: 600;
        color: white;
        background-color: #007BFF; 
        border-radius: 6px;
        padding: 10px 28px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 123, 255, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 6px 8px rgba(0, 123, 255, 0.3);
    }
    
    /* Input Field Styling */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 10px;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.075);
    }
    
    /* Output Section Headers (Consistency) */
    .markdown-text-container h3 {
        color: #007BFF; /* Matching blue for section headers */
        border-bottom: 2px solid #eeeeee;
        padding-bottom: 5px;
        margin-top: 25px;
    }
    
    /* Streamlit Expander Styling */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #333333;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)


st.title("ResuMate AI: Professional Resume Review")
st.markdown(
    """
    Leverage advanced AI to get a comprehensive, detailed critique of your resume. Analysis covers ATS alignment, impact, formatting, and overall readiness for the interview stage.
    """
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("GEMINI_API_KEY not found. Please ensure your .env file is configured.")
    st.stop()


with st.sidebar:
    st.header("Upload & Target Role")
    uploaded_file = st.file_uploader(
        "Upload your resume in .PDF or .txt format", 
        type=["pdf", "txt"],
        help="Text will be extracted from the uploaded file for analysis."
    )
    job_role = st.text_input(
        "Enter the Target Job Role",
        placeholder="e.g., Senior Data Scientist, UX Designer"
    )
    
    st.markdown("---")
    analyze_button = st.button("Analyze Resume")
    st.markdown("---")
    st.info("The detailed analysis typically completes in under 30 seconds.")


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
        st.warning("Please enter the Target Job Role.")
        st.stop()

    st.subheader(f"Review for Role: **{job_role.strip()}**")
    
    with st.spinner("Executing comprehensive analysis..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("Text extraction failed or the file is empty. Please verify the uploaded file.")
                st.stop()

            prompt = f"""
            Act as an expert career coach and senior recruiter with 15 years of experience in the relevant industry for the role of '{job_role}'.
            Your task is to perform a comprehensive review of the following resume. Your critique must be constructive, detailed, and actionable.
            Target Job Role: {job_role}

            Resume Content:
            {file_content}

            You MUST structure your entire feedback into five distinct, clearly labeled sections. **Crucially, you must wrap each section's content in specific XML-like tags.** The response MUST only contain the tags and the markdown content within them.

            Tags to use:
            1. <FirstImpression>...</FirstImpression>
            2. <ATSKeywords>...</ATSKeywords>
            3. <ImpactQuantification>...</ImpactQuantification>
            4. <FormattingReadability>...</FormattingReadability>
            5. <OverallRecommendation>...</OverallRecommendation>

            Example Structure:
            <FirstImpression>
            ### 1. First Impression (5-Second Test)
            Your immediate impression...
            </FirstImpression>

            <ATSKeywords>
            ### 2. ATS and Keyword Alignment
            Analysis of ATS optimization...
            </ATSKeywords>

            [... and so on for the remaining sections ...]

            Ensure all content within the tags uses strong markdown (bold text, bullet points) for maximum readability.
            """
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a world-class expert resume reviewer and career coach. Your output MUST strictly adhere to the requested XML-like tag structure for parsing."
            )
            response = model.generate_content(prompt)
            raw_text = response.text
            
            st.markdown("---")
            st.header("Detailed Analysis Results")
            
            tags = {
                "First Impression": ("<FirstImpression>", "</FirstImpression>"),
                "ATS & Keyword Alignment": ("<ATSKeywords>", "</ATSKeywords>"),
                "Impact & Quantification": ("<ImpactQuantification>", "</ImpactQuantification>"),
                "Clarity, Formatting, & Readability": ("<FormattingReadability>", "</FormattingReadability>"),
                "Overall Recommendation": ("<OverallRecommendation>", "</OverallRecommendation>")
            }

            def extract_content(text, start_tag, end_tag):
                start_index = text.find(start_tag) + len(start_tag)
                end_index = text.find(end_tag)
                if start_index > len(start_tag) - 1 and end_index != -1:
                    return text[start_index:end_index].strip()
                return "Analysis content could not be found for this section."

            for section_title, (start_tag, end_tag) in tags.items():
                content = extract_content(raw_text, start_tag, end_tag)
                
                
                expanded = True if section_title in ["Overall Recommendation"] else False

                with st.expander(f"**{section_title}**", expanded=expanded):
                    st.markdown(content, unsafe_allow_html=True)
            
            st.markdown("---")
            st.success("Review complete. Focus on the 'Impact & Quantification' section for your next revision.")

        except Exception as e:
            st.error(f"An error occurred during analysis or output parsing: {str(e)}")

elif not analyze_button and not uploaded_file and not job_role:
    st.info("Utilize the sidebar on the left to upload your document and specify the job role, then initiate the review.")
