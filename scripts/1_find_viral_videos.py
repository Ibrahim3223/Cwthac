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

# API key kontrolü
if not API_KEY:
    print("❌ YOUTUBE_API_KEY environment variable bulunamadı!")
    with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
        f.write('false')
    exit(1)

print(f"🔑 API Key bulundu: {API_KEY[:10]}...")

# YouTube API istemcisi
try:
    youtube = build('youtube', 'v3', developerKey=API_KEY, cache_discovery=False)
    print("✅ YouTube API client başlatıldı")
except Exception as e:
    print(f"❌ Client başlatma hatası: {e}")
    with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
        f.write('false')
    exit(1)

def find_viral_shorts():
    """Viral shorts'ları bulur - çoklu strateji ile"""
    
    print("🔍 Viral videolar aranıyor...")
    
    # Strateji 1: Son 7 gün, shorts hashtag
    published_after_week = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
    
    search_queries = [
        {
            'part': 'id,snippet',  # ← ÖNEMLİ: part parametresi
            'q': '#shorts viral',
            'publishedAfter': published_after_week,
            'type': 'video',
            'order': 'viewCount',
            'maxResults': 50
        },
        {
            'part': 'id,snippet',  # ← ÖNEMLİ: part parametresi
            'q': 'shorts trending',
            'publishedAfter': published_after_week,
            'type': 'video',
            'order': 'viewCount',
            'maxResults': 50,
            'relevanceLanguage': 'en'  # İngilizce içerik
        },
        {
            'part': 'id,snippet',  # ← ÖNEMLİ: part parametresi
            'q': '#shorts',
            'publishedAfter': published_after_week,
            'type': 'video',
            'order': 'viewCount',
            'maxResults': 50
        }
    ]
    
    all_video_ids = []
    
    for idx, query_params in enumerate(search_queries):
        try:
            print(f"\n🔎 Strateji {idx + 1}: {query_params.get('q', 'default')}...")
            
            search_response = youtube.search().list(**query_params).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if video_ids:
                print(f"   ✓ {len(video_ids)} video bulundu")
                all_video_ids.extend(video_ids)
            else:
                print(f"   ✗ Video bulunamadı")
                
        except HttpError as e:
            print(f"   ✗ API hatası: {e}")
            continue
    
    # Duplicate'leri kaldır
    all_video_ids = list(set(all_video_ids))
    
    if not all_video_ids:
        print("\n❌ Hiçbir strateji ile video bulunamadı")
        print("💡 Öneri: API quota'nızı kontrol edin veya daha sonra tekrar deneyin")
        with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
            f.write('false')
        return None
    
    print(f"\n📊 Toplam {len(all_video_ids)} benzersiz video bulundu")
    print("📝 Video detayları alınıyor...")
    
    # Video detaylarını al (max 50 at a time)
    videos = []
    
    for i in range(0, len(all_video_ids), 50):
        batch_ids = all_video_ids[i:i+50]
        
        try:
            videos_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(batch_ids)
            ).execute()
            
            for item in videos_response.get('items', []):
                try:
                    stats = item['statistics']
                    content = item['contentDetails']
                    
                    # Duration check - ISO 8601 format (PT1M = 1 minute)
                    duration = content.get('duration', '')
                    
                    # Shorts: max 60 seconds
                    # PT59S, PT1M gibi formatları kontrol et
                    is_short = False
                    if 'PT' in duration:
                        # Basit kontrol: M veya H varsa short değil
                        if 'H' not in duration:  # Saat yok
                            if 'M' not in duration:  # Dakika yok = saniye only
                                is_short = True
                            elif duration.count('M') == 1:  # Tek M var
                                # PT1M veya daha az mı?
                                mins = int(duration.split('M')[0].replace('PT', ''))
                                if mins <= 1:  # 1 dakika veya daha az
                                    is_short = True
                    
                    if not is_short:
                        continue  # Shorts değil, atla
                    
                    view_count = int(stats.get('viewCount', 0))
                    like_count = int(stats.get('likeCount', 0))
                    comment_count = int(stats.get('commentCount', 0))
                    
                    # Engagement rate
                    engagement_rate = 0
                    if view_count > 0:
                        engagement_rate = ((like_count + comment_count) / view_count) * 100
                    
                    # Daha gevşek kriterler
                    if view_count >= 50000 and engagement_rate >= 1.5:
                        videos.append({
                            'video_id': item['id'],
                            'title': item['snippet']['title'],
                            'description': item['snippet'].get('description', ''),
                            'channel_title': item['snippet']['channelTitle'],
                            'channel_id': item['snippet']['channelId'],
                            'published_at': item['snippet']['publishedAt'],
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'engagement_rate': round(engagement_rate, 2),
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'duration': duration
                        })
                
                except (KeyError, ValueError, AttributeError) as e:
                    continue
                    
        except HttpError as e:
            print(f"❌ Video detay hatası: {e}")
            continue
    
    if not videos:
        print("\n❌ Shorts kriterlerine uyan video bulunamadı")
        print("📊 Bulunan videolar: Shorts değil veya yeterli engagement yok")
        print("💡 İpucu: Kriterleri daha da gevşetin (min 10K view)")
        with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
            f.write('false')
        return None
    
    # En yüksek engagement'a sahip videoyu seç
    videos.sort(key=lambda x: (x['engagement_rate'], x['view_count']), reverse=True)
    selected_video = videos[0]
    
    print(f"\n✅ Viral shorts bulundu!")
    print(f"📹 Başlık: {selected_video['title']}")
    print(f"👁️  İzlenme: {selected_video['view_count']:,}")
    print(f"❤️  Beğeni: {selected_video['like_count']:,}")
    print(f"💬 Yorum: {selected_video['comment_count']:,}")
    print(f"📊 Engagement: {selected_video['engagement_rate']}%")
    print(f"⏱️  Süre: {selected_video['duration']}")
    print(f"🔗 URL: https://youtube.com/watch?v={selected_video['video_id']}")
    
    # Kaydet
    with open(f'{OUTPUT_DIR}/selected_video.json', 'w', encoding='utf-8') as f:
        json.dump(selected_video, f, ensure_ascii=False, indent=2)
    
    with open(f'{OUTPUT_DIR}/video_selected.txt', 'w') as f:
        f.write('true')
    
    return selected_video

if __name__ == '__main__':
    find_viral_shorts()
