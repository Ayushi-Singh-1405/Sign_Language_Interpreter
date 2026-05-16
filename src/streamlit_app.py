"""
Sign Language Interpreter - Main Application
Real-time ASL gesture recognition with Streamlit UI
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import pyttsx3
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.detector import HandDetector
from src.classifier import ASLClassifier

st.set_page_config(
    page_title="Sign Language Interpreter", page_icon="🤟", layout="wide"
)

st.title("🤟 Sign Language Interpreter")
st.markdown("Real-time ASL gesture recognition - Convert hand signs to text and speech")

if "word_buffer" not in st.session_state:
    st.session_state.word_buffer = ""
if "last_words" not in st.session_state:
    st.session_state.last_words = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "total_letters" not in st.session_state:
    st.session_state.total_letters = 0
if "current_letter" not in st.session_state:
    st.session_state.current_letter = "-"
if "current_confidence" not in st.session_state:
    st.session_state.current_confidence = 0.0
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []


class HandVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = HandDetector()
        self.classifier = ASLClassifier()
        self.classifier.load_model()
        self.frame_count = 0
        self.prediction_history = []
        self.min_confidence = 0.7
        self.stable_frames = 15
        self.last_letter = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        result = self.detector.detect(img)
        landmarks = self.detector.get_landmarks(result)

        current_letter = "-"
        confidence = 0.0

        if landmarks:
            img = self.detector.draw_hand(img, landmarks)

            features = self.detector.extract_features(landmarks)
            if features is not None:
                letter, conf = self.classifier.predict(features)
                if letter and conf >= self.min_confidence:
                    current_letter = letter
                    confidence = conf
                    self.prediction_history.append((letter, conf))
                else:
                    self.prediction_history.append((None, 0.0))
            else:
                self.prediction_history.append((None, 0.0))
        else:
            self.prediction_history.append((None, 0.0))

        if len(self.prediction_history) > self.stable_frames:
            self.prediction_history.pop(0)

        stable_letter = self._get_stable_letter()
        if stable_letter and stable_letter != self.last_letter:
            self.last_letter = stable_letter
            current_letter = stable_letter

        cv2.putText(
            img,
            f"Letter: {current_letter} ({confidence * 100:.0f}%)",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        st.session_state.current_letter = current_letter
        st.session_state.current_confidence = confidence

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def _get_stable_letter(self):
        if len(self.prediction_history) < self.stable_frames:
            return None

        recent = [p[0] for p in self.prediction_history[-self.stable_frames :] if p[0]]
        if not recent:
            return None

        letter_counts = {}
        for letter in recent:
            letter_counts[letter] = letter_counts.get(letter, 0) + 1

        max_count = max(letter_counts.values())
        if max_count >= self.stable_frames * 0.7:
            for letter, count in letter_counts.items():
                if count == max_count:
                    return letter
        return None


def init_tts():
    try:
        engine = pyttsx3.init()
        return engine
    except:
        return None


def speak_text(text, engine):
    if engine and text:
        engine.say(text)
        engine.runAndWait()


def main():
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📷 Live Camera Feed")

        ctx = webrtc_streamer(
            key="hand-detector",
            video_processor_factory=HandVideoProcessor,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
        )

        if ctx.state.playing:
            st.session_state.is_running = True
            st.success("Camera active - Show your hand to the camera!")
        else:
            st.session_state.is_running = False
            st.info("Click 'START' to begin hand detection")

        st.markdown("---")
        st.subheader("🖐️ Recognition Controls")

        controls = st.columns([1, 1, 1, 1, 1])
        with controls[0]:
            if st.button(
                "➕ Add Letter",
                use_container_width=True,
                disabled=not st.session_state.is_running,
            ):
                letter = st.session_state.current_letter
                if letter and letter != "-":
                    st.session_state.word_buffer += letter
                    st.session_state.total_letters += 1
                    st.rerun()
        with controls[1]:
            if st.button(
                "␣ Space",
                use_container_width=True,
                disabled=not st.session_state.is_running,
            ):
                if (
                    st.session_state.word_buffer
                    and not st.session_state.word_buffer.endswith(" ")
                ):
                    st.session_state.word_buffer += " "
                    st.rerun()
        with controls[2]:
            if st.button(
                "⌫ Delete",
                use_container_width=True,
                disabled=len(st.session_state.word_buffer) == 0,
            ):
                st.session_state.word_buffer = st.session_state.word_buffer[:-1]
                st.rerun()
        with controls[3]:
            if st.button(
                "🔊 Speak Text",
                use_container_width=True,
                disabled=not st.session_state.word_buffer,
            ):
                engine = init_tts()
                if engine:
                    speak_text(st.session_state.word_buffer, engine)
        with controls[4]:
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.word_buffer = ""
                st.session_state.last_words = []
                st.session_state.total_letters = 0
                st.session_state.current_letter = "-"
                st.session_state.current_confidence = 0.0
                st.rerun()

    with col2:
        st.subheader("📝 Recognition Output")

        current_letter = st.container()
        with current_letter:
            st.markdown("**Current Letter:**")
            letter_display = st.markdown(
                f"**{st.session_state.current_letter}**", unsafe_allow_html=True
            )

        confidence_value = st.session_state.current_confidence
        confidence_bar = st.progress(confidence_value)
        st.markdown(f"**Confidence:** {confidence_value * 100:.1f}%")

        st.markdown("---")
        st.subheader("📖 Word Buffer")
        text_area = st.text_area(
            "Recognized text will appear here...",
            st.session_state.word_buffer,
            height=150,
            label_visibility="collapsed",
        )

        word_count = len(st.session_state.last_words)
        st.caption(
            f"Words recognized: {word_count} | Letters: {st.session_state.total_letters}"
        )

        if st.session_state.last_words:
            st.markdown("**Recent words:**")
            recent = ", ".join(st.session_state.last_words[-5:])
            st.text(recent)

    st.markdown("---")

    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Instructions
        
        1. Click **START** to begin camera
        2. Position your hand in front of the webcam
        3. Make ASL alphabet gestures (A-Z)
        4. Hold each sign steady for the system to recognize
        5. Use special gestures:
           - **Space** - A flat open palm (separate words)
           - **Delete** - Thumb pointing down (remove last letter)
        6. Completed words are spoken aloud
        
        ### Tips for Best Results
        - Good lighting helps accuracy
        - Keep your hand 30-100cm from camera
        - Use a plain background
        - Move slowly between signs
        """)

    with st.expander("🔤 ASL Alphabet Reference"):
        cols = st.columns(13)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, letter in enumerate(alphabet):
            with cols[i % 13]:
                st.caption(f"**{letter}**")


if __name__ == "__main__":
    main()
