#!/usr/bin/env python3
"""
Video için Google Gemini ile senaryo oluşturur
"""

import os
import json
import google.generativeai as genai

# Konfigürasyon
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

CACHE_DIR = 'data/cache'

def load_analysis():
    """Analiz sonuçlarını yükle"""
    with open(f'{CACHE_DIR}/analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_script_with_gemini(analysis_data):
    """Analiz sonuçlarına göre Gemini ile senaryo oluştur"""
    
    print("📝 Video senaryosu Gemini ile oluşturuluyor...")
    
    video_data = analysis_data['video_data']
    analysis = analysis_data['analysis']
    
    script_prompt = f"""
You are a YouTube Shorts scriptwriter. Based on the following viral video analysis, write a 45-50 second analysis video script.

ORIGINAL VIDEO:
- Title: {video_data['title']}
- Channel: {video_data['channel_title']}
- Views: {video_data['view_count']:,}

ANALYSIS RESULTS:
- Main Hook: {analysis['main_hook']}
- Virality Score: {analysis['virality_score']}/100
- Key Takeaway: {analysis['key_takeaway']}

SCRIPT RULES:
1. First 3 seconds: Attention-grabbing opening (hook)
2. 5-25 seconds: Explain what the video does
3. 25-40 seconds: Explain WHY it went viral (2-3 main reasons)
4. 40-50 seconds: CTA and value proposition

LANGUAGE & TONE:
- Young, dynamic, authentic
- No jargon, simple English
- Exciting but not exaggerated
- Not "watch this video now" but "here's why this video exploded" style

FORMAT:
Specify timing for each sentence.

Return in JSON format:
{{
    "title": "Video title (max 80 characters, curiosity-inducing)",
    "hook": "First 3 seconds sentence",
    "scenes": [
        {{
            "timing": "0-3",
            "text": "Hook sentence",
            "visual_note": "What to show on screen"
        }},
        {{
            "timing": "3-8",
            "text": "Second part",
            "visual_note": "Visual description"
        }}
        // ... total 45-50 seconds
    ],
    "description": "YouTube description text (don't forget to credit the source!)",
    "tags": ["tag1", "tag2", "tag3"],
    "word_count": 120
}}

RETURN ONLY JSON, no other text.
"""
    
    try:
        # Gemini model
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={
                'temperature': 0.8,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        response = model.generate_content(script_prompt)
        
        # JSON parse et
        response_text = response.text.strip()
        
        # Markdown kod bloğu varsa temizle
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        script = json.loads(response_text)
        
        # Kaynak belirtme kontrolü
        if 'source' not in script['description'].lower() and 'credit' not in script['description'].lower():
            script['description'] += f"\n\n📌 Source Video: https://youtube.com/watch?v={video_data['video_id']}\n👤 Original Channel: {video_data['channel_title']}\n\n⚠️ This video is for educational and analysis purposes. Fair use."
        
        print("✅ Senaryo oluşturuldu")
        print(f"📺 Başlık: {script['title']}")
        print(f"🎬 Hook: {script['hook']}")
        print(f"🔢 Kelime Sayısı: {script.get('word_count', 'N/A')}")
        
        # Tam senaryoyu yazdır
        print("\n📝 FULL SCRIPT:")
        for scene in script['scenes']:
            print(f"[{scene['timing']}s] {scene['text']}")
        
        # Kaydet
        with open(f'{CACHE_DIR}/script.json', 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        return script
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        print(f"Response: {response_text[:200]}")
        raise
    except Exception as e:
        print(f"❌ Senaryo oluşturma hatası: {e}")
        raise

if __name__ == '__main__':
    analysis_data = load_analysis()
    generate_script_with_gemini(analysis_data)
