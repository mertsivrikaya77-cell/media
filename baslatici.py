import os
import sys
import subprocess
import time
from PyQt6.QtWidgets import QApplication, QMessageBox

# Konfigürasyon
REPO_URL = "https://github.com/mertsivrikaya77-cell/media"
LOCAL_DIR_NAME = "Kocaelispor_Data"
DOCUMENTS_DIR = os.path.join(os.path.expanduser("~"), "Documents")
TARGET_DIR = os.path.join(DOCUMENTS_DIR, LOCAL_DIR_NAME)

def main():
    app = QApplication(sys.argv)
    
    # 1. Klasör Kontrolü
    if not os.path.exists(TARGET_DIR):
        # İlk açılış: İndirme (Clone)
        msg = QMessageBox()
        msg.setWindowTitle("Kurulum")
        msg.setText("Uygulama verileri ilk kez indiriliyor...\nBu işlem internet hızına göre sürebilir.")
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()
        QApplication.processEvents()
        
        try:
            subprocess.run(["git", "clone", REPO_URL, TARGET_DIR], check=True)
            msg.close()
        except Exception as e:
            msg.close()
            QMessageBox.critical(None, "Hata", f"Veriler indirilemedi:\n{e}")
            return

    # 2. Güncelleme Kontrolü (Opsiyonel - her açılışta hızlıca kontrol etsin mi?)
    # Şimdilik uygulamanın içindeki butona bırakıyoruz, açılışı yavaşlatmasın.

    # 3. Yolu Tanımla ve Başlat
    if TARGET_DIR not in sys.path:
        sys.path.insert(0, TARGET_DIR)
    
    try:
        # Dinamik Import
        import baslat
        # baslat.py içindeki ana fonksiyonu veya akışı çalıştır
        # baslat.py şu an main blokta çalışıyor, onu bir fonksiyona çevirmek daha temiz olurdu ama
        # import edildiğinde __main__ bloğu çalışmaz. 
        # Bu yüzden baslat.py'ye ufak bir 'run()' fonksiyonu eklememiz gerekebilir veya
        # direkt window'u buradan çağırabiliriz.
        
        from arayuz.ana_pencere import MediaStaffApp
        
        # baslat.py içindeki QApplication çakışmasını önlemek için:
        # Zaten burada bir app yarattık.
        window = MediaStaffApp()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(None, "Kritik Hata", f"Uygulama başlatılamadı:\n{e}\n\nYol: {TARGET_DIR}")

if __name__ == "__main__":
    main()
