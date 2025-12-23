"""
Test script to upload face image directly
"""
import requests
import sys

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "utkarsh@gmail.com"
PASSWORD = "Utkarsh06"

# Get image path from command line
if len(sys.argv) < 2:
    print("Usage: python test_face_upload.py <path_to_image>")
    print("Example: python test_face_upload.py C:\\Users\\YourName\\Desktop\\photo.jpg")
    sys.exit(1)

image_path = sys.argv[1]

# Step 1: Login
print(f"🔐 Logging in as {EMAIL}...")
login_response = requests.post(
    f"{API_URL}/api/v1/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    sys.exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful!")
print(f"Token: {token[:50]}...")

# Step 2: Upload face
print(f"\n📸 Uploading face image: {image_path}")
with open(image_path, 'rb') as f:
    files = {'file': f}
    headers = {'Authorization': f'Bearer {token}'}
    
    upload_response = requests.post(
        f"{API_URL}/api/v1/faces/register",
        files=files,
        headers=headers
    )

print(f"\n📊 Response Status: {upload_response.status_code}")
print(f"📊 Response Body:")
print(upload_response.json())

if upload_response.status_code == 200:
    print("\n✅ Face uploaded successfully!")
else:
    print("\n❌ Face upload failed!")
