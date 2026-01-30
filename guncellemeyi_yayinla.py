import os
import subprocess
import sys

def yayinla():
    print("🚀 GÜNCELLEME YAYINLAMA SİHİRBAZI 🚀")
    print("---------------------------------------")
    
    aciklama = input("Yapılan değişiklikleri kısaca yazın (Örn: Hata düzeltildi): ")
    if not aciklama:
        aciklama = "Genel Güncelleme"
        
    try:
        # 1. Dosyaları Ekle
        print("1. Dosyalar paketleniyor...")
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. Kaydet (Commit)
        print("2. Versiyon oluşturuluyor...")
        subprocess.run(["git", "commit", "-m", aciklama], check=True)
        
        # 3. Gönder (Push)
        print("3. Sunucuya yükleniyor (GitHub)...")
        subprocess.run(["git", "push"], check=True)
        
        print("\n✅ BAŞARILI! Güncelleme yayınlandı.")
        print("Diğer bilgisayarlarda 'Güncellemeleri Kontrol Et' butonuna basarak bu sürümü alabilirsiniz.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ HATA OLUŞTU: {e}")
        print("İnternet bağlantınızı veya Git ayarlarınızı kontrol edin.")
    except Exception as e:
        print(f"\n❌ BEKLENMEYEN HATA: {e}")

if __name__ == "__main__":
    yayinla()
    input("\nÇıkmak için Enter'a basın...")
