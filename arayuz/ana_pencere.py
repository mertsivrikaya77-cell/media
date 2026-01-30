import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QPushButton, QFrame, QProgressBar, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices

from yapilandirma import APP_STYLE
from araclar import get_current_time, tarih_tr
from veri.fikstur import FIKSTUR
from cekirdek.fotograf_ayiklayici import AyiklamaIslemi
from cekirdek.guncelleme_yoneticisi import GuncellemeYoneticisi

# UI Modülleri
from arayuz.program_penceresi import ProgramPenceresi
from arayuz.detay_penceresi import DetayPenceresi
from arayuz.taktik_tahtasi import TaktikTahtasi
from arayuz.sosyal_medya_penceresi import PaylasimTakipPenceresi, MacGunuChecklist

class MediaStaffApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaStaffKS v48.0 - PERFORMANCE EDITION")
        self.setFixedSize(1250, 750)
        self.setStyleSheet(APP_STYLE)
        self.init_ui()
        self.ref_folder = None
        self.src_folder = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui_timer)
        self.timer.start(1000)
        self.update_ui_timer()
        self.output_path = None # Çıktı klasörünü tutmak için değişken


    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.main_layout = QHBoxLayout(cw)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.time_lbl = QLabel("--")
        self.time_lbl.setObjectName("Pill")
        self.time_lbl.setFixedWidth(240)
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_lbl)
        layout.addWidget(QLabel("MediaStaffKS", objectName="Logo"))
        self.br = QPushButton("Referans Görüntülerini Seç")
        self.br.clicked.connect(self.select_ref)
        layout.addWidget(self.br)
        self.bs = QPushButton("Antrenman Veya Maç Görüntülerini Seç")
        self.bs.clicked.connect(self.select_src)
        layout.addWidget(self.bs)
        
        # --- MODEL SEÇİMİ ---
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Hızlı Mod (Optimize - Önerilen)"])
        self.model_combo.setStyleSheet("color: white; background: #333; padding: 5px;")
        layout.addWidget(self.model_combo)
        
        self.bst = QPushButton("BAŞLAT")
        self.bst.setObjectName("StartBtn")
        self.bst.setFixedHeight(70)
        self.bst.clicked.connect(self.start_processing)
        self.bst.setEnabled(False)
        layout.addWidget(self.bst)
        layout.addStretch()
        sl = QHBoxLayout()
        for n, c, l in [("IG","#E1306C","https://www.instagram.com/kocaelispor"),("X","#000","https://twitter.com/Kocaelispor"),("FB","#1877F2","https://www.facebook.com/kocaelispor"),("DR","#0F9D58","https://drive.google.com")]:
            b = QPushButton(n)
            b.setFixedSize(50,50)
            b.setObjectName("SocialBtn")
            b.setStyleSheet(f"background:{c};color:white;border-radius:12px;font-weight:bold;")
            b.clicked.connect(lambda ch, u=l: QDesktopServices.openUrl(QUrl(u)))
            sl.addWidget(b)
        layout.addLayout(sl)
        self.main_layout.addLayout(layout, 25)

    def setup_center_panel(self):
        frame = QFrame()
        frame.setObjectName("GreenBox")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20,20,20,20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(" CANLI AYIKLAMA PANELİ ")
        lbl.setObjectName("SectionTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self.stats_lbl = QLabel("Bekleniyor...")
        self.stats_lbl.setStyleSheet("font-size:16px;color:white;font-weight:bold;padding:10px;background:#000;border-radius:8px;")
        self.stats_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_lbl)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)
        self.log_lbl = QLabel("Sistem Hazır.")
        self.log_lbl.setObjectName("LogText")
        self.log_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.log_lbl)
        layout.addStretch()
        bf = QPushButton("📂 Tamamlandı Klasöre Git")
        bf.setStyleSheet("background:black;color:#00A86B;border:2px solid #00A86B;")
        bf.clicked.connect(self.open_output_folder)
        layout.addWidget(bf)
        self.main_layout.addWidget(frame, 40)

    def setup_right_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Butonlar arası boşluğu minimuma indirdik

        # Butonlar için ortak küçük stil
        btn_style = "QPushButton { padding: 6px; font-size: 12px; }"

        # --- 1. ONLINE PAYLAŞIM ÇETELESİ ---
        btn_online = QPushButton(" ✅  ONLİNE PAYLAŞIM ÇETELESİ")
        btn_online.setStyleSheet("background:#222; color:#00A86B; border:2px dashed #00A86B; padding: 8px; font-weight: bold; font-size: 12px;")
        btn_online.clicked.connect(lambda: PaylasimTakipPenceresi().exec())
        btn_online.clicked.connect(lambda: PaylasimTakipPenceresi().exec())
        layout.addWidget(btn_online)

        # --- GÜNCELLEME BUTONU ---
        self.btn_update = QPushButton(" 🔄  GÜNCELLEMELERİ KONTROL ET")
        self.btn_update.setStyleSheet("background:#0056b3; color:white; border:1px solid #FFF; padding: 8px; font-weight: bold; font-size: 11px;")
        self.btn_update.clicked.connect(self.check_updates)
        layout.addWidget(self.btn_update)

        # --- DİĞER MODÜL BUTONLARI ---
        for text, slot in [
            (" 🎂  Doğum Günleri", lambda: DetayPenceresi("Doğum Günleri", "DOGUMGUNU").exec()),
            (" 🗓️  Fikstür & Analiz", lambda: DetayPenceresi("Maç Fikstürü", "FIKSTUR").exec()),
            (" 🟢  Taktik Tahtası", lambda: TaktikTahtasi().exec()),
            (" Tarihte Bugün X", lambda: DetayPenceresi("X'te Tarihte Bugün", "XTARIHCE").exec())
        ]:
            b = QPushButton(text)
            b.setStyleSheet(btn_style)
            b.clicked.connect(slot)
            layout.addWidget(b)

        # --- HAFTALIK PROGRAM ---
        bpr = QPushButton(" 📅  Haftalık Program (CANLI)")
        bpr.setStyleSheet("background:#FFD700; color:black; border:1px solid #FFF; padding:6px; font-size:12px; font-weight:bold;")
        bpr.clicked.connect(lambda: ProgramPenceresi().exec())
        layout.addWidget(bpr)

        # --- 2. MAÇ GÜNÜ ÇETELESİ (GERİ GELDİ) ---
        btn_c = QPushButton(" ✅  Maç Günü Çetelesi")
        btn_c.setStyleSheet("background:#222; color:#00A86B; border:2px dashed #00A86B; padding:6px; font-size:12px;")
        btn_c.clicked.connect(lambda: MacGunuChecklist().exec()) # .exec() kullanıldı
        layout.addWidget(btn_c)

        layout.addStretch()

        # --- SIRADAKİ MAÇ BLOĞU ---
        nf = QFrame()
        nf.setObjectName("GreenBox")
        nf.setFixedHeight(200) # Yüksekliği 200'e çekerek tam sığdırdık
        nl = QVBoxLayout(nf)
        nl.setContentsMargins(5, 5, 5, 5)
        nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nt = QLabel(" SIRADAKİ MAÇ ")
        nt.setObjectName("SectionTitle")
        nl.addWidget(nt)
        
        self.mh = QLabel("Trabzonspor (E)")
        self.mh.setObjectName("MatchHeader")
        self.mh.setStyleSheet("font-size: 24px; font-weight: 900;")
        nl.addWidget(self.mh)
        
        self.md = QLabel("SÜPER LİG\n18 Ocak 2026")
        self.md.setStyleSheet("color:#DDD; font-size:13px;")
        nl.addWidget(self.md)
        
        self.cnt = QLabel("00G 00:00:00")
        self.cnt.setStyleSheet("color:#FFF; font-size:28px; font-weight:900;")
        nl.addWidget(self.cnt)
        
        layout.addWidget(nf)
        self.main_layout.addLayout(layout, 35)

    def update_ui_timer(self):
        now = get_current_time()
        self.time_lbl.setText(f"{now.strftime('%H:%M')} | {tarih_tr(now).split(',')[0]}")
        u = [m for m in FIKSTUR if m["tarih"] > now]
        if u:
            c = u[0]
            r = c["tarih"] - now
            t = int(r.total_seconds())
            d = t // 86400
            h = (t % 86400) // 3600
            m = (t % 3600) // 60
            s = t % 60
            self.mh.setText(c['rakip'])
            self.md.setText(f"{c['turnuva']}\n{tarih_tr(c['tarih'])}")
            self.cnt.setText(f"{d}G {h:02}:{m:02}:{s:02}")
        else:
            self.mh.setText("Sezon Sonu")
            self.md.setText("-")
            self.cnt.setText("--:--")

    def select_ref(self): 
        d = QFileDialog.getExistingDirectory(self, "Referans Klasörü")
        if d: 
            self.ref_folder = d
            self.br.setText(f"✅ {os.path.basename(d)}")
            self.br.setStyleSheet("background:black;border:2px solid #00A86B;color:#00A86B;")
            self.check_ready()

    def select_src(self): 
        d = QFileDialog.getExistingDirectory(self, "Kaynak Klasör")
        if d: 
            self.src_folder = d
            self.bs.setText(f"✅ {os.path.basename(d)}")
            self.bs.setStyleSheet("background:black;border:2px solid #00A86B;color:#00A86B;")
            self.check_ready()

    def check_ready(self): 
        if self.ref_folder and self.src_folder: 
            self.bst.setEnabled(True)

    def start_processing(self): 
        self.bst.setEnabled(False)
        self.log_lbl.setText("Analiz Başlatılıyor...")
        
        # Model seçimi
        selected_text = self.model_combo.currentText()
        model_type = "cnn" if "CNN" in selected_text else "hog"
        
        self.worker = AyiklamaIslemi(self.ref_folder, self.src_folder, model_type)
        self.worker.log_sinyali.connect(self.log_lbl.setText)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.bitis_sinyali.connect(self.finished)
        self.worker.start()
    
    def update_progress(self, total, remaining, success, mixed):
        processed = total - remaining
        percent = int((processed / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.stats_lbl.setText(f"Toplam: {total} | Kalan: {remaining}\n✅: {success} | ⚠️: {mixed}")

    def finished(self, msg, path): 
        self.bst.setEnabled(True)
        self.output_path = path
        QMessageBox.information(self, "Durum", msg)
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_output_folder(self):
        if self.output_path and os.path.exists(self.output_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_path))
        else:
            # Yedek: Eğer henüz işlem yapılmadıysa veya path yoksa Desktop'taki varsayılan yere bakmaya çalış (opsiyonel)
            # Şimdilik kullanıcıya uyarı vermiyoruz veya sessiz kalıyoruz
            # Şimdilik kullanıcıya uyarı vermiyoruz veya sessiz kalıyoruz
            pass

    # --- GÜNCELLEME SİSTEMİ ---
    def check_updates(self):
        self.btn_update.setEnabled(False)
        self.btn_update.setText("Kontrol Ediliyor...")
        
        self.update_worker = GuncellemeYoneticisi(mode="kontrol")
        self.update_worker.durum_sinyali.connect(lambda msg: self.log_lbl.setText(msg))
        self.update_worker.hata_sinyali.connect(lambda msg: QMessageBox.warning(self, "Hata", msg))
        self.update_worker.bitis_sinyali.connect(self.on_update_check_finished)
        self.update_worker.start()

    def on_update_check_finished(self, update_available):
        self.btn_update.setEnabled(True)
        self.btn_update.setText(" 🔄  GÜNCELLEMELERİ KONTROL ET")
        
        if update_available:
            reply = QMessageBox.question(self, "Güncelleme", "Yeni bir sürüm mevcut! İndirmek ister misiniz?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.start_update()
        else:
             QMessageBox.information(self, "Bilgi", "Uygulamanız zaten son sürüm.")

    def start_update(self):
        self.update_worker = GuncellemeYoneticisi(mode="guncelle")
        self.update_worker.durum_sinyali.connect(lambda msg: self.log_lbl.setText(msg))
        self.update_worker.hata_sinyali.connect(lambda msg: QMessageBox.critical(self, "Hata", msg))
        self.update_worker.bitis_sinyali.connect(lambda success: QMessageBox.information(self, "Tamamlandı", "Güncelleme Başarılı!\nLütfen uygulamayı yeniden başlatın."))
        self.update_worker.start()
