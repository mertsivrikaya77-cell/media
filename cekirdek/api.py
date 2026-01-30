import requests
import csv
from yapilandirma import SHEET_URL

def programi_getir():
    default_program = [{"gun": "Hata", "tarih": "-", "akis": ["İnternet Yok veya Link Girilmedi"]}]
    if "BURAYA" in SHEET_URL or len(SHEET_URL) < 10: 
        return [{"gun": "Link Eksik", "tarih": "-", "akis": ["Lütfen koda Google Sheets CSV linkini ekleyin."]}]
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        response.encoding = 'utf-8'
        cr = csv.reader(response.text.splitlines(), delimiter=',')
        yeni_program = []
        rows = list(cr)
        for row in rows:
            if len(row) >= 3:
                gun = row[0].strip()
                tarih = row[1].strip()
                akis_ham = row[2].replace('\n', ',') 
                akis = [x.strip() for x in akis_ham.split(',') if x.strip()]
                yeni_program.append({"gun": gun, "tarih": tarih, "akis": akis})
        return yeni_program if len(yeni_program) > 0 else default_program
    except Exception as e:
        print(f"Hata: {e}")
        return default_program
