#!/usr/bin/env python3
"""
Final video montajını yapar
"""

import os
import json
import requests
from moviepy.editor import *
from moviepy.video.fx.all import crop
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Konfigürasyon
CACHE_DIR = 'data/cache'
OUTPUT_DIR = 'data/processed'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Video özellikleri (YouTube Shorts)
WIDTH = 1080
HEIGHT = 1920
FPS = 30

def load_data():
    """Gerekli tüm verileri yükle"""
    with open(f'{CACHE_DIR}/script.json', 'r', encoding='utf-8') as f:
        script = json.load(f)
    with open(f'{CACHE_DIR}/selected_video.json', 'r', encoding='utf-8') as f:
        video_data = json.load(f)
    return script, video_data

def download_thumbnail(url, video_id):
    """Orijinal videonun thumbnail'ini indir"""
    print("🖼️ Thumbnail indiriliyor...")
    
    thumb_path = f'{CACHE_DIR}/thumb_{video_id}.jpg'
    response = requests.get(url)
    
    with open(thumb_path, 'wb') as f:
        f.write(response.content)
    
    return thumb_path

def create_text_clip(text, duration, fontsize=60, color='white', bg_color='black'):
    """Metin klibi oluştur"""
    
    # PIL ile metin görüntüsü oluştur
    img = Image.new('RGB', (WIDTH, HEIGHT), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Font (default font kullan)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    
    # Metni ortala
    # Word wrap için basit implementasyon
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < WIDTH - 100:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Metni çiz
    y_offset = (HEIGHT - len(lines) * fontsize) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        y = y_offset + i * (fontsize + 20)
        
        # Gölge efekti
        draw.text((x+3, y+3), line, font=font, fill='black')
        draw.text((x, y), line, font=font, fill=color)
    
    # PIL image'i numpy array'e çevir
    img_array = np.array(img)
    
    # ImageClip oluştur
    clip = ImageClip(img_array).set_duration(duration)
    
    return clip

def create_intro_clip(script):
    """Giriş klibi oluştur (hook)"""
    print("🎬 Giriş klibi oluşturuluyor...")
    
    hook_text = script['hook']
    return create_text_clip(hook_text, duration=3, fontsize=70, color='yellow', bg_color='#1a1a1a')

def create_analysis_clips(script, thumbnail_path):
    """Analiz kliplerini oluştur"""
    print("📊 Analiz klipleri oluşturuluyor...")
    
    clips = []
    
    # Thumbnail'i ekle (orijinal videodan)
    thumb = ImageClip(thumbnail_path).set_duration(5).resize((WIDTH, HEIGHT))
    
    # Overlay text: "Bu video neden viral oldu?"
    overlay_text = create_text_clip(
        "Bu video neden viral oldu?",
        duration=5,
        fontsize=80,
        color='white',
        bg_color=(0, 0, 0, 0)  # Transparent
    ).set_position('center')
    
    thumbnail_with_text = CompositeVideoClip([thumb, overlay_text])
    clips.append(thumbnail_with_text)
    
    # Analiz sahne klipleri
    for scene in script['scenes'][1:]:  # İlk sahne hook olduğu için atla
        timing = scene['timing'].split('-')
        duration = int(timing[1]) - int(timing[0])
        
        text_clip = create_text_clip(
            scene['text'],
            duration=duration,
            fontsize=55,
            color='white',
            bg_color='#0f0f0f'
        )
        clips.append(text_clip)
    
    return clips

def add_background_music(video_clip):
    """Arka plan müziği ekle (lisanslı müzik kullan!)"""
    print("🎵 Arka plan müziği ekleniyor...")
    
    # Not: Buraya kendi lisanslı müziğinizi ekleyin
    # Örnek: Epidemic Sound, Artlist, vb.
    
    # Şimdilik sadece voiceover kullanacağız
    voiceover_path = f'{CACHE_DIR}/voiceover.mp3'
    
    if os.path.exists(voiceover_path):
        audio = AudioFileClip(voiceover_path)
        
        # Video süresine uyarla
        if audio.duration > video_clip.duration:
            audio = audio.subclip(0, video_clip.duration)
        
        video_with_audio = video_clip.set_audio(audio)
        return video_with_audio
    
    return video_clip

def create_final_video(script, video_data):
    """Final videoyu oluştur"""
    print("🎥 Final video oluşturuluyor...")
    
    # Thumbnail indir
    thumbnail_path = download_thumbnail(video_data['thumbnail'], video_data['video_id'])
    
    # Intro
    intro = create_intro_clip(script)
    
    # Analiz klipleri
    analysis_clips = create_analysis_clips(script, thumbnail_path)
    
    # Tüm klipleri birleştir
    all_clips = [intro] + analysis_clips
    final_video = concatenate_videoclips(all_clips, method="compose")
    
    # Ses ekle
    final_video = add_background_music(final_video)
    
    # Çıktı dosyası
    output_path = f"{OUTPUT_DIR}/final_video_{video_data['video_id']}.mp4"
    
    # Render
    print("🎬 Video render ediliyor...")
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=f'{CACHE_DIR}/temp-audio.m4a',
        remove_temp=True,
        preset='medium',
        threads=4
    )
    
    print(f"✅ Video oluşturuldu: {output_path}")
    
    # Metadata kaydet
    with open(f'{OUTPUT_DIR}/video_metadata.json', 'w', encoding='utf-8') as f:
        json.dump({
            'output_path': output_path,
            'original_video_id': video_data['video_id'],
            'title': script['title'],
            'description': script['description']
        }, f, ensure_ascii=False, indent=2)
    
    return output_path

if __name__ == '__main__':
    script, video_data = load_data()
    create_final_video(script, video_data)
