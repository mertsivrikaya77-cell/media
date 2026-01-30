import sys
import os
import re
from datetime import datetime

def resource_path(relative_path):
    """ Dosya yollarını paketlenmiş uygulama (.app) içinde bulur """
    try:
        # PyInstaller dosyaları buraya açar
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_current_time():
    return datetime.now()

def tarih_tr(dt):
    aylar = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran', 
             7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
    gunler = {0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba', 3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'}
    return f"{dt.day} {aylar[dt.month]} {dt.year}, {gunler[dt.weekday()]}"

def normalize_name(text):
    text = re.sub(r'[_\d]+$', '', text)
    replacements = {'İ': 'i', 'I': 'i', 'ı': 'i', 'Ğ': 'g', 'ğ': 'g', 'Ü': 'u', 'ü': 'u', 'Ş': 's', 'ş': 's', 'Ö': 'o', 'ö': 'o', 'Ç': 'c', 'ç': 'c'}
    text = text.lower()
    for src, target in replacements.items(): 
        text = text.replace(src, target)
    return text.title()
