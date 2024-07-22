import streamlit as st
import os
from openai import OpenAI
from docx import Document
from io import BytesIO

api_key = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to transcribe audio using Whisper
def transcribe_audio(audio_file):
    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcription['text'] if isinstance(transcription, dict) else transcription.text

# Function to summarize the transcription
def abstract_summary_extraction(transcription, custom_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

# Function to extract key points
def key_points_extraction(transcription, custom_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

# Function to extract action items
def action_item_extraction(transcription, custom_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

# Function to perform sentiment analysis
def sentiment_analysis(transcription, custom_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

# Function to generate meeting minutes
def meeting_minutes(transcription, summary_prompt, key_points_prompt, action_items_prompt, sentiment_prompt):
    abstract_summary = abstract_summary_extraction(transcription, summary_prompt)
    key_points = key_points_extraction(transcription, key_points_prompt)
    action_items = action_item_extraction(transcription, action_items_prompt)
    sentiment = sentiment_analysis(transcription, sentiment_prompt)
    return {
        'abstract_summary': abstract_summary,
        'key_points': key_points,
        'action_items': action_items,
        'sentiment': sentiment
    }

# Function to save meeting minutes as a Word document
def save_as_docx(minutes):
    doc = Document()
    for key, value in minutes.items():
        heading = ' '.join(word.capitalize() for word in key.split('_'))
        doc.add_heading(heading, level=1)
        doc.add_paragraph(value)
        doc.add_paragraph()
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit app
def main():
    st.title("Meeting Summarizer")

    uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])
    if uploaded_file is not None:
        transcription = transcribe_audio(uploaded_file)

        st.subheader("Transcription")
        st.write(transcription)

        summary_prompt = st.text_area("Summary Prompt", value="You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points.")
        key_points_prompt = st.text_area("Key Points Prompt", value="You are a proficient AI with a specialty in distilling information into key points. Based on the following text, identify and list the main points that were discussed or brought up. These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion. Your goal is to provide a list that someone could read to quickly understand what was talked about.")
        action_items_prompt = st.text_area("Action Items Prompt", value="You are an AI expert in analyzing conversations and extracting action items. Please review the text and identify any tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. These could be tasks assigned to specific individuals, or general actions that the group has decided to take. Please list these action items clearly and concisely.")
        sentiment_prompt = st.text_area("Sentiment Analysis Prompt", value="As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. Indicate whether the sentiment is generally positive, negative, or neutral, and provide brief explanations for your analysis where possible.")

        if st.button("Generate Meeting Minutes"):
            minutes = meeting_minutes(transcription, summary_prompt, key_points_prompt, action_items_prompt, sentiment_prompt)
            st.subheader("Meeting Minutes")
            for key, value in minutes.items():
                st.write(f"**{key.replace('_', ' ').capitalize()}**")
                st.write(value)

            docx_file = save_as_docx(minutes)

            st.download_button(
                label="Download Meeting Minutes",
                data=docx_file,
                file_name="meeting_minutes.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
