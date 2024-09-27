import streamlit as st
from VoiceIn import VoiceIn
import os
from st_audiorec import st_audiorec

st.columns([2,1,2])[1].image("electro-pi.png")
st.title("Advix Bot")
st.info("Voice In Module")

if 'memory' not in st.session_state:
    st.session_state.memory = []

# st.file_uploader("Upload you voice:", type=['mp3','wav','m4a'])

voice_in = VoiceIn()

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    if os.path.exists('myfile.wav'):
        os.remove('myfile.wav')
    with open('myfile.wav', mode='xb') as f:
        f.write(wav_audio_data)
    text = voice_in.speech_to_text('myfile.wav')
    st.session_state.memory.append({'voice':wav_audio_data, 'text':text})

if st.session_state.memory != []:
    st.write("___")
    for m in st.session_state.memory:
        st.audio(m['voice'], format='audio/wav')
        st.write(m['text'])
        st.write("---")

