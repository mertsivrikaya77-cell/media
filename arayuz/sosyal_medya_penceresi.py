import requests
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
                             QPushButton, QCalendarWidget, QTextEdit, QLineEdit, 
                             QMessageBox, QProgressBar, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QCursor, QTextCharFormat, QColor
from araclar import tarih_tr
from veri.oyuncular import KADRO_DATA
from yapilandirma import PASTEBIN_API_KEY, PASTEBIN_BIN_ID

class MacGunuChecklist(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maç Günü Paylaşım Takibi")
        self.setFixedSize(400, 450)
        self.setStyleSheet("QDialog{background:#121212;border:2px solid #00A86B;} QCheckBox{color:#E0E0E0;font-size:16px;font-weight:bold;padding:10px;spacing:15px;} QCheckBox::indicator{width:24px;height:24px;border:2px solid #555;border-radius:6px;background:#222;} QCheckBox::indicator:checked{background-color:#00A86B;border-color:#00A86B;} QCheckBox:hover{background-color:#1A1A1A;border-radius:8px;} QLabel{color:#00A86B;font-size:20px;font-weight:900;margin-bottom:15px;border-bottom:1px solid #333;padding-bottom:10px;} QPushButton{background:#333;color:white;padding:12px;border-radius:8px;font-weight:bold;margin-top:10px;}")
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("✅ PAYLAŞIM LİSTESİ", alignment=Qt.AlignmentFlag.AlignCenter))
        items = ["👕 Formamız (Renk/Kombin)", "⛅ Hava Durumu & Zemin", "🏟️ Stad Hazır Görüntüsü", "🔒 Soyunma Odası", "🚌 Takım Otobüsü Geliş", "1️⃣1️⃣ İlk 11 Kadrosu"]
        for i in items: 
            cb = QCheckBox(i)
            cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            layout.addWidget(cb)
        layout.addStretch()
        btn = QPushButton("Pencereyi Gizle")
        btn.clicked.connect(self.hide)
        layout.addWidget(btn)

class PaylasimTakipPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kocaelispor Medya - Günlük Admin Notları")
        self.setFixedSize(1050, 780)
        
        self.API_KEY = PASTEBIN_API_KEY
        self.BIN_ID  = PASTEBIN_BIN_ID
        self.BASE_URL = f"https://api.jsonbin.io/v3/b/{self.BIN_ID}"
        self.HEADERS = {"Content-Type": "application/json", "X-Master-Key": self.API_KEY}
        
        self.history = {} 
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        
        self.init_ui()
        QTimer.singleShot(200, self.load_from_cloud)
        
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.load_from_cloud)
        self.sync_timer.start(8000)

    def init_ui(self):
        self.setStyleSheet("QDialog { background-color: #0c0c0c; color: white; }")
        main_layout = QHBoxLayout(self)
        
        # SOL PANEL
        left = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.date_changed)
        left.addWidget(self.calendar)
        
        left.addWidget(QLabel("📝 GÜNLÜK ADMİN NOTLARI", styleSheet="color:#00A86B; font-weight:bold; margin-top:10px;"))
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background:#111; color:#0f9; border:1px solid #333; border-radius:10px;")
        left.addWidget(self.chat_area)
        
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Not yaz ve Enter'a bas...")
        self.msg_input.returnPressed.connect(self.send_message)
        left.addWidget(self.msg_input)

        # İDMAN DURUMU
        self.workout_status = QLabel("⚪ Veri Bekleniyor...")
        self.workout_status.setStyleSheet("font-weight:bold; font-size:13px; padding:8px; border-radius:5px; background:#1a1a1a; margin-top:5px;")
        left.addWidget(self.workout_status)

        # TEMİZLE BUTONU
        self.clear_btn = QPushButton("🗑️ Seçili Günü Temizle")
        self.clear_btn.setStyleSheet("background-color: #330000; color: #ff4444; border: 1px solid #ff4444; padding: 5px; border-radius: 5px; font-weight: bold; margin-top: 5px;")
        self.clear_btn.clicked.connect(self.clear_day_data)
        left.addWidget(self.clear_btn)
        
        self.status_lbl = QLabel("🟢 Sistem Çevrimiçi")
        left.addWidget(self.status_lbl)
        main_layout.addLayout(left, 40)
        
        # SAĞ PANEL (OYUNCULAR)
        right = QVBoxLayout()
        self.date_header = QLabel(tarih_tr(datetime.now()), styleSheet="font-size: 24px; font-weight: 900;")
        right.addWidget(self.date_header)
        self.pbar = QProgressBar(); self.pbar.setRange(0, 8); right.addWidget(self.pbar)
        self.player_list = QListWidget()
        self.populate_oyuncular()
        self.player_list.itemClicked.connect(self.save_to_cloud)
        right.addWidget(self.player_list)
        main_layout.addLayout(right, 60)

    def clear_day_data(self):
        # Onay kutusu
        reply = QMessageBox.question(self, 'Veri Silme', f"{self.selected_date} verileri silinecek. Emin misiniz?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.sync_timer.stop()
                note_key = f"notes_{self.selected_date}"
                if self.selected_date in self.history: del self.history[self.selected_date]
                if note_key in self.history: del self.history[note_key]
                requests.put(self.BASE_URL, json={"record": self.history}, headers=self.HEADERS, timeout=5)
                self.update_ui()
                self.status_lbl.setText("🗑️ Gün Temizlendi")
            except: pass
            self.sync_timer.start(8000)

    def update_ui(self):
        self.player_list.blockSignals(True)
        # Takvim Boyama
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        active_fmt = QTextCharFormat(); active_fmt.setBackground(QColor("#004d26")); active_fmt.setForeground(QColor("white")); active_fmt.setFontWeight(700)
        for key in self.history.keys():
            d_str = key.replace("notes_", "")
            if len(d_str) == 10 and len(self.history.get(key, [])) > 0:
                self.calendar.setDateTextFormat(QDate.fromString(d_str, "yyyy-MM-dd"), active_fmt)

        # Durum ve Veriler
        shared = self.history.get(self.selected_date, [])
        note_key = f"notes_{self.selected_date}"
        has_notes = len(self.history.get(note_key, [])) > 0
        if len(shared) > 0 or has_notes:
            self.workout_status.setText("🟢 İDMAN YAPILDI"); self.workout_status.setStyleSheet("color:#0f9; background:#002b16; padding:8px; border-radius:5px;")
        else:
            self.workout_status.setText("🔴 İDMAN YOKTUR"); self.workout_status.setStyleSheet("color:#f44; background:#2b0000; padding:8px; border-radius:5px;")

        for i in range(self.player_list.count()):
            it = self.player_list.item(i); it.setCheckState(Qt.CheckState.Checked if it.text() in shared else Qt.CheckState.Unchecked)
        self.pbar.setValue(len(shared))
        self.chat_area.setPlainText("\n".join(self.history.get(note_key, [])))
        self.player_list.blockSignals(False)

    def send_message(self):
        txt = self.msg_input.text().strip()
        if not txt: return
        self.sync_timer.stop()
        try:
            r = requests.get(self.BASE_URL, headers=self.HEADERS, timeout=5)
            if r.status_code == 200:
                data = r.json().get("record", {})
                self.history = data.get("record", data) if isinstance(data.get("record"), dict) else data
            admin_name = os.environ.get('USER', 'Admin')
            new_msg = f"[{datetime.now().strftime('%H:%M')}] {admin_name}: {txt}"
            note_key = f"notes_{self.selected_date}"
            notes = self.history.get(note_key, [])
            notes.append(new_msg); self.history[note_key] = notes
            requests.put(self.BASE_URL, json={"record": self.history}, headers=self.HEADERS, timeout=5)
            self.msg_input.clear(); self.update_ui()
        except: pass
        self.sync_timer.start(8000)

    def save_to_cloud(self):
        shared = [self.player_list.item(i).text() for i in range(self.player_list.count()) if self.player_list.item(i).checkState() == Qt.CheckState.Checked]
        self.history[self.selected_date] = shared
        try: requests.put(self.BASE_URL, json={"record": self.history}, headers=self.HEADERS, timeout=5); self.update_ui()
        except: pass

    def load_from_cloud(self):
        if self.msg_input.hasFocus(): return
        try:
            r = requests.get(self.BASE_URL, headers=self.HEADERS, timeout=5)
            if r.status_code == 200:
                data = r.json().get("record", {})
                self.history = data.get("record", data) if isinstance(data.get("record"), dict) else data
                self.update_ui()
        except: pass

    def date_changed(self):
        qdate = self.calendar.selectedDate(); self.selected_date = qdate.toString("yyyy-MM-dd")
        self.date_header.setText(tarih_tr(datetime(qdate.year(), qdate.month(), qdate.day()))); self.update_ui()

    def populate_oyuncular(self):
        self.player_list.clear()
        for p in sorted([p['ad'] for p in KADRO_DATA]):
            it = QListWidgetItem(p); it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable); it.setCheckState(Qt.CheckState.Unchecked); self.player_list.addItem(it)
