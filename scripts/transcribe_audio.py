import whisper
import sys
import os
import json
from static_ffmpeg import add_paths

def transcribe(audio_path):
    print(f"Ensuring ffmpeg is available...")
    add_paths() # Add ffmpeg to the path
    
    print(f"Loading Whisper model (base)...")
    try:
        model = whisper.load_model("base") 
        print(f"Transcribing {audio_path}...")
        result = model.transcribe(audio_path)
        
        # Save the output to a text file
        output_path = audio_path.rsplit('.', 1)[0] + ".txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
            
        print(f"Successfully saved transcript to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <path_to_audio_file>")
    else:
        transcribe(sys.argv[1])
