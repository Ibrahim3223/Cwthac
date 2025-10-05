#!/usr/bin/env python3
"""
Videoyu YouTube'a yükler
"""

import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Konfigürasyon
CACHE_DIR = 'data/cache'
OUTPUT_DIR = 'data/processed'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """YouTube API'ye kimlik doğrulama"""
    
    credentials = None
    
    # GitHub Secrets'tan OAuth bilgilerini al
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    
    if all([client_id, client_secret, refresh_token]):
        # Refresh token ile credentials oluştur
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )
        
        # Token'ı yenile
        if credentials.expired:
            credentials.refresh(Request())
    
    else:
        print("❌ YouTube OAuth bilgileri eksik!")
        print("Lütfen şu secret'ları GitHub'a ekleyin:")
        print("- YOUTUBE_CLIENT_ID")
        print("- YOUTUBE_CLIENT_SECRET")
        print("- YOUTUBE_REFRESH_TOKEN")
        raise ValueError("OAuth credentials missing")
    
    return build('youtube', 'v3', credentials=credentials)

def load_video_metadata():
    """Video metadata'sını yükle"""
    with open(f'{OUTPUT_DIR}/video_metadata.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def load_script():
    """Script bilgilerini yükle (tags için)"""
    with open(f'{CACHE_DIR}/script.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def upload_video(youtube, video_path, metadata, script):
    """Videoyu YouTube'a yükle"""
    
    print("📤 Video YouTube'a yükleniyor...")
    
    # Shorts için özel hashtag ekle
    description = metadata['description']
    if '#Shorts' not in description:
        description += "\n\n#Shorts #YouTubeShorts"
    
    # Request body
    body = {
        'snippet': {
            'title': metadata['title'],
            'description': description,
            'tags': script['tags'] + ['viral', 'analiz', 'shorts', 'türkçe'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': 'public',  # veya 'private' test için
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Media upload
    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )
    
    # Upload request
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    print("⏳ Yükleme başlıyor...")
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"📊 Yüklendi: {progress}%")
    
    video_id = response['id']
    video_url = f"https://youtube.com/watch?v={video_id}"
    
    print(f"\n✅ Video başarıyla yüklendi!")
    print(f"🔗 URL: {video_url}")
    print(f"🆔 Video ID: {video_id}")
    
    # Sonucu kaydet
    result = {
        'video_id': video_id,
        'url': video_url,
        'title': metadata['title'],
        'uploaded_at': response['snippet']['publishedAt']
    }
    
    with open(f'{OUTPUT_DIR}/upload_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

if __name__ == '__main__':
    # YouTube servisini başlat
    youtube = get_authenticated_service()
    
    # Metadata yükle
    metadata = load_video_metadata()
    script = load_script()
    
    # Video yolu
    video_path = metadata['output_path']
    
    if not os.path.exists(video_path):
        print(f"❌ Video bulunamadı: {video_path}")
        exit(1)
    
    # Yükle
    result = upload_video(youtube, video_path, metadata, script)
    
    print("\n🎉 Tüm işlem tamamlandı!")
    print(f"📺 Yeni video: {result['url']}")
