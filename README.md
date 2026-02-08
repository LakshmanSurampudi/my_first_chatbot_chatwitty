# Witty Chatbot Deployment Guide

## Implementation Steps

### 1. Local Setup & Testing

```bash
# Navigate to project directory
cd chatbot-deploy

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

Visit http://localhost:8000 to test the chatbot.

---

### 2. Deploy to Render

#### A. Prepare GitHub Repository

```bash
# Initialize git (if not already)
git init

# Create .gitignore
echo ".env" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# Add and commit files
git add .
git commit -m "Initial commit: Witty chatbot"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

#### B. Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
   - Sign up/login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repo you just pushed

3. **Configure Service**
   - **Name**: `witty-chatbot` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - Click "Environment" tab
   - Add: `GOOGLE_API_KEY` = `your_actual_google_api_key`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your chatbot will be live at: `https://witty-chatbot-XXXX.onrender.com`

---

### 3. Share with People

Once deployed, share the Render URL with anyone:
- Example: `https://witty-chatbot-abc123.onrender.com`
- No login required
- Each user gets their own session automatically
- Sessions expire after 30 minutes of inactivity

---

## Troubleshooting

**Local Testing Issues:**
- Ensure `.env` file exists with valid `GOOGLE_API_KEY`
- Check port 8000 isn't already in use
- Install dependencies: `pip install -r requirements.txt`

**Render Deployment Issues:**
- Verify environment variable is set in Render dashboard
- Check logs in Render dashboard if service fails
- Ensure `render.yaml` is committed to repo
- Free tier may sleep after inactivity (first request takes 30s)

**API Errors:**
- Verify Google API key is valid
- Check Gemini API quota/billing in Google Cloud Console

---

## Project Structure

```
chatbot-deploy/
├── main.py              # FastAPI backend
├── static/
│   └── index.html       # Chat UI
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (local only)
├── .env.example         # Template for .env
├── render.yaml          # Render deployment config
└── README.md            # This file
```

---

## Session Management

- Each user gets unique session ID (generated client-side)
- Sessions stored in-memory (resets on server restart)
- Automatic cleanup after 30 minutes inactivity
- No persistence across page refreshes (as requested)

---

## Cost Considerations

- **Render**: Free tier available (sleeps after inactivity)
- **Google Gemini API**: Pay per request (check pricing)
- Monitor usage in Google Cloud Console
