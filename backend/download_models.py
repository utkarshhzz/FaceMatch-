"""Download required DeepFace models with retry logic"""
import os
import requests
from pathlib import Path
import time

def download_file_with_retry(url, destination, max_retries=5):
    """Download file with retry logic and resume capability"""
    
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    for attempt in range(max_retries):
        try:
            print(f"\n{'='*60}")
            print(f"Downloading: {url}")
            print(f"To: {destination}")
            print(f"Attempt {attempt + 1}/{max_retries}")
            print(f"{'='*60}")
            
            # Check if file already exists
            resume_byte_pos = destination.stat().st_size if destination.exists() else 0
            
            if resume_byte_pos > 0:
                print(f"Resuming from {resume_byte_pos / 1024 / 1024:.2f} MB")
            
            # Setup headers for resume
            headers = {'Range': f'bytes={resume_byte_pos}-'} if resume_byte_pos else {}
            
            # Download with timeout and streaming
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0)) + resume_byte_pos
            
            # Write to file
            mode = 'ab' if resume_byte_pos else 'wb'
            with open(destination, mode) as f:
                downloaded = resume_byte_pos
                chunk_size = 8192
                start_time = time.time()
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress update every 5MB
                        if downloaded % (5 * 1024 * 1024) < chunk_size:
                            percent = (downloaded / total_size) * 100 if total_size else 0
                            speed = downloaded / (time.time() - start_time) / 1024 / 1024
                            print(f"Progress: {downloaded/1024/1024:.1f}/{total_size/1024/1024:.1f} MB "
                                  f"({percent:.1f}%) - {speed:.2f} MB/s")
            
            # Verify download
            final_size = destination.stat().st_size
            if total_size > 0 and final_size < total_size:
                print(f"⚠️  Incomplete download: {final_size}/{total_size} bytes")
                continue
                
            print(f"✅ Download complete: {final_size / 1024 / 1024:.2f} MB")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ All {max_retries} attempts failed!")
                return False
    
    return False


def main():
    """Download all required models"""
    
    weights_dir = Path("/root/.deepface/weights")
    
    models = [
        {
            "name": "RetinaFace",
            "url": "https://github.com/serengil/deepface_models/releases/download/v1.0/retinaface.h5",
            "path": weights_dir / "retinaface.h5",
            "size_mb": 119
        },
        {
            "name": "ArcFace Weights",
            "url": "https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_weights.h5",
            "path": weights_dir / "arcface_weights.h5",
            "size_mb": 137
        }
    ]
    
    print("\n🚀 Starting DeepFace Model Downloads")
    print(f"Total size: ~{sum(m['size_mb'] for m in models)} MB\n")
    
    for model in models:
        print(f"\n📦 {model['name']} ({model['size_mb']} MB)")
        
        # Check if already exists
        if model['path'].exists():
            size = model['path'].stat().st_size / 1024 / 1024
            print(f"✅ Already exists: {size:.2f} MB")
            continue
        
        # Download
        success = download_file_with_retry(model['url'], model['path'])
        
        if not success:
            print(f"\n❌ Failed to download {model['name']}")
            return False
    
    print("\n" + "="*60)
    print("✅ All models downloaded successfully!")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        exit(1)
