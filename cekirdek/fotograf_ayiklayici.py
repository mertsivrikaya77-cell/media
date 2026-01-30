import os
import shutil
import time
import re
import pickle
import math
import multiprocessing
import traceback
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyQt6.QtCore import QThread, pyqtSignal

# 3rd Party
try:
    import face_recognition
    import numpy as np
    from PIL import Image
    FACE_LIB_AVAILABLE = True
except ImportError:
    FACE_LIB_AVAILABLE = False
    print("UYARI: face_recognition veya numpy eksik. Ayıklama çalışmayabilir.")

def process_single_image(args):
    """
    Tek bir resim için yüz tanıma işlemi yapar.
    Multiprocessing için bu fonksiyon class dışında (global scopeta) olmalı.
    
    Args:
        args: (file_path, output_base, mixed_base, known_encs, known_names, model_type) tuple'ı
    Returns:
        (status, name/result_msg, file_path)
    """
    
    def apply_gamma(image_np, gamma=1.5):
        """Karanlık yüzler için Gamma düzeltmesi uygular (Aydınlatma)"""
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")
        return table[image_np]

    file_path, output_base, mixed_base, known_encs, known_names, model_type = args
    filename = os.path.basename(file_path)

    try:
        # Resmi bir kez yükle
        raw_img = face_recognition.load_image_file(file_path)
        h, w, _ = raw_img.shape

        def run_scan(limit, upsample_times):
            """
            Verilen limit ve upsample parametreleri ile tarama yapar.
            Başarılı olursa (SUCCESS, name, path) döner.
            Başarısız olursa None döner.
            """
            scale = 1.0
            scan_img = raw_img

            # 1. Resize (Limit varsa)
            if limit and (w > limit or h > limit):
                scale = min(limit/w, limit/h)
                new_w, new_h = int(w*scale), int(h*scale)
                img_pil = Image.fromarray(raw_img)
                img_resized = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
                scan_img = np.array(img_resized)
            
            # 2. Gamma Correction (HOG için iptal edildi - Hız ve Doğruluk için)
            detect_img = scan_img
            # if model_type == "hog":
            #     detect_img = apply_gamma(scan_img, gamma=1.5)

            # 3. Yüz Bulma
            # number_of_times_to_upsample: Küçük yüzleri bulmak için resmi büyütür (HOG için)
            face_locs = face_recognition.face_locations(detect_img, model=model_type, number_of_times_to_upsample=upsample_times)
            
            if not face_locs:
                return None

            # 4. Koordinat Dönüştürme
            if scale != 1.0:
                actual_locs = [(int(t/scale), int(r/scale), int(b/scale), int(l/scale)) for t, r, b, l in face_locs]
            else:
                actual_locs = face_locs

            # 5. Merkeze En Yakın Yüzü Seçme
            orig_h, orig_w, _ = raw_img.shape
            yuz_listesi = []
            for loc in actual_locs:
                top, right, bottom, left = loc
                f_x, f_y = (left + right) / 2, (top + bottom) / 2
                dist = math.sqrt((orig_w/2 - f_x)**2 + (orig_h/2 - f_y)**2)
                yuz_listesi.append((dist, loc))
            
            yuz_listesi.sort(key=lambda x: x[0])
            target_loc = yuz_listesi[0][1]

            # 6. Kodlama ve Eşleştirme
            # Hız için num_jitters=1 yapıldı (Eski: 5)
            target_enc_list = face_recognition.face_encodings(raw_img, known_face_locations=[target_loc], num_jitters=1)
            
            if target_enc_list:
                target_enc = target_enc_list[0]
                distances = face_recognition.face_distance(known_encs, target_enc)

                if len(distances) > 0 and np.min(distances) < 0.6:
                    best_idx = np.argmin(distances)
                    name = known_names[best_idx]
                    
                    kaleciler = ["GOKHAN", "TALHA", "SERHAT", "JOVA", "ALEKSANDAR", "DEĞİRMENCİ"]
                    is_kaleci = any(k in name.upper() for k in kaleciler)
                    target_dir = "KALECILER" if is_kaleci else name
                    
                    p_folder = os.path.join(output_base, target_dir)
                    os.makedirs(p_folder, exist_ok=True)
                    shutil.copy2(file_path, os.path.join(p_folder, filename))
                    return ("SUCCESS", name, file_path)
            
            return None

        # --- 1. TUR: HIZLI TARAMA (Limitli, Upsample 1) ---
        # HOG için 1000px, CNN için 3000px (Hız Optimize)
        fast_limit = 1000 if model_type == "hog" else 3000
        result = run_scan(limit=fast_limit, upsample_times=1)
        
        if result:
            return result

        # --- 2. TUR: DETAYLI TARAMA (Deep Scan) ---
        # Eğer HOG ise ve Hızlı Tur "Karışık" dediyse, bir daha dene
        # Bu sefer Resize YOK (Orjinal Boyut) ve Upsample 2 (Daha dikkatli bak)
        if model_type == "hog":
            # Deep Scan: 2000px Limit (Yeterli detay, hızlı)
            deep_scan_result = run_scan(limit=2000, upsample_times=1)
            if deep_scan_result:
                # İkinci denemede buldu!
                # deep_scan_result artık ("SUCCESS", name, path) formatında
                # Ancak kullanıcı bunu "Deep Scan ile bulundu" diye bilmek ister mi? Şimdilik normal success dönelim.
                 # Belki loga (Deep Scan) eklenebilir ama return formatı sabit kalmalı.
                return deep_scan_result

        # Her iki turda da bulunamadı
        shutil.copy2(file_path, os.path.join(mixed_base, filename))
        return ("MIXED", "Karışık", file_path)

    except Exception as e:
        # Hata durumunda da karışığa at ki işlem durmasın
        try:
            shutil.copy2(file_path, os.path.join(mixed_base, filename))
        except: pass
        return ("ERROR", str(e), file_path)

class AyiklamaIslemi(QThread):
    log_sinyali = pyqtSignal(str) 
    progress_signal = pyqtSignal(int, int, int, int) 
    bitis_sinyali = pyqtSignal(str, str)

    def __init__(self, ref_folder, source_folder, model_type="hog"):
        super().__init__()
        self.ref_folder = ref_folder
        self.source_folder = source_folder
        self.model_type = model_type

    def run(self):
        if not FACE_LIB_AVAILABLE:
            self.bitis_sinyali.emit("HATA: face_recognition kütüphanesi eksik.", "")
            return

        try:
            # --- 1. TÜRKÇE TARİH FORMATI AYARI ---
            aylar = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                     7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
            simdi = datetime.now()
            gun = simdi.day
            ay_ismi = aylar[simdi.month]
            tarih_klasoru = f"{gun} {ay_ismi}" # Örn: "22 Ocak"
            
            self.log_sinyali.emit(f"🚀 İşlem Başladı: {tarih_klasoru} klasörü oluşturuluyor...")
            
            # Worker sayısı belirle
            max_workers = None
            if self.model_type == "cnn":
                max_workers = 1  # CNN çok ağır olduğu için tek çekirdek
                self.log_sinyali.emit(f"🐢 Hassas Mod (CNN) Aktif: Güvenli Mod (Tek Çekirdek)")
            else:
                # SİSTEM DONMASINI ENGELLEMEK İÇİN LİMİT
                total_cores = multiprocessing.cpu_count()
                # En az 2 çekirdeği sisteme bırak (Donma riskine karşı hız artışı)
                safe_workers = max(1, total_cores - 2)
                # Max limiti 6'ya çıkar (RAM kullanımı 3200px limit sayesinde azalacak)
                max_workers = min(safe_workers, 6) 
                
                self.log_sinyali.emit(f"⚡ Optimize Performans Modu (HOG): Sistem güvenliği için {max_workers} çekirdek kullanılıyor (Toplam: {total_cores})")
            
            # --- 2. HAFIZA VE REFERANS TARAMA ---
            cache_file = os.path.join(self.ref_folder, "ref_memory.pkl")
            known_encs, known_names = [], []
            
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    known_encs, known_names = data['encs'], data['names']
            else:
                self.log_sinyali.emit("⏳ Referans yüzler taranıyor (İlk işlem biraz sürebilir)...")
                ref_files = [f for f in os.listdir(self.ref_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                for filename in ref_files:
                    try:
                        raw_name = os.path.splitext(filename)[0]
                        clean_name = re.sub(r'[_ \d]+$', '', raw_name.replace('_', ' ')).strip().title()
                        path = os.path.join(self.ref_folder, filename)
                        
                        img = face_recognition.load_image_file(path)
                        encs = face_recognition.face_encodings(img, num_jitters=10) # Referansta yüksek kalite
                        if encs:
                            known_encs.append(encs[0])
                            known_names.append(clean_name)
                    except: continue
                
                if known_encs:
                    with open(cache_file, 'wb') as f:
                        pickle.dump({'encs': known_encs, 'names': known_names}, f)

            # --- 3. KLASÖR YAPILANDIRMA ---
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            output_base = os.path.join(desktop_path, tarih_klasoru) 
            mixed_base = os.path.join(output_base, "KARISIK")
            os.makedirs(mixed_base, exist_ok=True)

            source_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            total_files = len(source_files)
            success_count, mixed_count, processed_count = 0, 0, 0

            # --- 4. PARALEL İŞLEM DÖNGÜSÜ ---
            # İşlenecek görev listesini hazırla
            tasks = []
            for filename in source_files:
                file_path = os.path.join(self.source_folder, filename)
                tasks.append((file_path, output_base, mixed_base, known_encs, known_names, self.model_type))

            self.log_sinyali.emit(f"📸 Toplam {total_files} fotoğraf analiz edilecek...")

            # ProcessPoolExecutor ile paralel işlem başlat
            # max_workers=None -> CPU çekirdek sayısı kadar process açar
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # submit tasks
                future_to_file = {executor.submit(process_single_image, task): task[0] for task in tasks}

                for future in as_completed(future_to_file):
                    processed_count += 1
                    try:
                        status, result_msg, _ = future.result()
                        
                        if status == "SUCCESS":
                            success_count += 1
                            self.log_sinyali.emit(f"✅ {result_msg}")
                        elif status == "MIXED":
                            mixed_count += 1
                            # Karışık mesajlarını loglarda boğulmamak için her zaman yazmayabiliriz
                            # self.log_sinyali.emit(f"❌ Tanınmadı -> Karışık") 
                        else:
                            mixed_count += 1
                            self.log_sinyali.emit(f"⚠️ Hata: {result_msg}")

                    except Exception as exc:
                        mixed_count += 1
                        self.log_sinyali.emit(f"⚠️ Kritik İşlem Hatası: {str(exc)}")
                    
                    # İlerleme çubuğunu güncelle
                    self.progress_signal.emit(total_files, total_files - processed_count, success_count, mixed_count)

            self.bitis_sinyali.emit(f"🏁 İşlem Tamamlandı! Klasör: Masaüstü/{tarih_klasoru}", output_base)


        except Exception as e:
            traceback.print_exc()
            self.bitis_sinyali.emit(f"GENEL HATA: {str(e)}", "")
