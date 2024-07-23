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

# Function to generate response based on prompt and model
def generate_response(transcription, model, custom_prompt):
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

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

# Pre-canned prompts and their respective headings
pre_canned_prompts = {
    "meeting_summary": {
        "summary": {
            "prompt": "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points.",
            "heading": "Summary"
        },
        "key_points": {
            "prompt": "You are a proficient AI with a specialty in distilling information into key points. Based on the following text, identify and list the main points that were discussed or brought up. These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion. Your goal is to provide a list that someone could read to quickly understand what was talked about.",
            "heading": "Key Points"
        },
        "action_items": {
            "prompt": "You are an AI expert in analyzing conversations and extracting action items. Please review the text and identify any tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. These could be tasks assigned to specific individuals, or general actions that the group has decided to take. Please list these action items clearly and concisely.",
            "heading": "Action Items"
        },
        "sentiment": {
            "prompt": "As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. Indicate whether the sentiment is generally positive, negative, or neutral, and provide brief explanations for your analysis where possible.",
            "heading": "Sentiment Analysis"
        }
    },
    "user_research": {
        "summary": {
            "prompt": "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points.",
            "heading": "Summary"
        },
        "biographical_info": {
            "prompt": "You are a proficient AI with a specialty in distilling biographical information about people. Based on the following text, please identify biographical information about the subject of the research study.",
            "heading": "Biographical Info"
        },
        "key_insights": {
            "prompt": "You are a proficient AI with a specialty in distilling information into key points. Based on the following user research transcript, please identify the key insights. Identify and list the main points that were discussed or brought up. These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion. Your goal is to provide a list that someone could read to quickly understand what was talked about.",
            "heading": "Key Insights"
        },
        "recommendations": {
            "prompt": "You are a proficient AI with a specialty in identifying meaningful product opportunities. Based on the transcript, please identify product recommendations/opportunities.",
            "heading": "Recommendations"
        }
    }
}

# Streamlit app
def main():
    st.title("Meeting Summarizer")

    uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])
    if uploaded_file is not None:
        transcription = transcribe_audio(uploaded_file)
        st.subheader("Transcription")
        st.write(transcription)

        # Initialize session state for dynamic prompt inputs
        if 'prompts' not in st.session_state:
            st.session_state.prompts = []

        if st.button("Add GPT Task"):
            st.session_state.prompts.append({"prompt": "", "model": "gpt-4o", "heading": ""})

        for i, prompt_info in enumerate(st.session_state.prompts):
            st.subheader(f"GPT Task {i+1}")
            prompt_info["model"] = st.text_input("Model", value=prompt_info["model"], key=f"model_{i}")

            # Horizontal layout for pre-canned prompt buttons
            st.markdown("### Meeting Summary Prompts")
            cols = st.columns([1, 1, 1, 1])
            if cols[0].button("Summary", key=f"use_summary_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["meeting_summary"]["summary"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["meeting_summary"]["summary"]["heading"]
            if cols[1].button("Key Points", key=f"use_key_points_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["meeting_summary"]["key_points"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["meeting_summary"]["key_points"]["heading"]
            if cols[2].button("Action Items", key=f"use_action_items_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["meeting_summary"]["action_items"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["meeting_summary"]["action_items"]["heading"]
            if cols[3].button("Sentiment", key=f"use_sentiment_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["meeting_summary"]["sentiment"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["meeting_summary"]["sentiment"]["heading"]

            # User Research Synthesis buttons
            st.markdown("### User Research Synthesis Prompts")
            cols = st.columns([1, 1, 1, 1])
            if cols[0].button("Summary", key=f"use_user_summary_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["user_research"]["summary"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["user_research"]["summary"]["heading"]
            if cols[1].button("Biographical Info", key=f"use_biographical_info_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["user_research"]["biographical_info"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["user_research"]["biographical_info"]["heading"]
            if cols[2].button("Key Insights", key=f"use_key_insights_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["user_research"]["key_insights"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["user_research"]["key_insights"]["heading"]
            if cols[3].button("Recommendations", key=f"use_recommendations_prompt_{i}"):
                prompt_info["prompt"] = pre_canned_prompts["user_research"]["recommendations"]["prompt"]
                prompt_info["heading"] = pre_canned_prompts["user_research"]["recommendations"]["heading"]

            prompt_info["prompt"] = st.text_area("Prompt", value=prompt_info["prompt"], key=f"prompt_{i}")
            if st.button("Remove GPT Task", key=f"remove_gpt_task_{i}"):
                st.session_state.prompts.pop(i)
                break

        if st.button("Generate Meeting Minutes"):
            minutes = {}
            for i, prompt_info in enumerate(st.session_state.prompts):
                task_key = prompt_info["heading"] if prompt_info["heading"] else f"Task {i+1}"
                minutes[task_key] = generate_response(transcription, prompt_info["model"], prompt_info["prompt"])
            st.subheader("Meeting Minutes")
            for key, value in minutes.items():
                st.write(f"**{key}**")
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
