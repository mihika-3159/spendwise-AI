# 💸 Spendwise – AI-Powered Smart Expense Tracker

Spendwise is a simple but powerful **personal finance app** built with **Streamlit**.  
It lets you **log expenses, visualize spending, set goals, and get AI-powered money-saving tips** using Hugging Face’s free LLMs.

---

## ✨ Features
- 🔑 **Secure login & registration** (password hashing, stored in CSV)
- 📝 **Expense logging** with category, date, amount, description
- 📊 **Analytics dashboard**: monthly totals, goal tracking, bar & pie charts
- 💡 **AI Tips**: Hugging Face LLM suggests money-saving strategies (with caching & fallback)
- ⬇️ **Download CSV**: export your expenses
- 👨‍💻 **Demo user included** (`demo/demo123`)
- 🔒 **Security**: hashed passwords, `.env` for API keys, `.gitignore` for sensitive files

---

## 🛠 Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io)  
- **Backend:** Python (`utils/` for data + AI helpers)  
- **AI:** Hugging Face Inference API (default: `google/flan-t5-base`)  
- **Data:** CSV persistence (per-user expenses)  

---

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
pip install requirements.txt
```
### 4. Run the App
```bash
streamlit run app.py
```

Then open the link in your browser

## 📊 Demo

A live demo will be hosted soon via Streamlit Community Cloud, so anyone can try SpendWise without installing anything.

## 🙏 Acknowledgments

Thanks to Decoding Data Science for giving me the opportunity to build this project during the 8-day AI Challenge!

## 📌 Roadmap

 Add persistent storage so user data is saved between sessions

 Improve AI-generated advice using more personalized prompts

 Add expense categories and monthly summaries

 Deploy final version with public link

## 🧑‍💻 Contributing

Contributions and feedback are welcome! Open an issue or submit a pull request to suggest improvements