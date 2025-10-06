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
You are a YouTube viral content analysis expert. Analyze the following viral YouTube Shorts video.

VIDEO INFORMATION:
- Title: {video_data['title']}
- Description: {video_data['description'][:500]}
- Channel: {video_data['channel_title']}
- Views: {video_data['view_count']:,}
- Likes: {video_data['like_count']:,}
- Comments: {video_data['comment_count']:,}
- Engagement Rate: {video_data['engagement_rate']}%

TASK:
Analyze in detail why this video went viral. Analyze under the following headings:

1. **Content Strategy** (Topic selection, timing, relevance)
2. **Psychological Triggers** (Emotional appeal, curiosity, shock factor)
3. **Technical Quality** (Title, thumbnail estimation, opening seconds)
4. **Social Factors** (Trends, virality potential, shareability)
5. **Algorithm Optimization** (Retention, engagement signals)

Provide 2-3 concrete points for each heading. Speak like a content creator.

Return in JSON format:
{{
    "viral_factors": {{
        "content_strategy": ["point1", "point2", "point3"],
        "psychological_triggers": ["point1", "point2", "point3"],
        "technical_quality": ["point1", "point2", "point3"],
        "social_factors": ["point1", "point2", "point3"],
        "algorithm_optimization": ["point1", "point2", "point3"]
    }},
    "main_hook": "What is the main appeal of this video? (1 sentence)",
    "target_audience": "Target audience profile (1 sentence)",
    "virality_score": 85,
    "key_takeaway": "Most important lesson for content creators (1-2 sentences)"
}}

RETURN ONLY JSON, no other text.
"""
    
    try:
        # Gemini model
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
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
            'ai_model': 'gemini-2.0-flash-exp'
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
