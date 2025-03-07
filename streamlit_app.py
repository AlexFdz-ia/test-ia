import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import google.generativeai as genai

google_api_key=st.secrets["GOOGLE_API_KEY"]

# Funcion para generar la respuesta de Gemini
def generate_answer(system_message, chat_history, prompt):

    # Establecemos la API de Google
    # genai.configure(api_key=google_api_key)
    # Seleccionamos el modelo a usar
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Añadimos al historial el ultimo mensaje del ususario
    chat_history += f" User: {prompt}"

    # Combinamos el mensaje del sistema con el historial de mensajes para darle contexto
    full_prompt = f"{system_message}\n\n" + "\n".join(chat_history) + "\nAssistant:"

    # Generamos la respuesta y la añadimos al historial
    response = model.generate_content(full_prompt).text
    chat_history += f" Assistant: {response}"
    st.session_state['chat_history'] = chat_history

    return response

# Show title and description.
st.title("📄 Test creator")
st.write(
    "Upload a document below and let Gemini create a full test! "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
api_key = st.text_input("Google API Key", type="password")
api_key = True
if not api_key:
    st.info("Please add your Google API key to continue.", icon="🗝️")
else:

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
    if uploaded_file is not None:
        PdfReader = PdfReader(uploaded_file)

        total_pages = len(PdfReader.pages)

        # Establecemos un mensaje de sistema para el bot
        # Especificamos su ámbito y que sea fiel a los documentos subidos
        system_message = (
            """
            You are an AI model specializing in creating accurate and engaging multiple-choice test questions. Follow these guidelines:

            Scope of Knowledge: Only use the information provided by the user in the documents they supply. Do not use external knowledge or make assumptions beyond the provided information.

            Question Structure:

            Each question should test a specific concept or detail from the document.
            Provide exactly four options for each question. Ensure only one option is correct, and the others are plausible but incorrect.
            Answer Key: After each question, clearly indicate the correct answer. For example: (Correct Answer: Option A).

            Professional Tone: Ensure the questions are clear, concise, and aligned with the subject matter of the document. Avoid ambiguous phrasing.

            Limitations: If the user asks a question that is unrelated to the documents provided, politely respond:
            "I’m sorry, but I can only create test questions based on the information in the documents you have provided. Please share the relevant document or clarify your request."

            Examples of Test Questions:

            Example based on a hypothetical document about photosynthesis:

            Question: What is the primary function of chlorophyll in photosynthesis?
            A) To store energy
            B) To absorb light energy
            C) To produce oxygen directly
            D) To convert glucose into energy
            (Correct Answer: Option B)
            Example based on a hypothetical document about World War II:

            Question: Which event marked the beginning of World War II?
            A) The bombing of Pearl Harbor
            B) Germany’s invasion of Poland
            C) The signing of the Treaty of Versailles
            D) The D-Day landings in Normandy
            (Correct Answer: Option B)

            Document information:

            """
        )

        # Modelo para contar el numero de tokens de un mensaje
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        for num_page in range(total_pages):

            page = PdfReader.pages[num_page]
            
            msg_placeholder = system_message + page.extract_text()

            # Contamos el número de tokens usado en el mensaje del sistema
            # num_tokens = model.count_tokens(msg_placeholder).total_tokens

            # Comprobamos que no supere el límite establecido por Gemini
            # if num_tokens >= 1000000:
            #     break
            # else:
            # Añadimos el texto al mensaje del sistema
            #     system_message += page.extract_text()
            system_message += page.extract_text()

        
    



    # Ask the user for a question via `st.text_area`.
    prompt = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and prompt:

        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = ''

        # Generamos la respuesta manteniendo el historial de mensajes
        answer = generate_answer(system_message, st.session_state['chat_history'], prompt)

        # Stream the response to the app using `st.write_stream`.
        st.text(answer)



