#!/usr/bin/env python3
"""
Viral videoyu AI ile analiz eder
"""

import os
import json
from openai import OpenAI

# Konfigürasyon
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
CACHE_DIR = 'data/cache'

def load_video_data():
    """Seçilen video verisini yükle"""
    with open(f'{CACHE_DIR}/selected_video.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_with_ai(video_data):
    """Video verilerini AI ile analiz et"""
    
    print("🧠 Video AI ile analiz ediliyor...")
    
    analysis_prompt = f"""
Sen bir YouTube viral içerik analiz uzmanısın. Aşağıdaki viral YouTube Shorts videosunu analiz et.

VIDEO BİLGİLERİ:
- Başlık: {video_data['title']}
- Açıklama: {video_data['description'][:500]}
- Kanal: {video_data['channel_title']}
- İzlenme: {video_data['view_count']:,}
- Beğeni: {video_data['like_count']:,}
- Yorum: {video_data['comment_count']:,}
- Engagement Rate: {video_data['engagement_rate']}%

GÖREV:
Bu videonun neden viral olduğunu detaylı analiz et. Aşağıdaki başlıklar altında analiz yap:

1. **İçerik Stratejisi** (Konu seçimi, timing, relevance)
2. **Psikolojik Tetikleyiciler** (Duygusal çekicilik, merak, şok faktörü)
3. **Teknik Kalite** (Başlık, thumbnail tahmini, açılış saniyesi)
4. **Sosyal Faktörler** (Trend, virality potansiyeli, shareability)
5. **Algoritma Optimizasyonu** (Retention, engagement sinyalleri)

Her başlık için 2-3 somut madde ver. Analiz Türkçe olsun ve içerik üretici gibi konuş.

JSON formatında döndür:
{{
    "viral_factors": {{
        "content_strategy": ["madde1", "madde2", "madde3"],
        "psychological_triggers": ["madde1", "madde2", "madde3"],
        "technical_quality": ["madde1", "madde2", "madde3"],
        "social_factors": ["madde1", "madde2", "madde3"],
        "algorithm_optimization": ["madde1", "madde2", "madde3"]
    }},
    "main_hook": "Bu videonun ana çekiciliği ne? (1 cümle)",
    "target_audience": "Hedef kitle profili (1 cümle)",
    "virality_score": 85,
    "key_takeaway": "İçerik üreticiler için en önemli ders (1-2 cümle)"
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen bir YouTube viral içerik analiz uzmanısın. JSON formatında detaylı analizler yaparsın."},
                {"role": "user", "content": analysis_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        print("✅ AI analizi tamamlandı")
        print(f"🎯 Ana Hook: {analysis['main_hook']}")
        print(f"📊 Virality Score: {analysis['virality_score']}/100")
        
        # Kaydet
        output = {
            'video_data': video_data,
            'analysis': analysis,
            'analyzed_at': json.dumps(None)  # Will be set by json.dump
        }
        
        with open(f'{CACHE_DIR}/analysis.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        raise

if __name__ == '__main__':
    video_data = load_video_data()
    analyze_with_ai(video_data)
