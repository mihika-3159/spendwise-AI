# 💸 SpendWise — Track Smart, Spend Wise

**SpendWise** is a personal finance tracker built with **Streamlit** that helps you manage your expenses and get **AI-powered money-saving tips** based on your spending habits.

---

## 🚀 Features

- 🔐 **User Login & Registration**
- 💰 **Expense Tracking** by category and date  
- 📊 **Visual Analytics Dashboard**
- 🧠 **AI-Powered Smart Tips** using Cohere (Free Tier)
- 💾 **CSV-based Data Storage** (simple and local)
- ☁️ **Deployable on Streamlit Cloud**

---

## 🧩 Project Structure

SpendWise/
│
├── app.py 
├── utils/
│ ├── ai_helper.py # AI tip generation (Cohere API)
│ ├── tips.py # Tip logic and fallback system
│ ├── data_utils.py # Read/write CSV utilities
│ └── init.py
│
├── users.csv # User data
├── expenses/ # Individual user expense files
├── .env # API keys and environment variables
└── requirements.txt # Python dependencies

## 🏃 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR-USERNAME/SpendWise.git
cd SpendWise
```
### 2. Create and Activate Virtual Environment
```bash 
python -m venv venv
#For Windows
venv/Scripts/activate 
# For Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file
```
COHERE_API_KEY=your_cohere_pi_key
```

### 5. Run the App
```bash
streamlit run app.py
```

Then open the link in your browser

---
##🧠 AI Tips with Cohere

SpendWise uses Cohere’s Chat API (command-r-08-2024 model) to generate personalized, contextual money-saving tips based on your latest 30 days of spending.

---

## 📦 Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

---
## Tagline

SpendWise — Track Smart, spend wise
---

## 📄 License
MIT
---

## 📊 Demo

A live demo will be hosted soon via Streamlit Community Cloud, so anyone can try SpendWise without installing anything.
---

## 🙏 Acknowledgments

Thanks to Decoding Data Science for giving me the opportunity to build this project during the 8-day AI Challenge!
---

## 🧑‍💻 Contributing

Contributions and feedback are welcome! Open an issue or submit a pull request to suggest improvements
---