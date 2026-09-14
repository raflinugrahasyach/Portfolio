# 🍎 IoT Fruit Sorting System - PIXEL-PERFECT EDITION

> **Sistem penyortiran buah berbasis IoT dengan design 100% IDENTIK sesuai referensi**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📸 Screenshots

Design aplikasi ini dibuat **100% IDENTIK pixel-perfect** dengan referensi client. Setiap elemen UI telah disesuaikan dengan presisi tinggi.

## ✨ Fitur Utama

### 🎯 analytics interface
- ✅ Filter data berdasarkan bulan dengan date picker
- ✅ Tabel ringkasan dengan total row berwarna ungu solid
- ✅ Grafik tren 30 hari terakhir (Chart.js)
- ✅ Animasi smooth saat update data
- ✅ Responsive design

### 📊 Monitoring Real-Time
- ✅ 4 Kartu statistik dengan **border top berwarna berbeda**:
  - Tomat Masak: Border Merah (#ef5350)
  - Tomat Mentah: Border Hijau (#66bb6a)
  - Apel Sedang: Border Orange (#ffa726)
  - Apel Besar: Border Biru (#42a5f5)
- ✅ Tabel riwayat untuk Tomat dan Apel
- ✅ Auto-refresh setiap 3 detik
- ✅ Animasi fade-in untuk kartu

### 📸 Pengenalan
- ✅ Akses webcam real-time dengan izin browser
- ✅ Capture gambar dengan efek flash
- ✅ Galeri 6 gambar terakhir dengan delete option
- ✅ Keyboard shortcuts (Space/Enter untuk capture)
- ✅ Instructions box dengan numbered list

### 💡 Penyortiran
- ✅ Feed video real-time dari webcam
- ✅ Panel kontrol dengan 3 tombol:
  - Mulai Deteksi (Hijau)
  - Hentikan (Merah)
  - Reset Data (Abu-abu)
- ✅ Detection box dengan background hijau gradient
- ✅ **Panel statistik style formulir** dengan border tegas
- ✅ Status indicator dengan pulse animation
- ✅ Instruksi penggunaan dengan numbered badges

## 🎨 Design Specifications

### Color Palette
```css
/* Primary Colors */
--primary-purple: linear-gradient(135deg, #6a1b9a 0%, #8e24aa 100%);
--success-green: #2ecc71;
--danger-red: #e74c3c;
--info-blue: #5c6bc0;
--warning-orange: #ffa726;

/* Stat Card Border Colors */
--tomat-masak: #ef5350;
--tomat-mentah: #66bb6a;
--apel-sedang: #ffa726;
--apel-besar: #42a5f5;

/* Neutrals */
--bg-light: #f4f6f9;
--card-white: #ffffff;
--text-dark: #2c3e50;
--text-muted: #6c757d;
```

### Typography
- **Font Family**: 'Poppins', 'Segoe UI', sans-serif
- **Weights**: 300, 400, 500, 600, 700, 800
- **Headers**: Bold (700-800)
- **Body**: Regular (400-500)

### Spacing
- Card Padding: 24-28px
- Gap between elements: 12-24px
- Border Radius: 8-12px
- Box Shadow: 0 2px 8px rgba(0, 0, 0, 0.08)

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
Webcam (untuk fitur deteksi)
```

### Installation

**1. Clone atau Download Project**
```bash
git clone <repository-url>
cd iot-fruit-sorting
```

**2. Install Dependencies**
```bash
pip install Flask
# atau
pip install -r requirements.txt
```

**3. Run Application**
```bash
python app_new.py
```

**4. Open Browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
iot-fruit-sorting/
│
├── app_new.py                  # Main Flask application
├── requirements.txt            # Python dependencies
│
├── templates_new/              # HTML Templates (Jinja2)
│   ├── base.html              # Base template dengan navbar
│   ├── analytics interface.html         # analytics interface dengan chart
│   ├── monitoring.html        # Real-time monitoring
│   ├── pengenalan.html        # Image recognition
│   └── penyortiran.html       # Sorting mode
│
└── static/                     # Static files
    ├── images/                # Fruit images
    └── css/                   # Additional CSS (if needed)
```

## 🔧 Configuration

### Flask Settings
Edit `app_new.py`:
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DEBUG'] = True  # Set False for production
```

### Port Configuration
```python
app.run(
    host='0.0.0.0',  # Allow external access
    port=5000,       # Change if port 5000 is busy
    debug=True
)
```

## 📊 Data Management

### Current Implementation
- **Storage**: In-memory (Python dictionaries)
- **Persistence**: Lost on server restart
- **Sample Data**: Auto-generated for testing

### For Production
Recommended to use database:

**SQLite** (Simplest)
```python
import sqlite3
# Simple, file-based, no server needed
```

**PostgreSQL** (Recommended)
```python
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/fruitdb'
```

**MongoDB** (For high volume)
```python
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
```

## 🎯 API Endpoints

### analytics interface
```
GET  /analytics interface            - Main analytics interface page
POST /api/filter_dashboard - Filter by month
```

### Monitoring
```
GET /monitoring            - Real-time monitoring page
```

### Pengenalan & Penyortiran
```
GET  /pengenalan          - Recognition page
GET  /penyortiran         - Sorting page
POST /api/start_detection - Start detection
POST /api/stop_detection  - Stop detection
POST /api/detect_fruit    - Detect fruit (simulated)
POST /api/reset_data      - Reset all data
GET  /api/get_current_detection - Get current state
```

## 🔐 Security Considerations

### For Production release

**1. Environment Variables**
```python
import os
app.secret_key = os.environ.get('SECRET_KEY', 'default-key')
```

**2. HTTPS/SSL**
```python
if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # For development
    # Use proper SSL certificates in production
```

**3. CORS Configuration**
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

**4. Input Validation**
```python
from werkzeug.security import check_password_hash
# Add authentication middleware
```

## 🧪 Testing

### Manual Testing
1. Start application
2. Test each page navigation
3. Test camera access
4. Test data filtering
5. Test detection simulation

### Automated Testing (Future)
```python
import unittest
class TestDashboard(unittest.TestCase):
    def test_homepage(self):
        response = self.client.get('/analytics interface')
        self.assertEqual(response.status_code, 200)
```

## 🐛 Troubleshooting

### Common Issues

**Port 5000 Already in Use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**Camera Not Working**
- Check browser permissions (Settings → Privacy)
- Ensure HTTPS or localhost
- Close other apps using camera
- Try different browser

**ModuleNotFoundError**
```bash
pip install Flask --upgrade
```

**Chart Not Displaying**
- Check internet connection (Chart.js loads from CDN)
- Check browser console for errors
- Ensure jQuery is loaded before Chart.js

## 🌐 Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 90+     | ✅ Recommended |
| Firefox | 88+     | ✅ Fully Supported |
| Safari  | 14+     | ✅ Supported |
| Edge    | 90+     | ✅ Supported |
| IE      | Any     | ❌ Not Supported |

## 📱 Responsive Design

The application is optimized for:
- **Desktop**: 1920x1080 (Primary target)
- **Laptop**: 1366x768
- **Tablet**: 768x1024
- **Mobile**: 375x667 (Basic support)

## 🔄 Update History

### Version 2.0 - Pixel-Perfect Edition
- ✅ Complete UI redesign matching client specifications
- ✅ Border-top colored stat cards
- ✅ Formulir-style statistics panel
- ✅ Enhanced animations and transitions
- ✅ Improved instructions boxes
- ✅ Better keyboard shortcuts
- ✅ Flash effect on capture

### Version 1.0 - Initial Release
- Basic functionality
- Simple UI

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

## 👥 Credits

- **Design**: Based on client specifications
- **Framework**: Flask (Python)
- **Charts**: Chart.js
- **Icons**: Unicode emoji
- **Font**: Google Fonts (Poppins)

## 📞 Support

For issues or questions:
- Check troubleshooting section
- Review code comments
- Contact development team

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Docs](https://www.chartjs.org/docs/)
- [WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

---

**Made with ❤️ for IoT Fruit Sorting**

*Last Updated: February 2026*
