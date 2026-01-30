from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QHeaderView, QTableWidgetItem, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from cekirdek.api import programi_getir

class ProgramPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Haftalık Antrenman Programı (ONLINE)")
        self.setFixedSize(1100, 600)
        self.setStyleSheet("QDialog { background-color: #121212; } QLabel { color: #E0E0E0; font-family: 'Segoe UI'; } QTableWidget { background-color: #1A1A1A; gridline-color: #333; color: #DDD; font-size: 13px; border: 1px solid #333; } QHeaderView::section { background-color: #004d33; color: white; padding: 5px; border: 1px solid #333; font-weight: bold; } QTableWidget::item { padding: 5px; } QPushButton { background-color: #333; color: white; padding: 8px; border-radius: 5px; }")
        l = QVBoxLayout(self); h = QHBoxLayout()
        h.addWidget(QLabel("🟢 HAFTALIK PROGRAM (CANLI)", styleSheet="font-size:18px;font-weight:900;color:#00A86B;")); h.addStretch()
        h.addWidget(QLabel("SELÇUK İNAN - TEKNİK DİREKTÖR", styleSheet="font-size:12px;font-weight:bold;color:#FFD700;background:#333;padding:5px;border-radius:4px;")); l.addLayout(h)
        self.table = QTableWidget(); ONLINE = programi_getir(); self.table.setColumnCount(len(ONLINE)); self.table.setRowCount(8)
        self.table.setHorizontalHeaderLabels([f"{d['gun']}\n{d['tarih']}" for d in ONLINE])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.table.verticalHeader().setVisible(False)
        for c, d in enumerate(ONLINE):
            for r, a in enumerate(d['akis']):
                if r < 8:
                    it = QTableWidgetItem(a)
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if "ANTRENMAN" in a.upper(): it.setBackground(QColor("#FF6F61")); it.setForeground(QColor("black")); it.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                    elif "İZİN" in a.upper() or "OFF" in a.upper(): it.setBackground(QColor("#4CAF50")); it.setForeground(QColor("white")); it.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    elif "MAÇ" in a.upper(): it.setBackground(QColor("#6495ED")); it.setForeground(QColor("white")); it.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                    elif "KAHVALTI" in a.upper() or "YEMEK" in a.upper(): it.setBackground(QColor("#E0E0E0")); it.setForeground(QColor("black"))
                    self.table.setItem(r, c, it)
        l.addWidget(self.table); b = QPushButton("Kapat"); b.clicked.connect(self.close); l.addWidget(b)
