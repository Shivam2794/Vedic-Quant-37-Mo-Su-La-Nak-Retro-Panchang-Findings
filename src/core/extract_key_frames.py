import os
import subprocess
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

def extract_key_frames_ffmpeg(video_path, output_dir, ffmpeg_bin, interval_seconds=5):
    """
    Uses FFmpeg to extract high-resolution frames from a screen recording video
    at a regular interval (e.g., 1 frame every 5 seconds), then renames them to timestamp format.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Check if we already have files in the output directory
        existing_files = [f for f in os.listdir(output_dir) if f.endswith(".jpg") and not f.startswith("temp_")]
        if len(existing_files) > 10:
            print(f"Skipping {os.path.basename(video_path)} as it already has {len(existing_files)} key frames.")
            return True

    print(f"\nExtracting frames from {os.path.basename(video_path)} to {output_dir} using FFmpeg...")
    start_time = time.time()
    
    temp_pattern = os.path.join(output_dir, "temp_%04d.jpg")
    
    # We extract at a rate of 1 frame every 'interval_seconds'
    # Scale to 1920:1080 for crisp, high-resolution text visibility (word-by-word, pixel-by-pixel)
    # -q:v 2 sets high JPEG quality
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval_seconds},scale=1920:1080",
        "-q:v", "2",
        temp_pattern
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("FFmpeg extraction completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e.stderr.decode()}")
        return False
        
    # Rename temp files to timestamp format
    temp_files = sorted([f for f in os.listdir(output_dir) if f.startswith("temp_") and f.endswith(".jpg")])
    print(f"Found {len(temp_files)} temp frames. Renaming to timestamp format...")
    
    for idx, filename in enumerate(temp_files):
        # Frame index starts at 1
        seconds = idx * interval_seconds
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        timestamp_str = f"frame_{h:02d}_{m:02d}_{s:02d}.jpg"
        
        old_path = os.path.join(output_dir, filename)
        new_path = os.path.join(output_dir, timestamp_str)
        
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(old_path, new_path)
        
    end_time = time.time()
    print(f"Visual extraction complete! Processed {os.path.basename(video_path)} in {end_time - start_time:.2f} seconds.")
    return True

def main():
    video_dir = r"E:\New folder"
    videos = sorted([f for f in os.listdir(video_dir) if f.endswith(".mp4")])
    
    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin:
        print("CRITICAL: ffmpeg.exe could not be found!")
        return
        
    print(f"Using FFmpeg binary at: {ffmpeg_bin}")
    
    for video in videos:
        video_path = os.path.join(video_dir, video)
        video_name = os.path.splitext(video)[0]
        output_dir = os.path.join(video_dir, "key_frames", video_name)
        
        extract_key_frames_ffmpeg(video_path, output_dir, ffmpeg_bin, interval_seconds=5)

if __name__ == "__main__":
    main()
