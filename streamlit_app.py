import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model, ModelInference
import streamlit as st
import pdfplumber
import docx2txt

# Load environment variables from .env file
load_dotenv()

def get_credentials(key_type):
    """Get IBM Cloud credentials based on the type of API key."""
    url = "https://us-south.ml.cloud.ibm.com"
    apikey = os.getenv(key_type)
    if not apikey:
        st.error(f"API key for {key_type} is not set.")
    return {"url": url, "apikey": apikey}

def generate_code_summary(user_input):
    """Generate code summary using the Watsonx AI model."""
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 700,
        "repetition_penalty": 1.0
    }

   

   
    model = Model(
        model_id="ibm/granite-13b-chat-v2",
        params=parameters,
        credentials=get_credentials('API_KEY_CODE_SUMMARY'),
        project_id="5f7d24c8-0797-4cff-b45d-ca0599060bfe"
    )

    prompt = f"Provide a detailed explanation of how the following code functions. Additionally, suggest improvements to enhance its efficiency, readability, or structure. Finally, present a revised version of the code incorporating these improvements.\n\n{user_input}"

    try:
        generated_response = model.generate_text(prompt=prompt, guardrails=True)
    except Exception as e:
        st.error(f"Error generating code summary: {e}")
        return None
    
    return generated_response

def generate_qa(file_content, user_question):
    """Generate Q/A using the Watsonx AI model."""
    project_id = "d4f1f4c1-081c-4c73-9f53-53a36c816e24"
    deployment_id = "e649036b-0c85-4f42-9b6c-7fff446401bc"
    API_KEY = "rwTQpPdgqj-B53uCIhilNGl9P_9_Z6jrZFFR59LclmH1"
    URL = "https://us-south.ml.cloud.ibm.com"
    if not project_id or not deployment_id:
        st.error("Project ID or Deployment ID for Q/A is not set.")
        return None

    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 500,
        "stop_sequences": ["\n\n"],
        "repetition_penalty": 1
    }

    model = ModelInference(
        deployment_id=deployment_id,
        params=parameters,
        credentials={"url": URL, "apikey": API_KEY},
        project_id=project_id
    )

    prompt = f"""Answer the following question using strictly only information from the article. If there is no good answer in the article, say "The answer cannot be found in the given text. Don't jump on giving answers on your own. For 1 Question give 1 answer as priority".

Article: 
###
{file_content}
###

{user_question}"""

    try:
        generated_response = model.generate_text(prompt=prompt, guardrails=True)
    except Exception as e:
        st.error(f"Error generating Q/A: {e}")
        return None
    
    return generated_response

def generate_content_summary(user_input):
    """Generate document summary using the Watsonx AI model."""
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 2000,
        "repetition_penalty": 1.05
    }

    project_id = os.getenv("PROJECT_ID_DOC_SUMMARY")
    model_id = os.getenv("MODEL_ID_DOC_SUMMARY")

    if not project_id or not model_id:
        st.error("Project ID or Model ID for Document Summary is not set.")
        return None

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=get_credentials('API_KEY_DOC_SUMMARY'),
        project_id=project_id
    )

    prompt = (
        "You are Granite AI, a powerful summarization tool. Please read the following detailed text "
        "and provide a concise summary in bullet points, keeping the summary within 250 words. "
        "Use a 1, 2, 3 format for the points:\n\n"
        "Content to summarize:\n\n"
        f"{user_input}"
    )

    try:
        generated_response = model.generate_text(prompt=prompt, guardrails=True)
    except Exception as e:
        st.error(f"Error generating document summary: {e}")
        return None

    return generated_response

def generate_mcq(user_input):
    """Generate MCQs using the Watsonx AI model."""
    model_id = "ibm/granite-13b-chat-v2"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 900,
        "repetition_penalty": 1.05
    }

    project_id = os.getenv("PROJECT_ID_MCQ")

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=get_credentials("API_KEY_MCQ"),
        project_id=project_id
    )

    prompt = f"You are Granite Chat, an AI language model developed by IBM. You will be provided with summaries of up to 250 words, and your task is to create 3 multiple-choice questions (MCQs) or short questions based on each summary.\n\n{user_input}"

    generated_response = model.generate_text(prompt=prompt, guardrails=False)
    return generated_response

def extract_text_from_file(uploaded_file):
    """Extract text from different file types."""
    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type == "txt":
            return uploaded_file.read().decode("utf-8")
        elif file_type == "pdf":
            import pdfplumber
            with pdfplumber.open(uploaded_file) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        elif file_type == "docx":
            import docx2txt
            return docx2txt.process(uploaded_file)
        elif file_type in ["cpp", "py"]:
            return uploaded_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type.")
            return None
    except Exception as e:
        st.error(f"Error extracting text from file: {e}")
        return None

# Streamlit UI setup
st.title("SMARTSTUDY APP")
st.write("Welcome to the SMARTSTUDY APP! Choose an option below to get started.")

input_method = st.radio("How would you like to provide the content?", ("Upload a file", "Enter text manually"))
if input_method == "Upload a file":
    uploaded_file = st.file_uploader("Choose a file (txt, py, java, cpp, pdf, docx)", type=["txt", "py", "java", "cpp", "pdf", "docx"])
    if uploaded_file:
        user_input = extract_text_from_file(uploaded_file)
        if user_input:
            st.write("File content successfully loaded.")
else:
    user_input = st.text_area("Enter your content here:", height=300)

# Model choice and question input
st.sidebar.header("Choose the task")
model_choice = st.sidebar.selectbox(
    "Which model do you want to use?",
    ("Code Refactor", "Summary Generator", "Quiz Generator", "Q/A Generator")
)

if model_choice == "Q/A Generator":
    user_question = st.text_input("Enter your question related to the provided text:")
else:
    user_question = None

# Single submit button
if st.button("Submit"):
    if user_input:
        if model_choice == "Code Refactor":
            summary_response = generate_code_summary(user_input)
            if summary_response:
                st.subheader("Generated Code Refactor:")
                st.write(summary_response)
        elif model_choice == "Summary Generator":
            content_summary_response = generate_content_summary(user_input)
            if content_summary_response:
                st.subheader("Generated Summary:")
                st.write(content_summary_response)
        elif model_choice == "Quiz Generator":
            mcq_response = generate_mcq(user_input)
            if mcq_response:
                st.subheader("Generated Quiz:")
                st.write(mcq_response)
        elif model_choice == "Q/A Generator":
            if user_question:
                qa_response = generate_qa(user_input, user_question)
                if qa_response:
                    st.subheader("Generated Q/A:")
                    st.write(qa_response)
                else:
                    st.error("No valid response generated for the Q/A.")
            else:
                st.error("Please provide a question to generate the Q/A response.")
    else:
        st.error("Please provide the content to generate the response.")
