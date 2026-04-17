# Smart Interview Simulator

An AI-powered interview practice system with NLP analysis, resume parsing, and performance tracking.

## 📁 Project Structure

```
smart-interview-simulator/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── resume_parser.py    # Resume parsing module
│   ├── nlp_analyzer.py     # NLP analysis engine
│   ├── question_generator.py # Question generation
│   ├── feedback_engine.py  # Feedback & scoring
│   ├── database.py         # Database manager
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── src/
│   │   ├── pages/         # React pages
│   │   │   ├── Home.js
│   │   │   ├── InterviewSetup.js
│   │   │   ├── Interview.js
│   │   │   ├── Feedback.js
│   │   │   ├── History.js
│   │   │   └── Dashboard.js
│   │   ├── services/
│   │   │   └── api.js     # API service
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
│
├── dataset/
│   └── questions.json     # Question database
│
├── models/                # ML models (future)
├── database/              # Local storage fallback
└── README.md
```

## 🚀 Installation Steps

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **MongoDB** (optional, uses file storage if not available)

---

### Step 1: Clone & Setup

```bash
# Navigate to project directory
cd smart-interview-simulator
```

---

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (for NLP)
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

---

### Step 3: Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

---

### Step 4: Configure Environment (Optional)

Create `.env` file in backend directory:

```env
# MongoDB Connection (optional)
MONGODB_URI=mongodb://localhost:27017/interview_simulator

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Frontend API URL
REACT_APP_API_URL=http://localhost:8000/api
```

---

## ▶️ Running the Application

### Start Backend Server

```bash
cd backend
python main.py
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm start
```

The app will open at: `http://localhost:3000`

---

## 🐳 Docker Deployment (Optional)

### Create Dockerfile for Backend

```dockerfile
# filepath: backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### Create Dockerfile for Frontend

```dockerfile
# filepath: frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

```yaml
# filepath: docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./database:/app/database

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### Run with Docker

```bash
docker-compose up --build
```

---

## 📦 Production Build

### Backend

```bash
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend

```bash
cd frontend
npm run build
```

The build output will be in `frontend/build/`

---

## 🔧 Configuration Options

### Question Database

Edit `dataset/questions.json` to add/modify questions:

```json
{
  "software_developer": {
    "easy": [
      {
        "text": "Your question here",
        "category": "topic",
        "expected_keywords": ["keyword1", "keyword2"],
        "time_limit": 60
      }
    ]
  }
}
```

### Resume Skills

Edit `resume_parser.py` to add more skills:

```python
TECH_KEYWORDS = {
    "new_category": ["skill1", "skill2", "skill3"]
}
```

---

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/roles` | GET | Get job roles |
| `/api/interview/start` | POST | Start interview |
| `/api/resume/upload` | POST | Upload resume |
| `/api/question/{session_id}` | GET | Get next question |
| `/api/answer/submit` | POST | Submit answer |
| `/api/interview/end` | POST | End interview |
| `/api/history/{user_id}` | GET | Get history |
| `/api/dashboard/{user_id}` | GET | Get dashboard |

---

## 🛠️ Troubleshooting

### Common Issues

**1. SpaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**2. NLTK data missing**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

**3. MongoDB connection failed**
- The app automatically falls back to file-based storage
- No action needed

**4. Frontend API connection error**
- Ensure backend is running on port 8000
- Check `REACT_APP_API_URL` in environment

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues and questions, please open a GitHub issue.