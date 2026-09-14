# 📐 Technical Specifications - IoT Fruit Sorting System

## Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                │
│  HTML5 + CSS3 + JavaScript (Vanilla) + Jinja2      │
│  Chart.js + jQuery + WebRTC API                     │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                  │
│              Flask 3.0 (Python 3.8+)                │
│         RESTful API + Server-Side Rendering         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                     DATA LAYER                      │
│         In-Memory Storage (Development)             │
│      SQLite/PostgreSQL (Production Ready)           │
└─────────────────────────────────────────────────────┘
```

## Frontend Specifications

### HTML Structure

#### Base Template (`base.html`)
- **Purpose**: Master layout for all pages
- **Components**:
  - Navigation bar with gradient background
  - Active link highlighting
  - User greeting section
  - Logout button
  - Container wrapper for content
  - Script imports (jQuery, Chart.js)

#### analytics interface (`analytics interface.html`)
- **Components**:
  1. Month Filter Card
     - Month input type
     - Filter button (primary blue)
     - Reset button (danger red)
     - Display month text
  
  2. Summary Table Card
     - Header with title
     - 4-row data table
     - Footer row with purple gradient background
     - Responsive columns
  
  3. Chart Visualization Card
     - Chart.js line chart
     - Legend (Apel, Tomat)
     - 30-day trend display
     - Smooth animations

#### Monitoring (`monitoring.html`)
- **Components**:
  1. Stats Grid (4 cards)
     - Each card has unique border-top color
     - Large number display (56px font)
     - Label in uppercase
     - Hover effects
  
  2. Tomat Table
     - 6 columns
     - Zebra striping
     - Image preview
     - Empty state handling
  
  3. Apel Table
     - Same structure as Tomat table
     - Separate data stream

#### Pengenalan (`pengenalan.html`)
- **Components**:
  1. Tab Navigation
     - Pill-shaped buttons
     - Active state styling
  
  2. Camera Panel
     - Video stream container (420px height)
     - Placeholder with icon
     - Instructions box with numbered list
     - 3 control buttons
  
  3. Gallery Panel
     - 2x3 grid layout
     - Image thumbnails
     - Delete button overlay
     - Empty state message

#### Penyortiran (`penyortiran.html`)
- **Components**:
  1. Feed Panel
     - Video container (480px height)
     - Instructions with numbered badges
     - Black background for video
  
  2. Control Panel
     - Status indicator with pulse animation
     - 3 action buttons
     - Detection info box (green gradient)
     - Statistics panel (formulir-style)

### CSS Architecture

#### Design Tokens
```css
/* Colors */
--primary-purple-start: #6a1b9a;
--primary-purple-end: #8e24aa;
--success-green: #2ecc71;
--danger-red: #e74c3c;
--info-blue: #5c6bc0;
--warning-orange: #ffa726;

/* Border Colors */
--border-tomat-masak: #ef5350;
--border-tomat-mentah: #66bb6a;
--border-apel-sedang: #ffa726;
--border-apel-besar: #42a5f5;

/* Typography */
--font-family: 'Poppins', 'Segoe UI', sans-serif;
--font-size-base: 14px;
--font-size-large: 16px;
--font-size-xlarge: 56px;

/* Spacing */
--spacing-xs: 8px;
--spacing-sm: 12px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;

/* Border Radius */
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 12px;
--radius-full: 50px;

/* Shadows */
--shadow-sm: 0 2px 4px rgba(0,0,0,0.06);
--shadow-md: 0 2px 8px rgba(0,0,0,0.08);
--shadow-lg: 0 4px 16px rgba(0,0,0,0.12);
```

#### Layout System
- **Grid**: CSS Grid for main layouts
- **Flexbox**: For component alignment
- **Container Max-Width**: 1400px
- **Breakpoints**:
  - Desktop: 1920px (primary)
  - Laptop: 1366px
  - Tablet: 768px
  - Mobile: 375px

#### Animation Patterns
```css
/* Hover Effects */
.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(...);
  transition: all 0.3s ease;
}

/* Fade In */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Flash (Camera) */
@keyframes flash {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}
```

### JavaScript Functionality

#### Chart.js Configuration
```javascript
const chartConfig = {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: 'Apel',
      data: apelData,
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.1)',
      borderWidth: 3,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true }
    }
  }
};
```

#### WebRTC Camera Access
```javascript
async function startCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: {
      width: { ideal: 1280 },
      height: { ideal: 720 }
    }
  });
  
  const video = document.createElement('video');
  video.srcObject = stream;
  video.autoplay = true;
  video.playsInline = true;
}
```

#### AJAX Pattern
```javascript
$.ajax({
  url: '/api/endpoint',
  method: 'POST',
  contentType: 'application/json',
  data: JSON.stringify(payload),
  success: function(response) {
    // Handle success
  },
  error: function(xhr, status, error) {
    // Handle error
  }
});
```

## Backend Specifications

### Flask Application Structure

#### Route Mapping
```python
Routes:
  GET  /                     → Redirect to analytics interface
  GET  /analytics interface            → analytics interface page
  GET  /monitoring           → Monitoring page
  GET  /pengenalan           → Recognition page
  GET  /penyortiran          → Sorting page
  
API Endpoints:
  POST /api/start_detection  → Start detection
  POST /api/stop_detection   → Stop detection
  POST /api/detect_fruit     → Detect fruit
  POST /api/reset_data       → Reset data
  POST /api/filter_dashboard → Filter by month
  GET  /api/get_current_detection → Get state
```

#### Data Models

```python
# Fruit Data Structure
fruit_data = {
    'apel_besar': [
        {
            'date': '2026-02-15',
            'count': 5,
            'image': '/static/images/apel_besar.jpg',
            'timestamp': '2026-02-15T10:30:00'
        }
    ],
    # ... other fruit types
}

# Detection State
detection_state = {
    'running': False,
    'current_fruit': {
        'id': '260215_001',
        'name': 'APEL BESAR',
        'size': 'BESAR',
        'color': '#FFB800',
        'status': 'MATANG',
        'type': 'apel_besar'
    }
}
```

#### Helper Functions

```python
def get_monthly_data(year: int, month: int) -> dict:
    """
    Calculate fruit counts for specific month
    Returns: {fruit_type: count}
    """
    
def get_last_30_days_data() -> dict:
    """
    Get daily data for last 30 days
    Returns: {date: {apel: count, tomat: count}}
    """
```

### API Response Format

#### Success Response
```json
{
  "success": true,
  "data": {
    "apel_besar": 94,
    "apel_sedang": 48,
    "tomat_masak": 150,
    "tomat_mentah": 59
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

#### Detection Response
```json
{
  "success": true,
  "fruit": {
    "id": "260215_001",
    "name": "APEL BESAR",
    "size": "BESAR",
    "color": "#FFB800",
    "status": "MATANG",
    "type": "apel_besar"
  }
}
```

## Performance Specifications

### Page Load Times (Target)
- analytics interface: < 1.5s
- Monitoring: < 1.0s
- Pengenalan: < 1.0s
- Penyortiran: < 1.2s

### Optimization Strategies
1. **CSS**:
   - Minify in production
   - Critical CSS inline
   - Lazy load non-critical styles

2. **JavaScript**:
   - Defer non-critical scripts
   - Use CDN for libraries
   - Minimize DOM manipulation

3. **Images**:
   - WebP format with fallback
   - Lazy loading
   - Responsive images

4. **Network**:
   - Enable gzip compression
   - HTTP/2 push
   - Browser caching

### Memory Usage
- Frontend: ~50MB (with Chart.js)
- Backend: ~100MB (Flask + data)
- Peak: ~200MB (with camera stream)

## Security Specifications

### Authentication (Production)
```python
from flask_login import LoginManager, login_required

@app.route('/analytics interface')
@login_required
def analytics interface():
    # ...
```

### CSRF Protection
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

### Input Validation
```python
from werkzeug.security import safe_join

def validate_month(month_str):
    pattern = r'^\d{4}-\d{2}$'
    if not re.match(pattern, month_str):
        raise ValueError("Invalid month format")
```

### HTTPS Configuration
```python
if not app.debug:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(ssl_context=context)
```

## Testing Specifications

### Unit Tests
```python
import unittest

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_dashboard_loads(self):
        response = self.app.get('/analytics interface')
        self.assertEqual(response.status_code, 200)
    
    def test_filter_api(self):
        response = self.app.post('/api/filter_dashboard',
                                json={'month': '2026-02'})
        data = response.get_json()
        self.assertTrue(data['success'])
```

### Integration Tests
- Camera access flow
- Detection simulation
- Data persistence
- Chart rendering

### Performance Tests
- Load testing with 100 concurrent users
- Memory leak detection
- Database query optimization

## release Specifications

### Development
```bash
python app_new.py
# Runs on http://localhost:5000
# Debug mode: ON
# Auto-reload: ON
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app_new:app
# Workers: 4
# Port: 8000
# Debug: OFF
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app_new:app"]
```

### Environment Variables
```bash
FLASK_APP=app_new.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...
```

## Browser Compatibility Matrix

| Feature | Chrome 90+ | Firefox 88+ | Safari 14+ | Edge 90+ |
|---------|-----------|-------------|-----------|----------|
| CSS Grid | ✅ | ✅ | ✅ | ✅ |
| Flexbox | ✅ | ✅ | ✅ | ✅ |
| WebRTC | ✅ | ✅ | ✅ | ✅ |
| Fetch API | ✅ | ✅ | ✅ | ✅ |
| ES6+ | ✅ | ✅ | ✅ | ✅ |
| CSS Variables | ✅ | ✅ | ✅ | ✅ |

## Accessibility (WCAG 2.1)

### Level AA Compliance
- Color contrast ratio: 4.5:1 minimum
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators
- Alt text for images
- ARIA labels where needed

---

**Document Version**: 2.0  
**Last Updated**: February 2026  
**Maintained By**: Development Team
