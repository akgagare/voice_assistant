# Create analyzer instance
from voice_analysiser import VoiceRatingAnalyzer
analyzer = VoiceRatingAnalyzer()

# Record and analyze voice (5 seconds by default)
results = analyzer.analyze_voice()

# Print scores
print(f"Overall Score: {results['overall_score']:.1f}/100\n")
print("Individual Parameters:")
for param, score in results['parameters'].items():
    print(f"{param.title()}: {score:.1f}/100")

# Get detailed feedback
print("\nFeedback:")
for feedback in analyzer.get_feedback():
    print(f"- {feedback}")