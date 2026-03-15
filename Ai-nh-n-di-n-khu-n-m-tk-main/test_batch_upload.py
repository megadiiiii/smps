#!/usr/bin/env python3
"""
Test script for batch image upload to Face Authorization system.
Demonstrates how to upload multiple images efficiently.
"""

import os
import sys
import time
import requests
from pathlib import Path
from typing import List, Tuple

BASE_URL = "http://localhost:5000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/batch_embed"


def test_batch_upload(image_folder: str, max_images: int = 10) -> dict:
    """
    Upload images from a folder to the batch embedding API.
    
    Args:
        image_folder: Path to folder containing images
        max_images: Maximum number of images to upload (default 10 for testing)
    
    Returns:
        Dictionary with results
    """
    image_folder = Path(image_folder)
    
    if not image_folder.exists():
        print(f"❌ Folder not found: {image_folder}")
        return {"success": False, "error": "Folder not found"}
    
    # Find all image files
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    image_files = [
        f for f in image_folder.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"❌ No image files found in {image_folder}")
        return {"success": False, "error": "No images found"}
    
    # Limit to max_images
    image_files = image_files[:max_images]
    total_images = len(image_files)
    
    print(f"\n📁 Found {total_images} images to upload")
    print(f"🎯 Uploading to: {UPLOAD_ENDPOINT}\n")
    
    results = {
        "total": total_images,
        "success": 0,
        "failed": 0,
        "errors": [],
        "files": []
    }
    
    start_time = time.time()
    
    for idx, image_path in enumerate(image_files, 1):
        try:
            print(f"[{idx:3d}/{total_images}] Uploading {image_path.name}... ", end="", flush=True)
            
            # Prepare multipart form data
            with open(image_path, "rb") as f:
                files = {"image": (image_path.name, f, "image/*")}
                response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
            
            if response.status_code in (200, 201):
                result = response.json()
                results["success"] += 1
                results["files"].append({
                    "filename": image_path.name,
                    "status": "✓",
                    "embedding_dim": result.get("embedding_dim")
                })
                print(f"✓ Success (dim: {result.get('embedding_dim')})")
            else:
                error_msg = response.json().get("error", "Unknown error")
                results["failed"] += 1
                results["errors"].append({
                    "filename": image_path.name,
                    "error": error_msg
                })
                print(f"✗ Failed ({response.status_code}): {error_msg}")
        
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "filename": image_path.name,
                "error": str(e)
            })
            print(f"✗ Error: {str(e)}")
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print(f"✓ SUCCESS: {results['success']}/{total_images}")
    print(f"✗ FAILED:  {results['failed']}/{total_images}")
    print(f"⏱️  TIME:    {elapsed:.1f}s ({elapsed/total_images:.1f}s per image)")
    print("="*70)
    
    if results["errors"]:
        print("\n❌ Errors encountered:")
        for error in results["errors"]:
            print(f"  - {error['filename']}: {error['error']}")
    
    return results


def upload_with_metadata(
    image_folder: str,
    metadata_file: str = None,
    max_images: int = 10
) -> dict:
    """
    Upload images with person metadata (requires database).
    
    Args:
        image_folder: Path to folder with images
        metadata_file: JSON file with person info [{person_id, name, filename}, ...]
        max_images: Max images to upload
    
    Returns:
        Results dictionary
    """
    import json
    
    image_folder = Path(image_folder)
    
    if not metadata_file:
        print("⚠️  Metadata file not provided, using simple batch upload")
        return test_batch_upload(image_folder, max_images)
    
    metadata_path = Path(metadata_file)
    if not metadata_path.exists():
        print(f"❌ Metadata file not found: {metadata_path}")
        return {"success": False, "error": "Metadata file not found"}
    
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    print(f"\n📋 Loaded metadata for {len(metadata)} people")
    
    batch_endpoint = f"{BASE_URL}/api/batch_register"
    
    # Prepare batch data
    batch_data = []
    for item in metadata[:max_images]:
        image_path = image_folder / item["filename"]
        if not image_path.exists():
            print(f"⚠️  Image not found: {image_path}")
            continue
        
        # Read and encode image
        import base64
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        batch_data.append({
            "person_id": item["person_id"],
            "name": item["name"],
            "image_base64": image_base64
        })
    
    print(f"🎯 Uploading {len(batch_data)} faces with metadata...\n")
    
    try:
        response = requests.post(batch_endpoint, json=batch_data, timeout=60)
        result = response.json()
        
        print(f"✓ Total: {result['summary']['total']}")
        print(f"✓ Success: {result['summary']['success']}")
        print(f"✗ Failed: {result['summary']['failed']}")
        
        if result['summary']['failed'] > 0:
            print("\nFailed registrations:")
            for res in result['results']:
                if not res['success']:
                    print(f"  - {res['person_id']}: {res['message']}")
        
        return result
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Test with sample images folder
    test_folder = "uploads"
    
    if len(sys.argv) > 1:
        test_folder = sys.argv[1]
    
    print("🚀 Face Authorization - Batch Upload Test")
    print(f"Using folder: {test_folder}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        if response.status_code != 200:
            print(f"⚠️  Server returned {response.status_code}")
    except (requests.ConnectionError, requests.Timeout):
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("   Make sure the Flask app is running: python app.py")
        print("   (Server may still be loading models, wait 30 seconds)")
        sys.exit(1)
    
    # Run batch upload
    results = test_batch_upload(test_folder, max_images=10)
    
    # Optional: test with metadata
    # results = upload_with_metadata(test_folder, "metadata.json", max_images=10)
