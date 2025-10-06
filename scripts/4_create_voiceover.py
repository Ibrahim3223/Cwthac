#!/usr/bin/env python3
"""
Senaryo için Azure TTS ile sesli anlatım oluşturur
"""

import os
import json
import azure.cognitiveservices.speech as speechsdk

# Konfigürasyon
CACHE_DIR = 'data/cache'
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', 'westeurope')

def load_script():
    """Senaryoyu yükle"""
    with open(f'{CACHE_DIR}/script.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_voiceover_azure(script):
    """Azure Speech Service ile profesyonel İngilizce sesli anlatım"""
    
    print("🎙️ Azure TTS ile sesli anlatım oluşturuluyor...")
    
    # Full script text
    full_text = " ".join([scene['text'] for scene in script['scenes']])
    
    # Azure Speech configuration
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    
    # English voice (Male)
    # Alternatives:
    # - en-US-GuyNeural (Male, natural, conversational)
    # - en-US-JennyNeural (Female, friendly)
    # - en-GB-RyanNeural (British Male)
    # - en-US-DavisNeural (Male, energetic)
    speech_config.speech_synthesis_voice_name = 'en-US-GuyNeural'
    
    # Ses kalitesi ayarları
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    
    # Çıktı dosyası
    output_path = f'{CACHE_DIR}/voiceover.mp3'
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    
    # Speech synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    # SSML with advanced control (optional)
    ssml_text = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-GuyNeural">
            <prosody rate="1.1" pitch="+5%">
                {full_text}
            </prosody>
        </voice>
    </speak>
    """
    
    try:
        print(f"🔊 Sentezleniyor: {len(full_text)} karakter...")
        
        # SSML ile sentez
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        # Sonuç kontrolü
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"✅ Sesli anlatım kaydedildi: {output_path}")
            
            # Metadata kaydet
            with open(f'{CACHE_DIR}/voiceover_info.json', 'w') as f:
                json.dump({
                    'path': output_path,
                    'method': 'azure_tts',
                    'voice': 'en-US-GuyNeural',
                    'region': AZURE_SPEECH_REGION,
                    'text_length': len(full_text)
                }, f, indent=2)
            
            return output_path
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ Sentez iptal edildi: {cancellation_details.reason}")
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"❌ Hata detayı: {cancellation_details.error_details}")
            
            raise Exception(f"Azure TTS hatası: {cancellation_details.reason}")
        
    except Exception as e:
        print(f"❌ Azure TTS hatası: {e}")
        raise

def get_available_voices():
    """Kullanılabilir İngilizce sesleri listele (debug için)"""
    
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    result = synthesizer.get_voices_async("en-US").get()
    
    print("\n🎤 Available English Voices:")
    for voice in result.voices:
        print(f"- {voice.short_name} ({voice.gender}): {voice.local_name}")

if __name__ == '__main__':
    # Debug modda sesleri listele
    if os.getenv('DEBUG_VOICES') == 'true':
        get_available_voices()
    else:
        script = load_script()
        voiceover_path = create_voiceover_azure(script)
        print(f"\n🎉 Voiceover hazır: {voiceover_path}")
