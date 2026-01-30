import os
import math
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QListWidget, QListWidgetItem, 
                             QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QGridLayout, 
                             QDialog, QFileDialog, QButtonGroup)
from PyQt6.QtGui import (QPixmap, QDrag, QPainter, QPen, QBrush, QFont, QCursor, QPainterPath, QColor)
from PyQt6.QtCore import (Qt, QMimeData, QPoint, QRectF, QPropertyAnimation, QEasingCurve, 
                          QTimer, QRect, QPointF, QLineF)

from yapilandirma import (KART_SIZE, SAHA_EN, SAHA_BOY, RENK_CIM_KOYU, RENK_CIM_ACIK, 
                                    RENK_CIZGI, RENK_KOCAELI_YESIL, RENK_KOCAELI_SIYAH)

# --- 1. SÜRÜKLENEBİLİR LİSTE ---
class SuruklenebilirListe(QListWidget):
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return
        dosya_adi = item.data(Qt.ItemDataRole.UserRole)
        mime_data = QMimeData()
        mime_data.setText(dosya_adi)
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        pixmap = QPixmap(140, 30)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.white)
        txt = item.text()
        if len(txt) > 15: txt = txt[:12] + "..."
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, txt)
        painter.end()
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.CopyAction)

# --- 2. OYUNCU KARTI (NUMARASIZ) ---
class OyuncuToken(QLabel):
    def __init__(self, dosya_adi, resim_yolu, parent=None):
        super().__init__(parent)
        self.dosya_adi = dosya_adi
        self.ekran_ismi = os.path.splitext(dosya_adi)[0].replace("_", " ").title()
        self.setFixedSize(KART_SIZE + 40, KART_SIZE + 40) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        
        self.pixmap_data = QPixmap()
        self.resim_var = False
        if os.path.exists(resim_yolu):
            loaded = self.pixmap_data.load(resim_yolu)
            if loaded: self.resim_var = True

        # SİLME BUTONU
        self.btn_sil = QPushButton("x", self)
        self.btn_sil.setGeometry(KART_SIZE + 10, 0, 18, 18) 
        self.btn_sil.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_sil.setStyleSheet("background-color: #d32f2f; color: white; border-radius: 9px; font-weight: bold; border: 1px solid white; font-size:10px;")
        self.btn_sil.clicked.connect(self.sil_beni)
        self.btn_sil.show()
        self.show()

    def sil_beni(self):
        self.deleteLater()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        draw_size = float(KART_SIZE)
        draw_x = (self.width() - draw_size) / 2
        draw_y = 15.0 
        center_rect = QRectF(draw_x, draw_y, draw_size, draw_size)
        
        # 1. GÖRSEL
        if self.resim_var and not self.pixmap_data.isNull():
            path = QPainterPath()
            path.addEllipse(center_rect)
            painter.setClipPath(path)
            painter.drawPixmap(center_rect.toRect(), self.pixmap_data.scaled(center_rect.toRect().size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            painter.setClipping(False)
            painter.setPen(QPen(RENK_KOCAELI_YESIL, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center_rect)
        else:
            painter.setBrush(QBrush(RENK_KOCAELI_SIYAH))
            painter.setPen(QPen(RENK_KOCAELI_YESIL, 2))
            painter.drawEllipse(center_rect)
            initials = self.ekran_ismi[:2].upper()
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(center_rect, Qt.AlignmentFlag.AlignCenter, initials)

        # 2. İSİM (Outline - Sade)
        font = QFont("Segoe UI", 10, QFont.Weight.Black)
        painter.setFont(font)
        parcalar = self.ekran_ismi.split(" ")
        gosterilecek_isim = parcalar[0]
        if len(gosterilecek_isim) < 3 and len(parcalar) > 1: gosterilecek_isim = parcalar[1] 
            
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(gosterilecek_isim)
        text_x = (self.width() - text_width) / 2
        text_y = draw_y + draw_size + 18 
        
        path = QPainterPath()
        path.addText(text_x, text_y, font, gosterilecek_isim)
        painter.setPen(QPen(Qt.GlobalColor.black, 3, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton): return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.dosya_adi)
        drag.setMimeData(mime)
        pix = self.grab()
        drag.setPixmap(pix)
        drag.setHotSpot(event.position().toPoint())
        drag.exec(Qt.DropAction.MoveAction)

# --- 3. SAHA ---
class TaktikSaha(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(SAHA_EN, SAHA_BOY)
        self.current_tool = "move"
        self.drawing = False
        self.start_point = QPoint()
        self.drawings = [] 
        
        # Logo Yükleme
        self.logo_pixmap = QPixmap()
        # Not: Dinamik dosya yolu, __file__ kullanarak scriptin yanındaki klasöre bakar.
        try:
            # TODO: Burasi onemli, logo nereden gelecek? 
            # Simdilik bir ust klasor varsayimi
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_yolu = os.path.join(base_dir, "OYUNCULARIMIZ", "logo.png") # Ana klasordeki OYUNCULARIMIZ
            if os.path.exists(logo_yolu):
                self.logo_pixmap.load(logo_yolu)
        except:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Çim
        stripe_h = int(self.height() / 14) 
        for i in range(15):
            color = RENK_CIM_KOYU if i % 2 == 0 else RENK_CIM_ACIK
            painter.fillRect(0, i * stripe_h, self.width(), stripe_h, color)

        # ORTA SAHA LOGOSU
        center_rect = QRect(int(self.width()/2 - 100), int(self.height()/2 - 100), 200, 200)
        painter.setOpacity(0.2) 
        if not self.logo_pixmap.isNull():
            painter.drawPixmap(center_rect, self.logo_pixmap.scaled(center_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("Arial", 80, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "KS")
        painter.setOpacity(1.0)

        # Çizgiler
        painter.setPen(QPen(RENK_CIZGI, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        margin = 25
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.drawRect(rect)
        center_y = int(rect.center().y())
        painter.drawLine(rect.left(), center_y, rect.right(), center_y) 
        center_point = QPointF(float(rect.center().x()), float(rect.center().y()))
        painter.drawEllipse(center_point, 60, 60) 
        
        box_w, box_h = 240, 100 
        center_x = int(rect.center().x())
        painter.drawRect(int(center_x - box_w/2), rect.top(), box_w, box_h)
        painter.drawRect(int(center_x - box_w/2), rect.bottom() - box_h, box_w, box_h)
        
        goal_w = 100
        painter.fillRect(int(center_x - goal_w/2), rect.top() - 5, goal_w, 5, QColor(255,255,255,180))
        painter.fillRect(int(center_x - goal_w/2), rect.bottom(), goal_w, 5, QColor(255,255,255,180))

        for tool, start, end in self.drawings:
            self.draw_tactical_shape(painter, tool, start, end)
        if self.drawing:
            self.draw_tactical_shape(painter, self.current_tool, self.start_point, self.mapFromGlobal(self.cursor().pos()))

    def draw_tactical_shape(self, painter, tool, start, end):
        painter.setPen(QPen(Qt.GlobalColor.yellow, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        if tool == "arrow": self.draw_arrow(painter, start, end)
        elif tool == "dashed": 
            painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))
            painter.drawLine(start, end)

    def draw_arrow(self, painter, start, end):
        painter.drawLine(start, end)
        line = QLineF(QPointF(start), QPointF(end))
        angle = math.atan2(-line.dy(), line.dx())
        arrow_size = 18
        p1 = QPointF(end.x() + math.sin(angle - math.pi / 3) * arrow_size, end.y() + math.cos(angle - math.pi / 3) * arrow_size)
        p2 = QPointF(end.x() + math.sin(angle - math.pi + math.pi / 3) * arrow_size, end.y() + math.cos(angle - math.pi + math.pi / 3) * arrow_size)
        painter.drawPolygon([QPointF(end), p1, p2])

    def mousePressEvent(self, event):
        if self.current_tool != "move":
            self.drawing = True
            self.start_point = event.position().toPoint()
        else: super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing: self.update()
        else: super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
            end_point = event.position().toPoint()
            self.drawings.append((self.current_tool, self.start_point, end_point))
            self.update()
        else: super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event): 
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dropEvent(self, event):
        try:
            pos = event.position().toPoint()
            dosya = event.mimeData().text()
            if not dosya: return 
            source = event.source()
            offset = QPoint(int((KART_SIZE+30)/2), int((KART_SIZE+40)/2))
            if isinstance(source, OyuncuToken): source.move(pos - offset)
            else: self.parent().sahaya_oyuncu_koy(dosya, pos - offset)
            event.acceptProposedAction()
        except: pass

    def uygula_formasyon(self, tip):
        w = self.width()
        h = self.height()
        koordinatlar = {
            "4-2-3-1": [(0.5, 0.9), (0.15, 0.75), (0.38, 0.75), (0.62, 0.75), (0.85, 0.75), (0.35, 0.55), (0.65, 0.55), (0.15, 0.35), (0.5, 0.35), (0.85, 0.35), (0.5, 0.15)],
            "4-4-2": [(0.5, 0.9), (0.15, 0.75), (0.38, 0.75), (0.62, 0.75), (0.85, 0.75), (0.15, 0.45), (0.38, 0.45), (0.62, 0.45), (0.85, 0.45), (0.35, 0.20), (0.65, 0.20)],
            "4-3-3": [(0.5, 0.9), (0.15, 0.75), (0.38, 0.75), (0.62, 0.75), (0.85, 0.75), (0.3, 0.55), (0.5, 0.60), (0.7, 0.55), (0.15, 0.25), (0.5, 0.15), (0.85, 0.25)]
        }
        if tip not in koordinatlar: return
        pozisyonlar = koordinatlar[tip]
        sahadaki_oyuncular = self.findChildren(OyuncuToken)
        for i, token in enumerate(sahadaki_oyuncular):
            if i >= len(pozisyonlar): break
            px = int(pozisyonlar[i][0] * w) - int(token.width()/2)
            py = int(pozisyonlar[i][1] * h) - int(token.height()/2)
            anim = QPropertyAnimation(token, b"pos")
            anim.setDuration(600)
            anim.setStartValue(token.pos())
            anim.setEndValue(QPoint(px, py))
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            anim.start()
            token.anim = anim 

# --- 4. ANA PENCERE (YENİLENMİŞ) ---
class TaktikTahtasi(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kocaelispor Teknik Direktör v7.1")
        self.setFixedSize(880, 750)
        self.setStyleSheet("background-color: #121212; color: white; font-family: Segoe UI;")
        
        # Dizin ayarlaması
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Eğer paketleme modunda değilse ve main.py seviyesindeyse
        # OYUNCULARIMIZ klasörü Kocaelispor_App'in dışında olabilir mi?
        # Kullanıcının dosya yapısına göre:
        # Desktop/Kocaelispor Uygulaması/Kocaelispor_App/OYUNCULARIMIZ (Klasörde bu var)
        # Ama biz Kocaelispor_App/ui/taktik_tahtasi.py 'dayız.
        # Yani ../../Oyunclarimiz değil ../OYUNCULARIMIZ
        # main.py ile aynı seviyede olduğu için:
        self.resim_klasoru = os.path.join(base_dir, "OYUNCULARIMIZ")
        
        main_layout = QHBoxLayout(self)
        self.saha = TaktikSaha(self)
        main_layout.addWidget(self.saha)

        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background: #1e1e1e; border-left: 1px solid #333;")
        sl = QVBoxLayout(sidebar)
        
        sl.addWidget(QLabel("OTOMATİK DİZİLİŞ", styleSheet="color:#008f58; font-weight:bold; font-size:12px;"))
        self.combo_formasyon = QComboBox()
        self.combo_formasyon.addItems(["Diziliş Seç...", "4-2-3-1", "4-4-2", "4-3-3"])
        self.combo_formasyon.setStyleSheet("QComboBox { background: #333; padding: 5px; border-radius: 4px; color: white; }")
        self.combo_formasyon.currentTextChanged.connect(self.formasyon_degistir)
        sl.addWidget(self.combo_formasyon)
        sl.addSpacing(10)
        
        sl.addWidget(QLabel("ÇİZİM ARAÇLARI", styleSheet="color:#008f58; font-weight:bold; font-size:12px;"))
        grid_tools = QGridLayout()
        self.btn_move = self.create_tool_btn("✋ Taşı", "move")
        self.btn_run = self.create_tool_btn("↗️ Ok", "arrow")
        self.btn_pass = self.create_tool_btn("--- Pas", "dashed")
        btn_clear = QPushButton("Temizle")
        btn_clear.clicked.connect(self.clear_drawings)
        btn_clear.setStyleSheet("background:#d32f2f; padding:8px; border-radius:4px; font-weight:bold; font-size:11px;")

        grid_tools.addWidget(self.btn_move, 0, 0)
        grid_tools.addWidget(self.btn_run, 0, 1)
        grid_tools.addWidget(self.btn_pass, 1, 0)
        grid_tools.addWidget(btn_clear, 1, 1)
        sl.addLayout(grid_tools)
        
        sl.addWidget(QLabel("OYUNCU LİSTESİ", styleSheet="margin-top:15px; color:#AAA; font-weight:bold; font-size:12px;"))
        self.liste = SuruklenebilirListe()
        self.liste.setDragEnabled(True)
        self.liste.setStyleSheet("QListWidget{background:#121212; border:1px solid #333; border-radius:5px;} QListWidget::item{padding:6px; border-bottom:1px solid #222;} QListWidget::item:hover{background:#008f58;}")
        self.yukle_oyuncular()
        sl.addWidget(self.liste)
        
        btn_save = QPushButton("💾 KAYDET")
        btn_save.setStyleSheet("background:#008f58; color:white; font-weight:bold; padding:12px; border-radius:5px; margin-top:10px;")
        btn_save.clicked.connect(self.kaydet)
        sl.addWidget(btn_save)
        
        main_layout.addWidget(sidebar)
        self.tool_group = QButtonGroup(self)
        self.tool_group.addButton(self.btn_move)
        self.tool_group.addButton(self.btn_run)
        self.tool_group.addButton(self.btn_pass)
        self.btn_move.setChecked(True)
        QTimer.singleShot(500, self.ilk_kurulum)

    def ilk_kurulum(self):
        if not os.path.exists(self.resim_klasoru): return
        tum_dosyalar = sorted([f for f in os.listdir(self.resim_klasoru) if f.lower().endswith(('.png', '.jpg'))])
        # İlk 11 kişiyi sahaya at
        for i in range(min(11, len(tum_dosyalar))):
            self.sahaya_oyuncu_koy(tum_dosyalar[i], QPoint(0,0))
        # Otomatik 4-2-3-1'e geç
        self.saha.uygula_formasyon("4-2-3-1")

    def create_tool_btn(self, text, tool):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.set_tool(tool))
        btn.setStyleSheet("QPushButton { background: #333; padding: 8px; border-radius: 4px; font-weight:bold; color: white; font-size:11px;} QPushButton:checked { background: #008f58; border: 1px solid white; }")
        return btn

    def set_tool(self, tool_name):
        self.saha.current_tool = tool_name
        self.saha.drawing = False

    def clear_drawings(self):
        self.saha.drawings = []
        self.saha.update()
        
    def formasyon_degistir(self, text):
        if text != "Diziliş Seç...": self.saha.uygula_formasyon(text)

    def yukle_oyuncular(self):
        self.liste.clear()
        if os.path.exists(self.resim_klasoru):
            dosyalar = [f for f in os.listdir(self.resim_klasoru) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for d in sorted(dosyalar):
                item = QListWidgetItem(os.path.splitext(d)[0].replace("_", " ").title())
                item.setData(Qt.ItemDataRole.UserRole, d)
                self.liste.addItem(item)

    def sahaya_oyuncu_koy(self, dosya, pos):
        yol = os.path.join(self.resim_klasoru, dosya)
        if not os.path.exists(yol):
            for f in os.listdir(self.resim_klasoru):
                if f.lower() == dosya.lower(): yol = os.path.join(self.resim_klasoru, f); break
        p = OyuncuToken(dosya, yol, self.saha)
        p.move(pos)
        p.show()

    def kaydet(self):
        f, _ = QFileDialog.getSaveFileName(self, "Kaydet", "Kadro.png", "PNG (*.png)")
        if f: self.saha.grab().save(f)
