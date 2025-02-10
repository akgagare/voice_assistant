# Create analyzer instance with custom weights if desired

from voice_rater import VoiceRatingAnalyzer

analyzer = VoiceRatingAnalyzer(
    pitch_weight=1.0,
    tone_weight=1.0,
    variation_weight=0.8,
    pause_weight=0.7,
    confidence_weight=1.0
)

# Record and analyze voice
results = analyzer.analyze_voice(duration=10)

# Print detailed results
print(f"Overall Score: {results['overall_score']:.1f}/100\n")
print("Individual Parameters:")
for param, score in results['parameters'].items():
    print(f"{param.title()}: {score:.1f}/100")

# Get detailed feedback
print("\nDetailed Feedback:")
for feedback in analyzer.get_feedback():
    print(f"- {feedback}")

# Optionally save the recorded audio
analyzer.save_audio("my_recording.wav")