import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def process_inputs(audio_filepath, image_filepath):
    speech_to_text_output = transcribe_with_groq(
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
        audio_filepath=audio_filepath,
        stt_model="whisper-large-v3"
    )

    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=system_prompt + speech_to_text_output,
            encoded_image=encode_image(image_filepath),
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    else:
        doctor_response = "No image provided for me to analyze"

    voice_of_doctor = text_to_speech_with_elevenlabs(
        input_text=doctor_response,
        output_filepath="final.mp3"
    )

    return speech_to_text_output, doctor_response, voice_of_doctor


# CSS Styling for Dark Mode
custom_css = """
body {
    background: #313131;
    font-family: 'Segoe UI', sans-serif;
    color: #f5f5f5;
}
#title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    color: orange;
    margin-top: 10px;
    margin-bottom: 20px;
}
.card {
    background: #424242;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}
footer {display: none !important;}  /* remove Gradio footer */
label {font-size: 1.1rem !important;}
"""

with gr.Blocks(css=custom_css, title="MedAI-DPaP Multimodal LLM") as demo:
    # Title
    gr.HTML('<div id="title">🩺 MedAI-DPaP Multimodal LLM</div>')

    # App description
    gr.Markdown(
        """
        Welcome to **MedAI-DPaP** — your multimodal AI-powered healthcare companion.  
        Record your voice, upload an image, and get a response like a real doctor.  
        """,
        elem_classes="app-desc"
    )

    with gr.Row():
        with gr.Column(scale=1, elem_classes="card"):
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Record your Question"
            )
            image_input = gr.Image(
                type="filepath",
                label="🖼️ Upload Medical Image"
            )
            submit_btn = gr.Button("🔍 Analyze")

        with gr.Column(scale=1, elem_classes="card"):
            stt_output = gr.Textbox(label="📝 Speech to Text", lines=3)
            doctor_output = gr.Textbox(label="👨‍⚕️ Doctor's Response", lines=4)
            voice_output = gr.Audio(label="🔊 Doctor Speaks")

    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[stt_output, doctor_output, voice_output]
    )

demo.launch(debug=True)
