**📄 ResuMate AI: Professional Resume Reviewer**
ResuMate AI is an advanced web application designed to provide immediate, expert-level critique on resumes tailored for a specific job role. Leveraging the power of the Gemini API, it analyzes a resume (PDF or TXT format) against industry best practices, focusing on Applicant Tracking System (ATS) alignment, quantifiable impact, and overall readability.

The application is built using Streamlit for a fast, interactive user interface in pure Python.

✨ Features
Role-Specific Analysis: Critique is customized based on the exact job title entered by the user, ensuring highly relevant feedback.

ATS Alignment Check: Identifies keyword optimization and suggests improvements for passing automated screening systems.

Quantifiable Impact Review: Focuses on converting generic duty statements into strong, results-oriented achievements using the STAR method.

Comprehensive Review: Provides a structured critique covering:

First Impression (5-Second Test)

ATS & Keyword Alignment

Impact & Quantification

Clarity, Formatting, and Readability

Overall Recommendation

File Support: Accepts resume uploads in both PDF and TXT formats.

🛠️ Installation and Setup
Prerequisites
Python 3.8+

A Gemini API Key (available from Google AI Studio).

Step 1: Clone the Repository
git clone [https://your-repository-url.git](https://your-repository-url.git)
cd resumate-ai

Step 2: Set Up Environment
It is highly recommended to use a virtual environment.

python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

Step 3: Install Dependencies
Install the required libraries listed in the project's main1.py file:

pip install streamlit pypdf2 python-dotenv chardet google-genai

Step 4: Configure API Key
Create a file named .env in the root directory of the project and add your Gemini API key:

# .env file
GEMINI_API_KEY="YOUR_API_KEY_HERE"

🚀 Usage
Run the Streamlit application from your terminal:

streamlit run main1.py

The application will automatically open in your web browser, typically at http://localhost:8501.

How to Use the App
Upload Resume: Use the file uploader to select your .pdf or .txt resume file.

Enter Job Role: Specify the exact job title you are applying for (e.g., "Senior Cloud Architect").

Analyze: Click the Analyze Resume button.

Review Feedback: View the detailed, structured critique in the main panel.

⚙️ Technology Stack
Core Language: Python

Frontend/UI: Streamlit

AI/LLM: Google Gemini API (gemini-2.5-flash)

Dependencies: PyPDF2, python-dotenv, chardet

🤝 Contributing
Contributions are welcome! Please feel free to open an issue or submit a pull request if you have suggestions for new features, bug fixes, or improvements to the analysis prompts.
