import os
import subprocess
import whisper
import torch
import time

def find_ffmpeg():
    # Check if ffmpeg is in path
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "ffmpeg"
    except FileNotFoundError:
        pass

    # Common winget installation paths
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    winget_paths = [
        os.path.join(local_app_data, "Microsoft", "WinGet", "Links", "ffmpeg.exe"),
        os.path.join(local_app_data, "Microsoft", "WinGet", "Packages"),
    ]
    
    for path in winget_paths:
        if os.path.exists(path) and path.endswith(".exe"):
            return path
        elif os.path.exists(path):
            # Walk and search
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.lower() == "ffmpeg.exe":
                        return os.path.join(root, f)
                        
    # Program files fallback
    program_files = [r"C:\Program Files", r"C:\Program Files (x86)"]
    for pf in program_files:
        if os.path.exists(pf):
            for root, dirs, files in os.walk(pf):
                for f in files:
                    if f.lower() == "ffmpeg.exe":
                        return os.path.join(root, f)
    return None

def extract_audio(video_path, audio_path, ffmpeg_bin):
    if os.path.exists(audio_path):
        print(f"Audio file already exists: {audio_path}")
        return True
    
    print(f"Extracting audio from {video_path} to {audio_path}...")
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=600)
        print(f"Extraction successful!")
        return True
    except subprocess.TimeoutExpired as e:
        print(f"Error extracting audio: Timeout expired after {e.timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e.stderr.decode()}")
        return False

def transcribe_audio(audio_path, transcript_path, model):
    print(f"Transcribing {audio_path}...")
    start_time = time.time()
    result = model.transcribe(audio_path, verbose=False, language="en")
    end_time = time.time()
    
    print(f"Transcription complete in {end_time - start_time:.2f} seconds!")
    
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"--- TRANSCRIPT FOR {os.path.basename(audio_path)} ---\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {result.get('duration', 0)/60:.2f} minutes\n")
        f.write("-" * 60 + "\n\n")
        
        for segment in result.get("segments", []):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            
            # Format timestamp as [HH:MM:SS]
            sh = int(start // 3600)
            sm = int((start % 3600) // 60)
            ss = int(start % 60)
            
            f.write(f"[{sh:02d}:{sm:02d}:{ss:02d}] {text}\n")
            
    print(f"Saved transcript to {transcript_path}")

def main():
    video_dir = r"E:\New folder"
    scratch_dir = r"C:\Users\Shivam Patel\Downloads" # Using Downloads/scratch for easy access
    
    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin:
        print("CRITICAL: ffmpeg.exe could not be found! Is the installation complete?")
        return
        
    print(f"Using FFmpeg binary at: {ffmpeg_bin}")
    
    # Programmatically add FFmpeg's directory to the system PATH so Whisper can find it
    ffmpeg_dir = os.path.dirname(ffmpeg_bin)
    if ffmpeg_dir:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        print(f"Added to PATH: {ffmpeg_dir}")
    
    print(f"Loading Whisper model on {'cuda' if torch.cuda.is_available() else 'cpu'}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # 'base' model is a great balance of speed and high accuracy. 
    # With a GPU we can also use 'small' or 'medium' if we want higher quality.
    model = whisper.load_model("base", device=device)

    videos = sorted([f for f in os.listdir(video_dir) if f.endswith(".mp4")])
    print(f"Found {len(videos)} videos to process.")
    
    for video in videos:
        video_path = os.path.join(video_dir, video)
        audio_name = os.path.splitext(video)[0] + ".wav"
        audio_path = os.path.join(scratch_dir, audio_name)
        transcript_name = os.path.splitext(video)[0] + "_transcript.txt"
        transcript_path = os.path.join(scratch_dir, transcript_name)
        
        print("\n" + "="*50)
        print(f"Processing: {video}")
        print("="*50)
        
        if extract_audio(video_path, audio_path, ffmpeg_bin):
            transcribe_audio(audio_path, transcript_path, model)
            # Remove temp wav file to save disk space
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Cleaned up temp audio file: {audio_path}")

if __name__ == "__main__":
    main()
