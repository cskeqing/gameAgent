import os
import urllib.request

def download_model(url, save_path):
    if os.path.exists(save_path):
        print(f"Model already exists: {save_path}")
        return

    print(f"Downloading model from {url}...")
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Downloaded: {save_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    # Ensure models dir exists
    if not os.path.exists("models"):
        os.makedirs("models")
        
    # YOLOv8n
    download_model(
        "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt",
        "yolov8n.pt" 
    )
