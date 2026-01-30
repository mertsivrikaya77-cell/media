from PyQt6.QtGui import QColor

# Google Sheets CSV Linki
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOGDv0ZQb-tEQr72SoST9RCi5Gme0NDd9FeJ9CtvvSPIjFaXqRxhlC_IfpApgZQVKXTjWMO9T8VR6n/pub?output=csv" 

# Ayiklama Islemi için API
PASTEBIN_API_KEY = "$2a$10$yJxWoEHK.70N.cx4FOpVMevfwmNwc0uLCpNtfivMY3W7WOeVtVZmC"
PASTEBIN_BIN_ID  = "69677a14ae596e708fdbbe2c"

# Taktik Tahtası Ayarları
KART_SIZE = 60  
SAHA_EN = 520   
SAHA_BOY = 720  

# Renk Paleti
# Not: QColor kullanıldığı için UI dosyalarında import edilecek
RENK_CIM_KOYU = QColor("#1b5e20") 
RENK_CIM_ACIK = QColor("#2e7d32") 
RENK_CIZGI = QColor(255, 255, 255, 230)
RENK_KOCAELI_YESIL = QColor("#006837")
RENK_KOCAELI_SIYAH = QColor("#000000")

# CSS Stilleri
APP_STYLE = """
    QMainWindow { 
        background-color: #000000; 
    }
    QWidget { 
        font-family: 'Segoe UI', sans-serif; 
    }
    QFrame#GreenBox { 
        background-color: #004d33; 
        border-radius: 12px; 
    }
    QLabel { 
        color: #00A86B; 
    }
    QLabel#Logo { 
        font-size: 42px; 
        font-weight: 900; 
        letter-spacing: -1px; 
        color: #008f58; 
    }
    QLabel#Pill { 
        background-color: #004d33; 
        color: white; 
        padding: 8px 15px; 
        border-radius: 15px; 
        font-weight: bold; 
        font-size: 14px;
    }
    QLabel#SectionTitle { 
        background-color: black; 
        color: #00A86B; 
        padding: 5px 10px; 
        font-weight: bold; 
        font-size: 15px; 
        border-radius: 6px; 
    }
    QLabel#MonitorPlaceholder { 
        color: #555; 
        font-size: 16px; 
        border: 2px dashed #333; 
        border-radius: 10px; 
        background-color: #0a0a0a; 
    }
    QLabel#MatchHeader { 
        color: white; 
        font-size: 36px; 
        font-weight: 900; 
    }
    QPushButton { 
        background-color: #004d33; 
        color: #00A86B; 
        border-radius: 10px; 
        padding: 15px; 
        font-weight: bold; 
        font-size: 15px; 
        text-align: center; 
    }
    QPushButton:hover { 
        background-color: #006644; 
        color: white; 
    }
    QPushButton#StartBtn { 
        background-color: #222; 
        color: #555; 
        font-weight: 900; 
        font-size: 26px; 
        border-radius: 30px; 
    }
    QPushButton#StartBtn:enabled { 
        background-color: #006644; 
        color: black; 
    }
    QPushButton#SocialBtn { 
        color: white; 
        font-weight: bold; 
        border-radius: 12px; 
        font-size: 14px; 
    }
    QPushButton#XBtn { 
        background-color: #000; 
        color: #E7E9EA; 
        border: 2px solid #333; 
    }
    QProgressBar { 
        border: 2px solid #00A86B; 
        border-radius: 5px; 
        text-align: center; 
        color: white; 
        background-color: #222; 
    }
    QProgressBar::chunk { 
        background-color: #00A86B; 
    }
"""
