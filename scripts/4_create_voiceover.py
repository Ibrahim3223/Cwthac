#!/usr/bin/env python3
"""
Senaryo için sesli anlatım oluşturur (TTS)
"""

import os
import json
from elevenlabs import generate, set_api_key, Voice, VoiceSettings

# Alternatif: Google TTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Konfigürasyon
CACHE_DIR = 'data/cache'
ELEVENLABS_KEY = os.getenv('ELEVENLABS_API_KEY')

def load_script():
    """Senaryoyu yükle"""
    with open(f'{CACHE_DIR}/script.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_voiceover_elevenlabs(script):
    """ElevenLabs ile profesyonel sesli anlatım"""
    
    print("🎙️ ElevenLabs ile sesli anlatım oluşturuluyor...")
    
    # Full script text
    full_text = " ".join([scene['text'] for scene in script['scenes']])
    
    try:
        set_api_key(ELEVENLABS_KEY)
        
        # Türkçe destekleyen ses (örnek: Adam veya özel ses)
        audio = generate(
            text=full_text,
            voice=Voice(
                voice_id="pNInz6obpgDQGcFmaJgB",  # Adam (multilingual)
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            ),
            model="eleven_multilingual_v2"
        )
        
        # Kaydet
        output_path = f'{CACHE_DIR}/voiceover.mp3'
        with open(output_path, 'wb') as f:
            f.write(audio)
        
        print(f"✅ Sesli anlatım kaydedildi: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"⚠️ ElevenLabs hatası: {e}")
        print("📢 Google TTS'e geçiliyor...")
        return create_voiceover_gtts(script)

def create_voiceover_gtts(script):
    """Google TTS ile alternatif sesli anlatım (ücretsiz)"""
    
    if not GTTS_AVAILABLE:
        print("❌ gTTS yüklü değil!")
        raise ImportError("gTTS gerekli!")
    
    print("🎙️ Google TTS ile sesli anlatım oluşturuluyor...")
    
    # Full script text
    full_text = " ".join([scene['text'] for scene in script['scenes']])
    
    try:
        tts = gTTS(text=full_text, lang='tr', slow=False)
        output_path = f'{CACHE_DIR}/voiceover.mp3'
        tts.save(output_path)
        
        print(f"✅ Sesli anlatım kaydedildi: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Google TTS hatası: {e}")
        raise

def create_voiceover(script):
    """Ana TTS fonksiyonu - önce ElevenLabs dene, sonra Google TTS"""
    
    if ELEVENLABS_KEY:
        try:
            return create_voiceover_elevenlabs(script)
        except:
            pass
    
    # Fallback to Google TTS
    return create_voiceover_gtts(script)

if __name__ == '__main__':
    script = load_script()
    voiceover_path = create_voiceover(script)
    
    # Metadata kaydet
    with open(f'{CACHE_DIR}/voiceover_info.json', 'w') as f:
        json.dump({
            'path': voiceover_path,
            'method': 'elevenlabs' if ELEVENLABS_KEY else 'gtts'
        }, f)
