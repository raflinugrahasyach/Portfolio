"""
==============================================================
  IoT Fruit Sorting System  —  PRODUCTION v4  (MANUAL TRIGGER)
==============================================================
  Perubahan dari v3:
  [v4-1]  Manual Trigger: AI HANYA berjalan saat tombol ditekan.
          Endpoint baru: POST /api/capture_and_sort
  [v4-2]  ROI Static Box: Deteksi HANYA dari area 300×300px
          di tengah frame. Objek di luar ROI diabaikan total.
  [v4-3]  Confidence 90%: Threshold naik dari 85% → 90%.
          Di bawah 90% → "Objek Tidak Dikenali", tidak masuk DB.
  [v4-4]  BGR→RGB: Tetap dipertahankan + diterapkan pada ROI crop.
  [v4-5]  Video feed tetap streaming (MJPEG) tapi TIDAK ada auto-
          deteksi. Feed hanya menampilkan ROI box + HUD info.
  [v4-6]  Kalibrasi Slider: tetap berfungsi untuk batas
          Apel Besar vs Apel Sedang berdasarkan area dalam ROI.
  [v4-7]  fruit_data sinkron real-time ke analytics interface & Monitoring.

  Label Model: {0: 'Apel', 1: 'Tomat Masak', 2: 'Tomat Mentah'}

  INSTALL:
    pip install flask opencv-python numpy tensorflow
==============================================================
"""

# ── Standard Library ──────────────────────────────────────────────────────────
import os
import time
import threading
from datetime import datetime, timedelta

# ── Third-party ───────────────────────────────────────────────────────────────
import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

# ── TensorFlow (graceful fallback jika belum install) ─────────────────────────
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model as keras_load_model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow tidak terinstal — mode kontur saja aktif.")

# ==============================================================================
#  FLASK APP
# ==============================================================================
app = Flask(__name__)
app.secret_key = "iot-fruit-sorting-v4-manual-trigger-2026"

# ==============================================================================
#  KONFIGURASI TETAP
# ==============================================================================

MODEL_PATH = "model_buah_v1.h5"

LABELS = {
    0: "Apel",
    1: "Tomat Masak",
    2: "Tomat Mentah",
}

# [v4-2] Ukuran ROI (kotak statis di tengah frame) dalam piksel
ROI_SIZE = 300   # lebar dan tinggi kotak ROI berbentuk persegi

# Warna BGR untuk overlay di video feed
ROI_BOX_COLOR_BGR    = (180, 60, 220)   # ungu (BGR)
ROI_BOX_COLOR_ACTIVE = (0, 230, 80)     # hijau saat scanning berlangsung

BOX_COLORS_BGR = {
    "Apel Besar":   (0,   210,  80),
    "Apel Sedang":  (60,  180,  60),
    "Tomat Masak":  (0,   0,   230),
    "Tomat Mentah": (0,   165, 255),
}

COLORS_HEX = {
    "Apel Besar":   "#FFB800",
    "Apel Sedang":  "#FFB800",
    "Tomat Masak":  "#FF4655",
    "Tomat Mentah": "#66BB6A",
}

FRUIT_STATUS = {
    "Apel Besar":   "MATANG",
    "Apel Sedang":  "MATANG",
    "Tomat Masak":  "MASAK",
    "Tomat Mentah": "MENTAH",
}

FRUIT_SIZE = {
    "Apel Besar":   "BESAR",
    "Apel Sedang":  "SEDANG",
    "Tomat Masak":  "BULAT",
    "Tomat Mentah": "BULAT",
}

LABEL_TO_DB_KEY = {
    "Apel Besar":   "apel_besar",
    "Apel Sedang":  "apel_sedang",
    "Tomat Masak":  "tomat_masak",
    "Tomat Mentah": "tomat_mentah",
}

# ---------- Parameter deteksi ----------
BINARY_THRESHOLD    = 100
MIN_CONTOUR_AREA    = 3000    # px² dalam ROI (lebih kecil karena ROI 300x300)
# [v4-3] Threshold confidence naik ke 90%
MIN_CONFIDENCE      = 0.90
MIN_ROI_BRIGHTNESS  = 40

# ==============================================================================
#  GLOBAL STATE
# ==============================================================================

_lock = threading.Lock()

model: object        = None
model_error_msg: str = ""

# ── Kamera ────────────────────────────────────────────────────────────────────
camera      = None
camera_mode = None

# ── Flag scanning (True selama /api/capture_and_sort sedang diproses) ─────────
# Dipakai oleh video feed untuk menampilkan efek "active" pada ROI box
is_scanning: bool = False

# ── Kalibrasi ─────────────────────────────────────────────────────────────────
calibration_threshold: int = 25000
binary_threshold: int      = BINARY_THRESHOLD
min_roi_brightness: int    = MIN_ROI_BRIGHTNESS

# ── Hasil scan terakhir ───────────────────────────────────────────────────────
last_scan_result: dict = {}
detection_log: list    = []

# ── Database utama ────────────────────────────────────────────────────────────
fruit_data: dict = {
    "apel_besar":   [],
    "apel_sedang":  [],
    "tomat_masak":  [],
    "tomat_mentah": [],
}

# ==============================================================================
#  LOAD MODEL AI
# ==============================================================================

def load_ai_model():
    global model, model_error_msg
    if not TF_AVAILABLE:
        model_error_msg = "TensorFlow tidak terinstal"
        return
    if not os.path.exists(MODEL_PATH):
        model_error_msg = f"File '{MODEL_PATH}' tidak ditemukan"
        print(f"❌  Model tidak ditemukan: {MODEL_PATH}")
        return
    try:
        model = keras_load_model(MODEL_PATH, compile=False)
        dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
        model.predict(dummy, verbose=0)
        print(f"✅  Model '{MODEL_PATH}' dimuat & warm-up selesai.")
    except Exception as exc:
        model_error_msg = str(exc)
        model = None
        print(f"❌  Gagal memuat model: {exc}")


# ==============================================================================
#  HELPER — SIMPAN DETEKSI KE FRUIT_DATA DAN LOG
# ==============================================================================

def save_detection(fruit_label: str, area: int, confidence: float) -> dict:
    """
    Simpan satu event ke fruit_data dan detection_log.
    Kembalikan dict new_detection untuk dikirim ke frontend.
    """
    global last_scan_result, detection_log

    now       = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    time_str  = now.strftime("%H:%M:%S")
    db_key    = LABEL_TO_DB_KEY.get(fruit_label, "apel_besar")
    fruit_id  = now.strftime("%y%m%d") + f"_{len(detection_log) + 1:03d}"

    new_entry = {
        "date":      today_str,
        "count":     1,
        "timestamp": now.isoformat(),
        "image":     f"/static/images/{db_key}.jpg",
    }

    new_detection = {
        "id":         fruit_id,
        "name":       fruit_label.upper(),
        "label":      fruit_label,
        "type":       db_key,
        "size":       FRUIT_SIZE.get(fruit_label, "-"),
        "color":      COLORS_HEX.get(fruit_label, "#FFFFFF"),
        "status":     FRUIT_STATUS.get(fruit_label, "-"),
        "confidence": f"{confidence * 100:.1f}%",
        "conf_raw":   confidence,
        "area":       area,
        "time":       time_str,
        "date":       today_str,
    }

    with _lock:
        fruit_data[db_key].append(new_entry)
        last_scan_result = dict(new_detection)
        detection_log.append(new_detection)
        if len(detection_log) > 50:
            detection_log = detection_log[-50:]

    print(
        f"💾  Tersimpan → {fruit_label} | "
        f"Area={area}px² | Conf={confidence:.2%} | ID={fruit_id}"
    )
    return new_detection


# ==============================================================================
#  HELPER — QUERY DATA
# ==============================================================================

def get_monthly_data(year: int, month: int) -> dict:
    result = {k: 0 for k in fruit_data}
    for ftype, entries in fruit_data.items():
        for e in entries:
            d = datetime.strptime(e["date"], "%Y-%m-%d")
            if d.year == year and d.month == month:
                result[ftype] += e["count"]
    return result


def get_last_30_days_data() -> dict:
    end   = datetime.now()
    start = end - timedelta(days=29)
    daily: dict = {}
    cur = start
    while cur <= end:
        daily[cur.strftime("%Y-%m-%d")] = {"apel": 0, "tomat": 0}
        cur += timedelta(days=1)
    for ftype, entries in fruit_data.items():
        for e in entries:
            if e["date"] in daily:
                if "apel" in ftype:
                    daily[e["date"]]["apel"] += e["count"]
                else:
                    daily[e["date"]]["tomat"] += e["count"]
    return daily


def get_monitoring_counts() -> dict:
    return {
        "tomat_masak":  sum(e["count"] for e in fruit_data["tomat_masak"]),
        "tomat_mentah": sum(e["count"] for e in fruit_data["tomat_mentah"]),
        "apel_sedang":  sum(e["count"] for e in fruit_data["apel_sedang"]),
        "apel_besar":   sum(e["count"] for e in fruit_data["apel_besar"]),
    }


# ==============================================================================
#  HELPER — PREDIKSI AI PADA ROI CROP
#  [v4-1][v4-2][v4-3][v4-4] Semua logic inti ada di sini
# ==============================================================================

def run_ai_on_roi(frame: np.ndarray, roi_x1: int, roi_y1: int,
                  roi_x2: int, roi_y2: int) -> dict:
    """
    [v4-1][v4-2] Jalankan prediksi AI HANYA pada crop ROI.
    [v4-3] Confidence threshold: 90%.
    [v4-4] BGR→RGB sebelum model.predict().

    Return dict:
      success       : bool
      fruit_label   : str | None
      confidence    : float
      area          : int
      reason        : str  (pesan diagnostik)
      saved         : bool
    """
    with _lock:
        cal_thresh  = calibration_threshold
        bin_thresh  = binary_threshold
        roi_bright  = min_roi_brightness
        mdl         = model

    # ── [v4-2] Crop frame ke area ROI saja ───────────────────────────────────
    roi_bgr = frame[roi_y1:roi_y2, roi_x1:roi_x2].copy()

    if roi_bgr.size == 0:
        return {"success": False, "reason": "ROI kosong", "saved": False,
                "fruit_label": None, "confidence": 0.0, "area": 0}

    # ── Cek brightness ROI ────────────────────────────────────────────────────
    roi_gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    roi_mean = float(np.mean(roi_gray))
    if roi_mean < roi_bright:
        return {"success": False,
                "reason": f"ROI terlalu gelap (brightness {roi_mean:.0f} < {roi_bright})",
                "saved": False, "fruit_label": None, "confidence": 0.0, "area": 0}

    # ── Deteksi kontur dalam ROI ──────────────────────────────────────────────
    blur = cv2.GaussianBlur(roi_gray, (7, 7), 0)
    _, thresh = cv2.threshold(blur, bin_thresh, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return {"success": False, "reason": "Tidak ada objek terdeteksi di ROI",
                "saved": False, "fruit_label": None, "confidence": 0.0, "area": 0}

    max_cnt = max(contours, key=cv2.contourArea)
    area    = int(cv2.contourArea(max_cnt))

    if area < MIN_CONTOUR_AREA:
        return {"success": False,
                "reason": f"Objek terlalu kecil (area {area}px² < {MIN_CONTOUR_AREA}px²)",
                "saved": False, "fruit_label": None, "confidence": 0.0, "area": area}

    # ── Prediksi AI (jika model ada) ─────────────────────────────────────────
    label_base: str   = None
    confidence: float = 0.0

    if mdl is not None:
        # [v4-4] BGR→RGB KRUSIAL sebelum masuk model
        roi_rgb  = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
        resized  = cv2.resize(roi_rgb, (224, 224))
        arr      = resized.astype(np.float32) / 255.0
        batch    = np.expand_dims(arr, axis=0)

        preds      = mdl.predict(batch, verbose=0)
        class_idx  = int(np.argmax(preds[0]))
        confidence = float(np.max(preds[0]))
        label_base = LABELS.get(class_idx)
    else:
        return {"success": False, "reason": "Model AI tidak tersedia",
                "saved": False, "fruit_label": None, "confidence": 0.0, "area": area}

    # [v4-3] Confidence threshold 90% — di bawah ini = "Objek Tidak Dikenali"
    if confidence < MIN_CONFIDENCE:
        return {
            "success":     False,
            "reason":      f"Objek Tidak Dikenali — akurasi {confidence*100:.1f}% (minimal {MIN_CONFIDENCE*100:.0f}%)",
            "saved":       False,
            "fruit_label": None,
            "confidence":  confidence,
            "area":        area,
        }

    # ── Kalibrasi ukuran Apel ─────────────────────────────────────────────────
    if label_base == "Apel":
        fruit_label = "Apel Besar" if area >= cal_thresh else "Apel Sedang"
    else:
        fruit_label = label_base  # "Tomat Masak" / "Tomat Mentah"

    # ── Simpan ke database ────────────────────────────────────────────────────
    saved_det = save_detection(fruit_label, area, confidence)

    return {
        "success":     True,
        "reason":      "Berhasil dideteksi dan disimpan",
        "saved":       True,
        "fruit_label": fruit_label,
        "confidence":  confidence,
        "area":        area,
        "detection":   saved_det,
    }


# ==============================================================================
#  [v4-5] GENERATOR FRAME MJPEG — HANYA DISPLAY + ROI BOX, TIDAK AUTO-DETECT
# ==============================================================================

def generate_frames(mode: str = "pengenalan"):
    """
    Generator MJPEG streaming.
    [v4-5] Untuk mode 'sorting': tidak ada auto-deteksi.
           Hanya tampilkan feed + kotak ROI statis + HUD.
    mode='pengenalan' → sama, tanpa ROI box.
    mode='sorting'    → tampilkan ROI box + status scan.
    """
    global camera, camera_mode

    with _lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS,          30)
        camera_mode = mode

    FONT      = cv2.FONT_HERSHEY_SIMPLEX
    FONT_BOLD = cv2.FONT_HERSHEY_DUPLEX

    while True:
        with _lock:
            cam_ref    = camera
            scanning   = is_scanning
            last_res   = dict(last_scan_result)

        if cam_ref is None or not cam_ref.isOpened():
            break

        ok, frame = cam_ref.read()
        if not ok:
            time.sleep(0.05)
            continue

        h, w = frame.shape[:2]
        now  = datetime.now()

        # ── [v4-2] Hitung koordinat ROI statis di tengah frame ───────────────
        cx, cy  = w // 2, h // 2
        half    = ROI_SIZE // 2
        roi_x1  = max(0, cx - half)
        roi_y1  = max(0, cy - half)
        roi_x2  = min(w, cx + half)
        roi_y2  = min(h, cy + half)

        if mode == "sorting":
            # ── Gambar ROI box ────────────────────────────────────────────────
            if scanning:
                # Warna hijau + efek kedip saat aktif scanning
                blink_on = int(now.timestamp() * 6) % 2 == 0
                box_color = ROI_BOX_COLOR_ACTIVE if blink_on else (0, 180, 60)
                # Overlay semi-transparan di luar ROI (gelap area luar)
                mask = np.zeros_like(frame, dtype=np.uint8)
                cv2.rectangle(mask, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.rectangle(mask, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 0), -1)
                frame = cv2.addWeighted(frame, 0.5, mask, 0.5, 0)
                # Pastikan ROI tetap jelas
                frame[roi_y1:roi_y2, roi_x1:roi_x2] = frame[roi_y1:roi_y2, roi_x1:roi_x2]
            else:
                # Normal: area luar ROI sedikit redup
                outside_mask = np.zeros_like(frame, dtype=np.uint8)
                cv2.rectangle(outside_mask, (0, 0), (w, h), (30, 30, 30), -1)
                cv2.rectangle(outside_mask, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 0), -1)
                frame = cv2.addWeighted(frame, 1.0, outside_mask, 0.35, 0)
                box_color = ROI_BOX_COLOR_BGR

            # Gambar kotak ROI
            cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), box_color, 3)

            # Sudut kecil untuk estetika industri
            corner_len = 20
            thick = 4
            for (px, py, dx, dy) in [
                (roi_x1, roi_y1,  1,  1),
                (roi_x2, roi_y1, -1,  1),
                (roi_x1, roi_y2,  1, -1),
                (roi_x2, roi_y2, -1, -1),
            ]:
                cv2.line(frame, (px, py), (px + dx * corner_len, py), box_color, thick)
                cv2.line(frame, (px, py), (px, py + dy * corner_len), box_color, thick)

            # Label "AREA SCAN" di atas kotak ROI
            roi_label = "AREA SCAN" if not scanning else "SCANNING..."
            lbl_color = box_color
            (lw, lh), _ = cv2.getTextSize(roi_label, FONT, 0.6, 2)
            lx = roi_x1 + (ROI_SIZE - lw) // 2
            ly = roi_y1 - 10
            if ly > 15:
                cv2.putText(frame, roi_label, (lx, ly), FONT, 0.6, lbl_color, 2)

            # ── Tampilkan hasil scan terakhir di bawah ROI box ────────────────
            if last_res:
                result_color = (
                    BOX_COLORS_BGR.get(last_res.get("label", ""), (200, 200, 200))
                    if last_res.get("name") != "OBJEK TIDAK DIKENALI"
                    else (100, 100, 100)
                )
                result_txt = (
                    f"{last_res.get('name','?')} "
                    f"{last_res.get('confidence','')}"
                )
                (rtw, _), _ = cv2.getTextSize(result_txt, FONT_BOLD, 0.7, 2)
                rx = roi_x1 + (ROI_SIZE - rtw) // 2
                ry = roi_y2 + 28
                if ry < h - 10:
                    # Background pill
                    cv2.rectangle(frame,
                                  (rx - 6, ry - 18),
                                  (rx + rtw + 6, ry + 6),
                                  (30, 30, 30), -1)
                    cv2.putText(frame, result_txt, (rx, ry),
                                FONT_BOLD, 0.7, result_color, 2)

        # ── HUD: AI status kiri atas ───────────────────────────────────────────
        if model:
            hud_ai = "AI: AKTIF"
            hud_col = (0, 220, 80)
        elif not TF_AVAILABLE:
            hud_ai = "AI: TF TIDAK ADA"
            hud_col = (0, 100, 255)
        else:
            hud_ai = "AI: ERROR"
            hud_col = (0, 80, 220)
        cv2.putText(frame, hud_ai, (10, 26), FONT, 0.55, hud_col, 2)

        mode_txt = "SORTING MODE" if mode == "sorting" else "PENGENALAN MODE"
        cv2.putText(frame, mode_txt, (10, 50), FONT, 0.45, (180, 180, 180), 1)

        # Timestamp kanan atas
        ts = now.strftime("%H:%M:%S")
        (tw, _), _ = cv2.getTextSize(ts, FONT, 0.52, 1)
        cv2.putText(frame, ts, (w - tw - 8, 24), FONT, 0.52, (180, 180, 180), 1)

        # ── Encode & yield ────────────────────────────────────────────────────
        ok_enc, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if not ok_enc:
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buf.tobytes()
            + b"\r\n"
        )


# ==============================================================================
#  ROUTES — HALAMAN HTML
# ==============================================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():
    now = datetime.now()
    month_names = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December",
    ]
    return render_template(
        "dashboard.html",
        monthly_data        = get_monthly_data(now.year, now.month),
        chart_data          = get_last_30_days_data(),
        current_month       = f"{month_names[now.month - 1]} {now.year}",
        current_month_value = f"{now.year}-{now.month:02d}",
    )


@app.route("/monitoring")
def monitoring():
    counts      = get_monitoring_counts()
    all_entries = []
    for ftype, entries in fruit_data.items():
        for e in entries:
            all_entries.append({
                "type":  ftype,
                "date":  e["date"],
                "count": e["count"],
                "image": e.get("image", ""),
            })
    all_entries.sort(key=lambda x: x["date"], reverse=True)
    return render_template(
        "monitoring.html",
        counts       = counts,
        recent_tomat = [e for e in all_entries if "tomat" in e["type"]],
        recent_apel  = [e for e in all_entries if "apel"  in e["type"]],
    )


@app.route("/pengenalan")
def pengenalan():
    return render_template("pengenalan.html")


@app.route("/penyortiran")
def penyortiran():
    return render_template(
        "penyortiran.html",
        counts                = get_monitoring_counts(),
        calibration_threshold = calibration_threshold,
        binary_threshold      = binary_threshold,
        min_roi_brightness    = min_roi_brightness,
        model_loaded          = (model is not None),
        model_error           = model_error_msg,
        min_confidence_pct    = int(MIN_CONFIDENCE * 100),
        roi_size              = ROI_SIZE,
    )


# ==============================================================================
#  ROUTES — VIDEO FEED (MJPEG)
# ==============================================================================

@app.route("/video_feed/<mode>")
def video_feed(mode: str):
    if mode not in ("pengenalan", "sorting"):
        mode = "pengenalan"
    return Response(
        generate_frames(mode),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ==============================================================================
#  API — [v4-1] MANUAL TRIGGER: CAPTURE & SORT
# ==============================================================================

@app.route("/api/capture_and_sort", methods=["POST"])
def capture_and_sort():
    """
    [v4-1] ENDPOINT UTAMA — dipanggil HANYA saat tombol diklik user.
    Langkah:
      1. Ambil frame terbaru dari kamera.
      2. [v4-2] Crop ke area ROI statis di tengah frame.
      3. [v4-4] BGR→RGB sebelum predict.
      4. [v4-3] Confidence ≥ 90% → simpan. Di bawah itu → tolak.
      5. Return JSON hasil deteksi.
    """
    global is_scanning, camera

    # Pastikan kamera aktif
    with _lock:
        cam_ref = camera

    if cam_ref is None or not cam_ref.isOpened():
        # Buka kamera jika belum terbuka
        with _lock:
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS,          30)
            cam_ref = camera
        time.sleep(0.5)  # Beri waktu kamera init

    # Set flag scanning ON (video feed tampilkan efek aktif)
    with _lock:
        is_scanning = True

    try:
        # Flush beberapa frame lama agar dapat frame terbaru (penting!)
        for _ in range(3):
            cam_ref.read()

        ok, frame = cam_ref.read()
        if not ok or frame is None:
            return jsonify({
                "success": False,
                "reason":  "Gagal membaca frame dari kamera",
                "saved":   False,
            }), 500

        h, w = frame.shape[:2]

        # [v4-2] Hitung koordinat ROI statis
        cx, cy  = w // 2, h // 2
        half    = ROI_SIZE // 2
        roi_x1  = max(0, cx - half)
        roi_y1  = max(0, cy - half)
        roi_x2  = min(w, cx + half)
        roi_y2  = min(h, cy + half)

        # Jalankan AI hanya pada ROI
        result = run_ai_on_roi(frame, roi_x1, roi_y1, roi_x2, roi_y2)

        # Update last_scan_result dengan info minimal untuk HUD video
        if not result["success"]:
            with _lock:
                last_scan_result.update({
                    "name":       "OBJEK TIDAK DIKENALI",
                    "confidence": f"{result['confidence']*100:.1f}%" if result["confidence"] else "—",
                    "label":      "",
                })

        # Tambahkan counts terkini ke response
        result["counts"] = get_monitoring_counts()

        return jsonify(result)

    except Exception as exc:
        print(f"❌  Error capture_and_sort: {exc}")
        return jsonify({
            "success": False,
            "reason":  f"Error internal: {str(exc)}",
            "saved":   False,
        }), 500

    finally:
        # Selalu matikan flag scanning
        with _lock:
            is_scanning = False


# ==============================================================================
#  API — KONTROL KAMERA
# ==============================================================================

@app.route("/api/start_camera", methods=["POST"])
def start_camera():
    """Buka kamera tanpa memulai deteksi otomatis."""
    global camera, camera_mode
    with _lock:
        camera_mode = "sorting"
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS,          30)
    return jsonify({"success": True, "message": "Kamera diaktifkan"})


@app.route("/api/stop_camera", methods=["POST"])
def stop_camera():
    global camera, camera_mode
    with _lock:
        camera_mode = None
        if camera is not None:
            camera.release()
            camera = None
    return jsonify({"success": True, "message": "Kamera dimatikan"})


@app.route("/api/reset_data", methods=["POST"])
def reset_data():
    global fruit_data, detection_log, last_scan_result
    with _lock:
        for k in fruit_data:
            fruit_data[k].clear()
        detection_log    = []
        last_scan_result = {}
    return jsonify({"success": True, "message": "Semua data berhasil direset"})


# ==============================================================================
#  API — KALIBRASI & PARAMETER
# ==============================================================================

@app.route("/api/set_threshold", methods=["POST"])
def set_threshold():
    global calibration_threshold
    try:
        val = int(request.get_json().get("value", 25000))
        val = max(1000, min(200_000, val))
        with _lock:
            calibration_threshold = val
        return jsonify({"success": True, "new_threshold": calibration_threshold})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/set_detection_params", methods=["POST"])
def set_detection_params():
    global binary_threshold, min_roi_brightness
    try:
        data    = request.get_json() or {}
        changed = {}
        if "binary_threshold" in data:
            val = max(0, min(255, int(data["binary_threshold"])))
            with _lock:
                binary_threshold = val
            changed["binary_threshold"] = val
        if "min_roi_brightness" in data:
            val = max(0, min(255, int(data["min_roi_brightness"])))
            with _lock:
                min_roi_brightness = val
            changed["min_roi_brightness"] = val
        return jsonify({"success": True, "changed": changed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/get_threshold", methods=["GET"])
def get_threshold():
    with _lock:
        return jsonify({
            "calibration_threshold": calibration_threshold,
            "binary_threshold":      binary_threshold,
            "min_roi_brightness":    min_roi_brightness,
            "min_confidence_pct":    int(MIN_CONFIDENCE * 100),
            "roi_size":              ROI_SIZE,
        })


# ==============================================================================
#  API — POLLING STATUS & LOG
# ==============================================================================

@app.route("/api/get_scan_status", methods=["GET"])
def get_scan_status():
    """
    Dipakai frontend untuk polling status kamera & hasil scan terakhir.
    """
    with _lock:
        scanning   = is_scanning
        last_res   = dict(last_scan_result)
        counts     = get_monitoring_counts()
        log_last5  = list(reversed(detection_log[-5:]))

    return jsonify({
        "scanning":          scanning,
        "last_result":       last_res,
        "counts":            counts,
        "recent_detections": log_last5,
        "model_loaded":      (model is not None),
        "params": {
            "calibration_threshold": calibration_threshold,
            "binary_threshold":      binary_threshold,
            "min_roi_brightness":    min_roi_brightness,
            "min_confidence_pct":    int(MIN_CONFIDENCE * 100),
            "roi_size":              ROI_SIZE,
        },
    })


@app.route("/api/get_detection_log", methods=["GET"])
def get_detection_log_route():
    with _lock:
        log_copy = list(reversed(detection_log))
    return jsonify({"log": log_copy, "total": len(log_copy)})


@app.route("/api/filter_dashboard", methods=["POST"])
def filter_dashboard():
    try:
        data       = request.get_json() or {}
        month_year = data.get("month", datetime.now().strftime("%Y-%m"))
        year, month = map(int, month_year.split("-"))
        return jsonify({"success": True, "data": get_monthly_data(year, month)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==============================================================================
#  ERROR HANDLERS
# ==============================================================================

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Halaman tidak ditemukan"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500


# ==============================================================================
#  ENTRYPOINT
# ==============================================================================

if __name__ == "__main__":
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("templates",     exist_ok=True)

    load_ai_model()

    print()
    print("=" * 65)
    print("   🍎  IoT Fruit Sorting  —  PRODUCTION v4 (MANUAL TRIGGER)")
    print("=" * 65)
    print(f"   Model      : {'✅ ' + MODEL_PATH if model else '❌ ' + model_error_msg}")
    print(f"   [v4-1]  Manual Trigger  : AI hanya aktif saat tombol diklik ✅")
    print(f"   [v4-2]  ROI Static Box  : {ROI_SIZE}×{ROI_SIZE}px di tengah frame ✅")
    print(f"   [v4-3]  Confidence      : ≥{int(MIN_CONFIDENCE*100)}% (naik dari 85%) ✅")
    print(f"   [v4-4]  BGR→RGB         : diterapkan pada ROI crop ✅")
    print(f"   [v4-5]  Video Feed      : streaming tanpa auto-detect ✅")
    print(f"   [v4-6]  Kalibrasi       : {calibration_threshold}px (Apel Besar vs Sedang)")
    print(f"   [v4-7]  Sinkron DB      : fruit_data → dashboard & Monitoring ✅")
    print("-" * 65)
    print("   dashboard   → http://localhost:5000/dashboard")
    print("   Monitoring  → http://localhost:5000/monitoring")
    print("   Penyortiran → http://localhost:5000/penyortiran")
    print("   Video Feed  → http://localhost:5000/video_feed/sorting")
    print("=" * 65)
    print("   ⚠️  debug=False & use_reloader=False wajib saat ada OpenCV thread")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False,
    )

