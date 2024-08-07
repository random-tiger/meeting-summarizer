import openai
import streamlit as st

class OpenAIClient:
    def __init__(self):
        self.api_key = st.secrets["OPENAI_API_KEY"]
        if not self.api_key:
            raise ValueError("API key is not set. Please set the OPENAI_API_KEY in Streamlit secrets.")
        openai.api_key = self.api_key
    
    # Function to generate response based on prompt and model
    def generate_response(self, transcription, model, custom_prompt):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": custom_prompt},
                {"role": "user", "content": transcription}
            ],
            temperature=0,
        )
        return response.choices[0].message.content

    # Function to transcribe audio using Whisper
    def transcribe_audio(self, audio_file):
        transcription = openai.Audio.transcribe(
            model="whisper-1", file=audio_file
        )
        return transcription['text'] if isinstance(transcription, dict) else transcription.text

