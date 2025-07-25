# 🏛️ Wardi - Indonesia's Digital Heritage

Wardi(warisan digital indonesia ) is an innovative non-profit digital platform dedicated to preserving, recognizing, and learning about Indonesia's rich cultural heritage using AI technology and the power of community.

## 🎯 Vision & Mission

Vision: To become the leading platform for digitizing and preserving Indonesia's cultural heritage.

**Mission:**
- Facilitating the preservation of Indonesian culture through modern technology
- Connecting the public with the archipelago's cultural heritage
- Providing AI-based cultural education and analysis
- Building a community of Indonesian culture enthusiasts

## ✨ Key Features

### 🤖 AI Cultural Analysis
- **AI Image Analysis**: Identification of cultural objects using computer vision technology
- **Pattern Recognition**: Detection of batik motifs, carvings, and traditional ornaments
- **Cultural Classification**: Automatic categorization based on region of origin and period

### 🗣️ Language Translator
- **Regional Language Translator**: Real-time translation of Indonesian regional languages
- **Voice Recognition**: Voice input for live translation
- **Audio Playback**: Listen to the correct pronunciation

### 🌍 Cultural Places
- **Tourist Attraction Database**: Complete catalog of cultural attractions
- **Rating & Review**: Community rating and review system
- **Complete Categories**: Museums, Temples, Palaces, Tourist Villages, Galleries

### 💬 Community Forum
- **Cultural Discussion**: Forum for sharing experiences and knowledge
- **Interactive Q&A**: Questions and answers about Indonesian culture
- **Active Community**: Network of culture lovers from across the archipelago

### 👤 User Management
- **Registration & Login**: Secure authentication system
- **Personal Profile**: Manage cultural information and preferences
- **Progress Tracking**: Monitor activity and contributions

## 🛠️ Technology

### Backend
- **Framework**: Django 5.2.4
- **Database**: SQLite
- **Authentication**: Django Auth System
- **API**: RESTful APIs for front-end interaction

### Frontend
- **Template Engine**: Django Templates
- **Styling**: Custom CSS with responsive design
- JavaScript: Vanilla JS for interactivity
- Icons & UI: Emoji-based icons for easy accessibility

### AI & Machine Learning
- Google AI: Integration with Google Generative AI
- Image Processing: PIL (Python Imaging Library)
- Computer Vision: AI-powered cultural object recognition

## 📂 Project Structure

garuda/
└── wardi/ # Django Project Root
├── manage.py # Django management script
├── db.sqlite3 # Database file
├── wardi/ # Main project settings
│ ├── settings.py # Django configuration
│ ├── urls.py # Main URL routing
│ ├── wsgi.py # WSGI configuration 
│ └── asgi.py # ASGI configuration 
└── landing/ # Main application 
├── models.py # Database models 
├── views.py # View functions 
├── urls.py # App URL routing 
├── admin.py # Admin interface 
├── apps.py # App configuration 
├── tests.py # Unit tests 
├── migrations/ # Database migrations 
├── templates/ # HTML templates 
│ └── landing/ 
│ ├── base.html # Base template 
│ ├── index.html # Homepage 
│ ├── analyze.html # AI Analysis page 
│ ├── translate.html # Translation page 
│ ├── forum.html # Community forum 
│ ├── places.html # Cultural places 
│ ├── login.html # Login page 
│ └── register.html # Registration page 
└── static/ # Static files 
└── landing/ 
├── css/ 
└── js/
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2.4
- Git

### 1. Clone Repository
```bash
git clone https://github.com/JordiTBA/garuda.git
cd garuda
```

### 2. Setup Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source v/bin/activate
```

### 3. Install Dependencies
```bash
pip install django==5.2.4
pip install pillow
pip install google-genai
```

### 4. Database Setup
```bash
cd Wardi 
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Open a browser and access `http://127.0.0.1:8000/`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GOOGLE_AI_API_KEY=your-google-ai-api-key
```

### Google AI Setup
1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Add the key to the environment variables
3. Restart the server for the changes to take effect

## 📱 Usage

### 1. Home Page
- Access the platform's main features
- Intuitative navigation

## 🙏 Special Credits

We would like to extend our heartfelt gratitude to the following services and tools that made this project possible:

### 🤖 **Gemini AI**
- **Purpose**: Core AI API used throughout the website
- **Application**: Powers cultural object recognition, image analysis, and intelligent translation features
- **Impact**: Enables advanced computer vision capabilities for identifying Indonesian cultural artifacts and heritage items

### 🛠️ **GitHub Copilot**
- **Purpose**: AI-powered coding assistant 
- **Application**: Helped accelerate development through intelligent code completion and suggestions in VS Code
- **Impact**: Significantly improved development efficiency and code quality throughout the project lifecycle

### 🔍 **DeepSeek**
- **Purpose**: AI coding assistant and technical reference
- **Application**: Provided guidance for both frontend and backend development challenges
- **Impact**: Assisted in finding optimal solutions, best practices, and technical references for web development implementation

These tools were instrumental in bringing Wardi to life, combining human creativity with AI assistance to preserve and celebrate Indonesia's rich cultural heritage.