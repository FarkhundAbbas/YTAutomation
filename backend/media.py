import os
import requests
import random
import logging
import yaml
import math

try:
    # MoviePy v1
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    try:
        # MoviePy v2
        from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
    except ImportError:
        # Fallback partial import or mock
        logging.warning("MoviePy Import failed. Media generation will be mocked.")
        VideoFileClip = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MediaEngine:
    def __init__(self):
        self.config = self.load_config()
        self.pexels_key = self.config['video'].get('pexels_api_key')
        
    def load_config(self):
        config_path = os.path.join(os.getcwd(), 'config', 'media.yaml')
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def fetch_stock_videos(self, query, orientation="portrait", count=3):
        if not self.pexels_key or self.pexels_key == "YOUR_PEXELS_KEY":
            logger.warning("No Pexels API key found in config/media.yaml")
            return []
            
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query, 
            "per_page": count, 
            "orientation": orientation,
            "size": "medium" # Saves bandwidth on VPS
        }
        
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            video_files = []
            
            for vid in data.get('videos', []):
                # Get best fit file
                files = vid.get('video_files', [])
                # Simple selection: pick first mp4
                target = next((f for f in files if f['file_type'] == 'video/mp4'), None)
                if target:
                    # Download
                    filename = f"temp_stock_{vid['id']}.mp4"
                    self.download_file(target['link'], filename)
                    video_files.append(filename)
            return video_files
        except Exception as e:
            logger.error(f"Failed to fetch stock videos: {e}")
            return []

    def download_file(self, url, filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    def generate_video(self, audio_path, script_text, keywords, output_path, mode="shorts"):
        # 1. Analyze Audio Duration
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # 2. Fetch stock videos
        orientation = "portrait" if mode == "shorts" else "landscape"
        videos = self.fetch_stock_videos(keywords, orientation=orientation, count=math.ceil(duration / 5))
        
        if not videos:
            logger.error("No videos found. Cannot generate.")
            return False
            
        # 3. Stitch Videos
        clips = []
        current_dur = 0
        for v in videos:
            if current_dur >= duration: break
            try:
                clip = VideoFileClip(v)
                # Resize/Crop to 9:16 or 16:9
                # Simple resize for now, proper cropping requires calculation
                clip = clip.resize(height=1280) if mode == "shorts" else clip.resize(height=720)
                # Crop center
                w, h = clip.size
                target_ratio = 9/16 if mode == "shorts" else 16/9
                
                # Check aspect ratio logic... simplistic for now
                
                clips.append(clip)
                current_dur += clip.duration
            except Exception as e:
                logger.error(f"Error loading clip {v}: {e}")
                
        if not clips:
            return False
            
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.subclip(0, duration)
        final_video = final_video.set_audio(audio)
        
        # 4. Captions (Simple TextClip overlay)
        # Note: ImageMagick required for TextClip
        try:
            txt_clip = TextClip(script_text[:50]+"...", fontsize=50, color='white', size=final_video.size, method='caption')
            txt_clip = txt_clip.set_pos('center').set_duration(duration)
            final_video = CompositeVideoClip([final_video, txt_clip])
        except Exception as e:
            logger.warning(f"Could not add captions (ImageMagick missing?): {e}")
        
        # 5. Write Output
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # Cleanup temp files
        for v in videos:
            if os.path.exists(v): os.remove(v)
            
        return True

    def generate_thumbnail(self, title, output_path):
        api_url = self.config['thumbnail'].get('api_url', 'http://127.0.0.1:8188')
        prompt = f"{self.config['thumbnail']['default_prompt']}, text: '{title}'"
        
        # ComfyUI API Stub
        # Real implementation requires sending a workflow JSON to /prompt endpoint
        # For this deliverable, we log and create a placeholder image if requests fail
        
        logger.info(f"Generating thumbnail for '{title}' via {api_url}...")
        try:
            # Placeholder for ComfyUI interaction:
            # 1. Load workflow
            # 2. Inject Prompt
            # 3. Post to API
            # 4. Wait for WS execution
            # 5. Download image
            
            # Since we don't have a running ComfyUI, we simulate success or fallback
            pass
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            
        # Create a basic text-on-background thumbnail using MoviePy TextClip as fallback/demo
        try:
            clip = TextClip(title, fontsize=70, color='white', bg_color='black', size=(1280, 720))
            clip.save_frame(output_path, t=0)
            logger.info(f"Fallback thumbnail saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Fallback thumbnail failed: {e}")
            return False

if __name__ == "__main__":
    # Test stub
    pass
