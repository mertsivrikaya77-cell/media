import os
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class GuncellemeYoneticisi(QThread):
    durum_sinyali = pyqtSignal(str)
    hata_sinyali = pyqtSignal(str)
    bitis_sinyali = pyqtSignal(bool) # True: Güncellendi, False: Güncel/Yok

    def __init__(self, mode="kontrol"):
        super().__init__()
        # 1. Öncelik: Belgelerim/Kocaelispor_Data (Uygulama Modu)
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents", "Kocaelispor_Data")
        if os.path.exists(os.path.join(docs_dir, ".git")):
            self.repo_dir = docs_dir
        else:
            # 2. Öncelik: Geliştirici Modu (Dosya konumu)
            self.repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.mode = mode  # "kontrol" veya "guncelle"

    def run(self):
        if self.mode == "kontrol":
            self._kontrol_et()
        elif self.mode == "guncelle":
            self._guncelle()

    def _kontrol_et(self):
        try:
            # 1. Uzak sunucu kontrolü
            check_remote = subprocess.run(["git", "remote"], capture_output=True, text=True, cwd=self.repo_dir)
            if not check_remote.stdout.strip():
                self.hata_sinyali.emit("Güncelleme sunucusu tanımlı değil.")
                return

            self.durum_sinyali.emit("Sunucu kontrol ediliyor...")
            subprocess.run(["git", "fetch"], check=True, cwd=self.repo_dir)

            local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=self.repo_dir).strip()
            remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"], text=True, cwd=self.repo_dir).strip()

            if local_hash == remote_hash:
                self.durum_sinyali.emit("Sistem Güncel")
                self.bitis_sinyali.emit(False)
            else:
                self.durum_sinyali.emit("Yeni Sürüm Mevcut")
                self.bitis_sinyali.emit(True)

        except Exception as e:
            self.hata_sinyali.emit(f"Hata: {str(e)}")

    def _guncelle(self):
        try:
            self.durum_sinyali.emit("Güncellemeler indiriliyor...")
            subprocess.run(["git", "pull"], check=True, cwd=self.repo_dir)
            self.durum_sinyali.emit("Güncelleme Başarılı!")
            self.bitis_sinyali.emit(True)
        except Exception as e:
            self.hata_sinyali.emit(f"Güncelleme Hatası: {str(e)}")
