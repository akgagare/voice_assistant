from v3VoiceAnalyzer import VoiceAnalyzer
import os

def main():
    analyzer = VoiceAnalyzer()
    
    def analyze_voice():
        print("\nVoice Analysis")
        print("-------------")
        print("Press Enter to start recording...")
        input()
        
        result, audio_path = analyzer.record_and_analyze()
        
        print("\nAnalysis Results:")
        print("----------------")
        print(f"Audio saved at: {audio_path}")
        
        print("\nTranscribed Text:")
        print(result['transcribed_text'])
        
        print("\nFiller Word Analysis:")
        filler = result['filler_analysis']
        print(f"Total words: {filler['total_words']}")
        print(f"Total filler words: {filler['total_fillers']}")
        print(f"Filler word percentage: {filler['filler_percentage']:.2f}%")
        
        if filler['filler_count']:
            print("\nFiller Word Usage:")
            for word, count in filler['filler_count'].items():
                print(f"'{word}': {count} times")
        
        voice = result['voice_analysis']
        print("\nVoice Metrics:")
        for metric, value in voice['metrics'].items():
            print(f"{metric}: {value:.2f}")
        
        print("\nConfidence Indicators:")
        for indicator, value in voice['confidence_indicators'].items():
            print(f"{indicator}: {value:.2f}")
        
        print(f"\nFinal Confidence Score: {result['final_confidence_score']:.2f}")
        
        # Provide feedback and suggestions
        print("\nSuggestions for Improvement:")
        if filler['filler_percentage'] > 5:
            print("- Try to reduce the use of filler words")
            print(f"  (Currently using filler words {filler['filler_percentage']:.1f}% of the time)")
        
        metrics = voice['metrics']
        if metrics['pitch_stability'] < 50:
            print("- Work on maintaining a more stable pitch")
        if metrics['volume_stability'] < 50:
            print("- Try to maintain more consistent volume")
        if not (100 < metrics['speaking_rate'] < 140):
            print("- Adjust your speaking pace (aim for 120-140 words per minute)")
        
        return audio_path

    # Main program loop
    while True:
        print("\nVoice Analyzer")
        print("1. Record and analyze voice")
        print("2. Analyze existing audio file")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            analyze_voice()
            
        elif choice == '2':
            audio_path = input("Enter the path to the audio file: ")
            if os.path.exists(audio_path):
                analyzer.analyze_voice(audio_path)
            else:
                print("File not found!")
                
        elif choice == '3':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()