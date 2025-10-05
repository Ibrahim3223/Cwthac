#!/usr/bin/env python3
"""
Video için senaryo oluşturur
"""

import os
import json
from openai import OpenAI

# Konfigürasyon
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
CACHE_DIR = 'data/cache'

def load_analysis():
    """Analiz sonuçlarını yükle"""
    with open(f'{CACHE_DIR}/analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_script(analysis_data):
    """Analiz sonuçlarına göre senaryo oluştur"""
    
    print("📝 Video senaryosu oluşturuluyor...")
    
    video_data = analysis_data['video_data']
    analysis = analysis_data['analysis']
    
    script_prompt = f"""
Sen bir YouTube Shorts senaryo yazarısın. Aşağıdaki viral video analizine dayanarak 45-50 saniye uzunluğunda bir analiz videosu senaryosu yaz.

ORIJINAL VIDEO:
- Başlık: {video_data['title']}
- Kanal: {video_data['channel_title']}
- İzlenme: {video_data['view_count']:,}

ANALİZ SONUÇLARI:
- Ana Hook: {analysis['main_hook']}
- Virality Score: {analysis['virality_score']}/100
- Key Takeaway: {analysis['key_takeaway']}

SENARYO KURALLARI:
1. İlk 3 saniye: Dikkat çekici açılış (hook)
2. 5-25 saniye: Videonun ne yaptığını açıkla
3. 25-40 saniye: NEDEN viral olduğunu açıkla (2-3 ana neden)
4. 40-50 saniye: CTA ve değer önerisi

DİL VE TON:
- Genç, dinamik, samimi
- Jargon kullanma, basit Türkçe
- Heyecan verici ama abartısız
- "Şimdi bu videoyu izleyin" değil, "Bu video şu yüzden patladı" tarzı

FORMAT:
Her cümle için timing belirt.

JSON formatında döndür:
{{
    "title": "Video başlığı (max 80 karakter, merak uyandıran)",
    "hook": "İlk 3 saniye söylenecek cümle",
    "scenes": [
        {{
            "timing": "0-3",
            "text": "Hook cümlesi",
            "visual_note": "Ekranda ne gösterilecek"
        }},
        {{
            "timing": "3-8",
            "text": "İkinci bölüm",
            "visual_note": "Visual açıklama"
        }}
        // ... toplam 45-50 saniye
    ],
    "description": "YouTube açıklama metni (kaynak belirtmeyi unutma!)",
    "tags": ["tag1", "tag2", "tag3"],
    "word_count": 120
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen YouTube Shorts için viral senaryo yazarısın. Kısa, etkili ve akılda kalıcı içerikler üretirsin."},
                {"role": "user", "content": script_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        script = json.loads(response.choices[0].message.content)
        
        # Kaynak belirtme kontrolü
        if 'kaynak' not in script['description'].lower():
            script['description'] += f"\n\n📌 Kaynak Video: https://youtube.com/watch?v={video_data['video_id']}\n👤 Orijinal Kanal: {video_data['channel_title']}\n\n⚠️ Bu video eğitim ve analiz amaçlıdır. Fair use kapsamındadır."
        
        print("✅ Senaryo oluşturuldu")
        print(f"📺 Başlık: {script['title']}")
        print(f"🎬 Hook: {script['hook']}")
        print(f"🔢 Kelime Sayısı: {script['word_count']}")
        
        # Tam senaryoyu yazdır
        print("\n📝 TAM SENARYO:")
        for scene in script['scenes']:
            print(f"[{scene['timing']}s] {scene['text']}")
        
        # Kaydet
        with open(f'{CACHE_DIR}/script.json', 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        return script
        
    except Exception as e:
        print(f"❌ Senaryo oluşturma hatası: {e}")
        raise

if __name__ == '__main__':
    analysis_data = load_analysis()
    generate_script(analysis_data)
