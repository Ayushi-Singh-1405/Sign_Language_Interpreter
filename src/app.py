import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Sign Language Interpreter", page_icon="🤟", layout="wide"
)

st.title("🤟 Sign Language Interpreter")
st.markdown("Real-time ASL gesture recognition using MediaPipe + ML")

if "word_buffer" not in st.session_state:
    st.session_state.word_buffer = ""
if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0
if "current_letter" not in st.session_state:
    st.session_state.current_letter = "-"
if "is_active" not in st.session_state:
    st.session_state.is_active = False

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Camera Feed")
    frame_placeholder = st.empty()
    st.frame()

    controls = st.columns([1, 1, 1, 1])
    with controls[0]:
        start_btn = st.button("▶ Start", type="primary")
    with controls[1]:
        stop_btn = st.button("■ Stop")
    with controls[2]:
        clear_btn = st.button("🗑 Clear Text")
    with controls[3]:
        speak_btn = st.button("🔊 Speak")

with col2:
    st.subheader("Output")

    st.markdown("### Current Letter")
    letter_display = st.empty()
    letter_display.markdown(f"# {st.session_state.current_letter}")

    st.markdown(f"**Confidence:** {st.session_state.confidence:.1%}")

    st.markdown("---")
    st.markdown("### Word Buffer")
    text_display = st.text_area(
        "", st.session_state.word_buffer, height=150, label_visibility="hidden"
    )

    st.markdown("---")
    st.markdown("### Instructions")
    st.info("""
    1. Click **Start** to begin
    2. Show ASL gestures to your camera
    3. Hold each sign for ~1 second
    4. Use gestures for:
       - **Space** → Confirm word
       - **Delete** → Remove last letter
    """)

if clear_btn:
    st.session_state.word_buffer = ""
    st.rerun()

st.markdown("---")
st.markdown("### Quick Reference: ASL Alphabet")
cols = st.columns(13)
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for i, letter in enumerate(alphabet):
    with cols[i % 13]:
        st.caption(letter)
