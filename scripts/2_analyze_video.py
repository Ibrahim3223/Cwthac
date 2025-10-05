#!/usr/bin/env python3
"""
Viral videoyu Google Gemini ile analiz eder
"""

import os
import json
import google.generativeai as genai

# Konfigürasyon
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

CACHE_DIR = 'data/cache'

def load_video_data():
    """Seçilen video verisini yükle"""
    with open(f'{CACHE_DIR}/selected_video.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_with_gemini(video_data):
    """Video verilerini Gemini ile analiz et"""
    
    print("🧠 Video Gemini AI ile analiz ediliyor...")
    
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

SADECE JSON döndür, başka açıklama ekleme.
"""
    
    try:
        # Gemini model
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        response = model.generate_content(analysis_prompt)
        
        # JSON parse et
        response_text = response.text.strip()
        
        # Markdown kod bloğu varsa temizle
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        analysis = json.loads(response_text)
        
        print("✅ Gemini analizi tamamlandı")
        print(f"🎯 Ana Hook: {analysis['main_hook']}")
        print(f"📊 Virality Score: {analysis['virality_score']}/100")
        
        # Kaydet
        output = {
            'video_data': video_data,
            'analysis': analysis,
            'analyzed_at': None,
            'ai_model': 'gemini-1.5-flash'
        }
        
        with open(f'{CACHE_DIR}/analysis.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        print(f"Response: {response_text[:200]}")
        raise
    except Exception as e:
        print(f"❌ Gemini analiz hatası: {e}")
        raise

if __name__ == '__main__':
    video_data = load_video_data()
    analyze_with_gemini(video_data)
