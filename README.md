# 🧠 ChatBot for Mental Health Assessment

A Telegram-based chatbot that conducts depression screening assessments using the **PHQ-9 (Patient Health Questionnaire-9)** and provides personalized mental health insights and resources.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## 🎯 Overview

This project is a mental health chatbot designed to help users assess their mental well-being through scientifically validated questionnaires. The bot uses the **PHQ-9** depression screening tool to classify depression severity and provide supportive responses.

⚠️ **Important:** This bot is for educational and assessment purposes only and is **not a substitute** for professional mental health care.

---

## ✨ Features

- ✅ **PHQ-9 Depression Screening**: Conduct standardized depression assessments with 9 scientifically validated questions
- ✅ **Severity Classification**: Automatically classify depression into 5 levels (None, Mild, Moderate, Moderately Severe, Severe)
- ✅ **Personalized Responses**: Provide empathetic, therapeutic feedback based on assessment results
- ✅ **Secure Data Storage**: Store user assessments and conversation history in SQLite database
- ✅ **Mental Health Resources**: Share crisis hotlines, self-care tips, and professional resources
- ✅ **Assessment History**: Users can view their past assessment results
- ✅ **Privacy-Focused**: All data stored securely and confidentially
- ✅ **Scalable Architecture**: Built to handle multiple concurrent users

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Bot Framework**: [python-telegram-bot](https://python-telegram-bot.org/) v21.5
- **Database**: SQLite3
- **Machine Learning**: scikit-learn (for depression classification)
- **Environment Management**: python-dotenv

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Telegram account
- Git

### Step 1: Clone the Repository

git clone https://github.com/smritisingh-0401/ChatBot-for-Mental-Health-Assess.git
cd ChatBot-for-Mental-Health-Assess


### Step 2: Create Virtual Environment

Windows
python -m venv venv
venv\Scripts\activate


### Step 3: Install Dependencies

pip install -r requirements.txt


### Step 4: Initialize Database

python database.py

You should see:
✓ Database initialized successfully


---

## ⚙️ Configuration

### 1. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. Copy the bot token (looks like `123456789:ABCDefGHIjklmnoPQRstuvwxyz`)

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_PATH=./data/users.db

---

## 💻 Usage

### Run the Bot Locally
You should see:
INFO:telegram.ext._application:Application started

### Interact with Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start` to begin
4. Follow the prompts to take the assessment

---

## 📁 Project Structure

ChatBot-for-Mental-Health-Assess/
├── data/
│ └── users.db # SQLite database (auto-generated)
├── database.py # Database setup and CRUD operations
├── depression_detector.py # PHQ-9 scoring and classification logic
├── main.py # Main bot handler and conversation flow
├── requirements.txt # Python dependencies
├── .env # Environment variables (not committed)
├── .gitignore # Git ignore rules
└── README.md # Project documentation

text

---

## 🧪 How It Works

### PHQ-9 Assessment Flow

1. **User starts conversation**: Bot greets and explains the assessment
2. **9 Questions asked**: Each question measures depression symptoms over past 2 weeks
3. **User selects frequency**: 
   - Not at all (0 points)
   - Several days (1 point)
   - More than half the days (2 points)
   - Nearly every day (3 points)
4. **Score calculation**: Total score ranges from 0-27
5. **Severity classification**:
   - 0-4: No depression
   - 5-9: Mild depression
   - 10-14: Moderate depression
   - 15-19: Moderately severe depression
   - 20-27: Severe depression
6. **Personalized response**: Bot provides appropriate recommendations
7. **Resources shared**: Crisis hotlines, self-care tips, professional help options

### Database Schema

**Users Table**
- user_id (PRIMARY KEY)
- username, first_name, last_name
- created_at, last_interaction

**Assessments Table**
- assessment_id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- phq9_score, severity, answers
- assessment_date

**Conversations Table**
- conversation_id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- user_message, bot_response
- message_timestamp

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

**This chatbot is for educational and informational purposes only.**

- This bot is **NOT** a replacement for professional medical advice, diagnosis, or treatment
- Always seek the advice of a qualified mental health professional
- If you are experiencing a mental health crisis, please contact emergency services or a crisis hotline immediately

**Crisis Resources:**
- **US**: 988 Suicide & Crisis Lifeline (call or text 988)
- **International**: https://www.iasp.info/resources/Crisis_Centres/

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Smriti Singh**

- GitHub: [@smritisingh-0401](https://github.com/smritisingh-0401)
- Project Link: [ChatBot-for-Mental-Health-Assess](https://github.com/smritisingh-0401/ChatBot-for-Mental-Health-Assess)

---

## 🙏 Acknowledgments

- PHQ-9 questionnaire developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke
- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Mental health resources from SAMHSA, NAMI, and Crisis Text Line.

---
