import librosa
import librosa.display
import numpy as np
import speech_recognition as sr
import re
from scipy.signal import find_peaks

def extract_audio_features(audio_file):
    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Extract pitch (fundamental frequency)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = pitches[pitches > 0]  # Remove zero values
    avg_pitch = np.mean(pitch_values) if len(pitch_values) > 0 else 0
    
    # Extract loudness (RMS energy)
    rms = librosa.feature.rms(y=y)
    avg_loudness = np.mean(rms)
    
    # Extract speech rate (word per second estimation)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # Detect pauses (silence regions)
    silence_threshold = np.percentile(np.abs(y), 10)  # 10th percentile as threshold
    silent_parts = np.where(np.abs(y) < silence_threshold)[0]
    pause_ratio = len(silent_parts) / len(y)  # Ratio of silence in audio
    
    return {
        "avg_pitch": avg_pitch,
        "avg_loudness": avg_loudness,
        "speech_rate": tempo,
        "pause_ratio": pause_ratio
    }

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service unavailable."

def analyze_transcription(transcript):
    # Count filler words (common hesitation markers)
    filler_words = ["um", "uh", "like", "you know", "sort of", "kind of", "hmm"]
    filler_count = sum(transcript.lower().split().count(word) for word in filler_words)
    
    # Sentence confidence check (checking assertive vs weak language)
    weak_phrases = ["I think", "maybe", "probably", "kind of", "sort of"]
    weak_count = sum(1 for phrase in weak_phrases if phrase in transcript.lower())
    
    return {
        "filler_count": filler_count,
        "weak_phrases_count": weak_count,
        "word_count": len(transcript.split())
    }

def provide_feedback(audio_file):
    # Extract audio-based features
    audio_features = extract_audio_features(audio_file)
    
    # Transcribe and analyze text confidence
    transcript = transcribe_audio(audio_file)
    text_analysis = analyze_transcription(transcript)
    
    # Confidence assessment based on thresholds
    feedback = []
    
    if audio_features["avg_pitch"] > 200:
        feedback.append("Your pitch is slightly higher than normal. Try to maintain a steady tone.")
    
    if audio_features["avg_loudness"] < 0.01:
        feedback.append("Your voice is too soft. Try speaking louder for more confidence.")
    
    if text_analysis["filler_count"] > 3:
        feedback.append(f"You used {text_analysis['filler_count']} filler words. Try to minimize them.")
    
    if text_analysis["weak_phrases_count"] > 2:
        feedback.append(f"Avoid weak phrases like 'I think' or 'maybe'. Be more assertive.")

    if audio_features["pause_ratio"] > 0.2:
        feedback.append("There are too many long pauses. Try to keep a smooth flow in your speech.")
    
    if not feedback:
        feedback.append("Great job! Your speech sounds confident and clear.")
    
    return {
        "transcript": transcript,
        "audio_features": audio_features,
        "text_analysis": text_analysis,
        "feedback": feedback
    }

# Example usage
audio_file = "test_audio.wav"  # Change this to your actual file path
result = provide_feedback(audio_file)

# Display results
print("\nTranscription:\n", result["transcript"])
print("\nAudio Analysis:", result["audio_features"])
print("\nText Analysis:", result["text_analysis"])
print("\nFeedback:")
for f in result["feedback"]:
    print("-", f)
