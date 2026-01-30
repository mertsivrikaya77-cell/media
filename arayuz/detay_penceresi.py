from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, 
                             QWidget, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QFont, QDesktopServices, QCursor
from araclar import tarih_tr, get_current_time
from veri.fikstur import FIKSTUR
from veri.oyuncular import KADRO_DATA

class RakipAnalizPenceresi(QDialog):
    def __init__(self, m):
        super().__init__(); self.setWindowTitle(f"Scouting: {m['rakip']}"); self.setFixedSize(500, 480); self.setStyleSheet("QDialog{background:#121212;border:2px solid #00A86B;} QLabel{color:#E0E0E0;} QLabel#TeamName{color:#00A86B;font-size:28px;font-weight:900;} QFrame#InfoBox{background:#1E1E1E;border-radius:8px;padding:10px;} QPushButton{background:#004d33;color:white;padding:10px;border-radius:8px;font-weight:bold;}")
        l = QVBoxLayout(self); l.setSpacing(12); l.setContentsMargins(30,30,30,30)
        lbl = QLabel(m['rakip']); lbl.setObjectName("TeamName"); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(lbl)
        l.addWidget(QLabel(f"📅 {tarih_tr(m['tarih'])} | {m['tarih'].strftime('%H:%M')}"))
        l.addWidget(QLabel(f"🏟️ {m['stat']}"))
        f = QFrame(); f.setObjectName("InfoBox"); fl = QVBoxLayout(f); fl.addWidget(QLabel(f"📺 YAYIN: {m['tv']}")); fl.addWidget(QLabel(f"👕 BİZİM FORMA: {m['forma']}")); l.addWidget(f)
        l.addWidget(QLabel("📝 RAKİP NOTU:")); t = QLabel(m.get('analiz','Veri yok')); t.setWordWrap(True); t.setStyleSheet("background:#1A1A1A;padding:10px;border-radius:8px;border-left:4px solid #00A86B;"); l.addWidget(t); l.addStretch(); b = QPushButton("KAPAT"); b.clicked.connect(self.close); l.addWidget(b)

class DetayPenceresi(QDialog):
    def __init__(self, baslik, veri_tipi):
        super().__init__(); self.setWindowTitle(baslik); self.setMinimumSize(600, 600)
        self.setStyleSheet("QDialog{background:#000;} QLabel#Title{color:#00A86B;font-size:24px;font-weight:bold;border-bottom:2px solid #333;padding:15px;} QListWidget{background:transparent;border:none;} QListWidget::item{background:#1A1A1A;margin-bottom:12px;border-radius:8px;border-left:5px solid #00A86B;padding:15px;} QListWidget::item:hover{background:#252525;} QPushButton#TweetCard{background:#16181C;color:#E7E9EA;border:1px solid #333;padding:15px;border-radius:12px;text-align:left;font-weight:bold;} QPushButton#TweetCard:hover{background:#1D1F23;border-color:#00A86B;color:#FFFFFF;}")
        l = QVBoxLayout(self); t = QLabel(baslik); t.setObjectName("Title"); t.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(t)
        if veri_tipi == "XTARIHCE":
            now = get_current_time(); l.addWidget(QLabel(f"📅 BUGÜN: {tarih_tr(now).split(',')[0]}\nAşağıdaki kartlara tıklayarak o yılın arşivine gidebilirsiniz:", styleSheet="color:#71767B;font-size:14px;margin-bottom:10px;padding:0 10px;font-weight:bold;", wordWrap=True))
            sa = QScrollArea(); sa.setWidgetResizable(True); sa.setStyleSheet("background:transparent;border:none;"); sw = QWidget(); sl = QVBoxLayout(sw); sl.setSpacing(15)
            for i in range(1, 11): 
                y = now.year - i; u = f"https://x.com/search?q=from:Kocaelispor since:{y}-{now.month:02d}-{now.day:02d} until:{y}-{now.month:02d}-{now.day+1:02d}&src=typed_query"
                b = QPushButton(f"📅 {i} YIL ÖNCE BUGÜN ({y})\n🔎 Kocaelispor Paylaşımlarını Göster"); b.setObjectName("TweetCard"); b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)); b.setFont(QFont("Segoe UI", 14)); b.clicked.connect(lambda ch, x=u: QDesktopServices.openUrl(QUrl(x))); sl.addWidget(b)
            sl.addStretch(); sw.setLayout(sl); sa.setWidget(sw); l.addWidget(sa)
        else:
            self.lst = QListWidget(); self.lst.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if veri_tipi == "FIKSTUR": self.lst.itemClicked.connect(self.mac_detay_ac)
            l.addWidget(self.lst); self.doldur(veri_tipi)
            
    def doldur(self, tip):
        now = get_current_time()
        if tip == "FIKSTUR":
            for m in FIKSTUR:
                if m["tarih"] > now:
                    it = QListWidgetItem(); it.setData(Qt.ItemDataRole.UserRole, m); bg = "#FFD700" if "Fenerbahçe" in m['rakip'] or "Galatasaray" in m['rakip'] or "Beşiktaş" in m['rakip'] else "#FFFFFF"
                    it.setSizeHint(QSize(0, 130)); self.lst.addItem(it); self.lst.setItemWidget(it, QLabel(f"<div style='padding:5px;'><div style='font-size:18px;font-weight:bold;color:{bg};'>{m['rakip']}</div><div style='font-size:14px;color:#AAA;margin-top:4px;'>🏆 {m['turnuva']}</div><div style='font-size:14px;color:#DDD;margin-top:2px;'>📅 {tarih_tr(m['tarih'])}</div><div style='font-size:14px;font-weight:bold;color:#00A86B;margin-top:6px;'>⏳ {(m['tarih']-now).days} gün kaldı</div><div style='font-size:12px;color:#666;margin-top:5px;font-style:italic;'>👉 Detay ve Analiz için Tıkla</div></div>", textFormat=Qt.TextFormat.RichText, styleSheet="background:transparent;", wordWrap=True))
        elif tip == "DOGUMGUNU":
            s = sorted([{"ad":p["ad"],"rem":(p["dt"].replace(year=now.year) if p["dt"].replace(year=now.year).date()>=now.date() else p["dt"].replace(year=now.year+1)).date()-now.date(),"dt":p["dt"]} for p in KADRO_DATA], key=lambda x:x["rem"].days)
            for p in s:
                st = "<span style='color:#FF5555'>BUGÜN! 🎉</span>" if p["rem"].days == 0 else f"{p['rem'].days} gün kaldı"
                it = QListWidgetItem(); it.setSizeHint(QSize(0, 100)); self.lst.addItem(it); self.lst.setItemWidget(it, QLabel(f"<div style='padding:5px;'><div style='font-size:18px;font-weight:bold;color:#FFF;'>🎂 {p['ad']}</div><div style='font-size:14px;color:#AAA;'>{tarih_tr(p['dt'].replace(year=now.year)).split(',')[0]}</div><div style='font-size:14px;color:#CCC;margin-top:5px;'>{st}</div></div>", textFormat=Qt.TextFormat.RichText, styleSheet="background:transparent;"))
                
    def mac_detay_ac(self, item):
        m = item.data(Qt.ItemDataRole.UserRole)
        if m: RakipAnalizPenceresi(m).exec()
