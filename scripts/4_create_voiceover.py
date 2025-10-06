#!/usr/bin/env python3
"""
Senaryo için TTS ile sesli anlatım oluşturur
"""

import os
import json

# Konfigürasyon
CACHE_DIR = 'data/cache'
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', 'westeurope')

def load_script():
    """Senaryoyu yükle"""
    with open(f'{CACHE_DIR}/script.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_voiceover_gtts(script):
    """Google TTS ile sesli anlatım (fallback)"""
    
    print("🎙️ Google TTS ile sesli anlatım oluşturuluyor...")
    
    try:
        from gtts import gTTS
    except ImportError:
        print("❌ gTTS yüklü değil, yükleniyor...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'gtts'])
        from gtts import gTTS
    
    # Full script text
    full_text = " ".join([scene['text'] for scene in script['scenes']])
    
    try:
        # English TTS
        tts = gTTS(text=full_text, lang='en', slow=False)
        output_path = f'{CACHE_DIR}/voiceover.mp3'
        tts.save(output_path)
        
        print(f"✅ Sesli anlatım kaydedildi: {output_path}")
        
        # Metadata kaydet
        with open(f'{CACHE_DIR}/voiceover_info.json', 'w') as f:
            json.dump({
                'path': output_path,
                'method': 'google_tts',
                'language': 'en',
                'text_length': len(full_text)
            }, f, indent=2)
        
        return output_path
        
    except Exception as e:
        print(f"❌ Google TTS hatası: {e}")
        raise

def create_voiceover_azure(script):
    """Azure Speech Service ile profesyonel İngilizce sesli anlatım"""
    
    print("🎙️ Azure TTS deneniyor...")
    
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        print("⚠️ Azure SDK yüklü değil, Google TTS kullanılacak")
        return None
    
    if not AZURE_SPEECH_KEY:
        print("⚠️ Azure key eksik, Google TTS kullanılacak")
        return None
    
    # Full script text
    full_text = " ".join([scene['text'] for scene in script['scenes']])
    
    try:
        # Azure Speech configuration
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
        
        speech_config.speech_synthesis_voice_name = 'en-US-GuyNeural'
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        
        output_path = f'{CACHE_DIR}/voiceover.mp3'
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="en-US-GuyNeural">
                <prosody rate="1.1" pitch="+5%">
                    {full_text}
                </prosody>
            </voice>
        </speak>
        """
        
        print(f"🔊 Sentezleniyor: {len(full_text)} karakter...")
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"✅ Azure TTS başarılı: {output_path}")
            
            with open(f'{CACHE_DIR}/voiceover_info.json', 'w') as f:
                json.dump({
                    'path': output_path,
                    'method': 'azure_tts',
                    'voice': 'en-US-GuyNeural',
                    'region': AZURE_SPEECH_REGION,
                    'text_length': len(full_text)
                }, f, indent=2)
            
            return output_path
        else:
            print(f"⚠️ Azure TTS başarısız, Google TTS'e geçiliyor")
            return None
            
    except Exception as e:
        print(f"⚠️ Azure TTS hatası: {e}")
        print("📢 Google TTS'e geçiliyor...")
        return None

def create_voiceover(script):
    """Ana TTS fonksiyonu - önce Azure dene, sonra Google TTS"""
    
    # Önce Azure dene
    if AZURE_SPEECH_KEY:
        result = create_voiceover_azure(script)
        if result:
            return result
    
    # Azure başarısız olduysa veya key yoksa Google TTS kullan
    return create_voiceover_gtts(script)

if __name__ == '__main__':
    script = load_script()
    voiceover_path = create_voiceover(script)
    print(f"\n🎉 Voiceover hazır: {voiceover_path}")
