#!/usr/bin/env python3
"""
Viral YouTube Shorts videolarını bulur
"""

import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Konfigürasyon
API_KEY = os.getenv('YOUTUBE_API_KEY')
OUTPUT_DIR = 'data/cache'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# YouTube API istemcisi
youtube = build('youtube', 'v3', developerKey=API_KEY)

def find_viral_shorts():
    """Son 24 saatteki viral shorts'ları bulur"""
    
    print("🔍 Viral videolar aranıyor...")
    
    # Son 24 saat
    published_after = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
    
    try:
        # Shorts için arama (kısa videolar)
        search_response = youtube.search().list(
            part='id,snippet',
            type='video',
            videoDuration='short',  # 60 saniyeden kısa
            order='viewCount',
            publishedAfter=published_after,
            maxResults=50,
            regionCode='TR',  # Türkiye
            relevanceLanguage='tr'
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        if not video_ids:
            print("❌ Video bulunamadı")
            with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
                f.write('false')
            return None
        
        # Video detaylarını al
        videos_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()
        
        videos = []
        for item in videos_response.get('items', []):
            stats = item['statistics']
            
            # Viral kriterleri
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0))
            comment_count = int(stats.get('commentCount', 0))
            
            # Engagement rate hesapla
            if view_count > 0:
                engagement_rate = ((like_count + comment_count) / view_count) * 100
            else:
                engagement_rate = 0
            
            # Minimum viral kriterler
            if view_count >= 100000 and engagement_rate >= 2:
                videos.append({
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': round(engagement_rate, 2),
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'duration': item['contentDetails']['duration']
                })
        
        if not videos:
            print("❌ Viral kriterlere uyan video bulunamadı")
            with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
                f.write('false')
            return None
        
        # En yüksek engagement'a sahip videoyu seç
        videos.sort(key=lambda x: x['engagement_rate'], reverse=True)
        selected_video = videos[0]
        
        print(f"\n✅ Viral video bulundu!")
        print(f"📹 Başlık: {selected_video['title']}")
        print(f"👁️ İzlenme: {selected_video['view_count']:,}")
        print(f"❤️ Beğeni: {selected_video['like_count']:,}")
        print(f"📊 Engagement Rate: {selected_video['engagement_rate']}%")
        
        # Kaydet
        with open(f'{OUTPUT_DIR}/selected_video.json', 'w', encoding='utf-8') as f:
            json.dump(selected_video, f, ensure_ascii=False, indent=2)
        
        with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
            f.write('true')
        
        return selected_video
        
    except HttpError as e:
        print(f"❌ API Hatası: {e}")
        with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
            f.write('false')
        return None

if __name__ == '__main__':
    find_viral_shorts()
