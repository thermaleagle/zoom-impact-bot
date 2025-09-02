# Railway Deployment Guide

## Quick Deployment Steps

### 1. Prepare Your Repository
- [ ] Push your code to GitHub
- [ ] Ensure all files are committed (pyproject.toml, requirements.txt, etc.)

### 2. Railway Setup
- [ ] Go to [railway.app](https://railway.app) and sign up/login
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your `zoom-impact-bot` repository
- [ ] Wait for Railway to detect Python project

### 3. Environment Variables
In Railway dashboard → Your Project → Variables tab, add:

```
BOT_TOKEN=8310364034:AAEzkZMU2s6TqlRYg3yNJuaUZrNsEVnQ-G0
GOOGLE_SERVICE_JSON={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
SHEET_NAME=Zoom Impact Bot Data
```

**Important**: 
- `GOOGLE_SERVICE_JSON` should be the **entire JSON content** from your service_account.json file
- Make sure to escape quotes properly in Railway's interface

### 4. Deploy
- [ ] Railway will automatically build and deploy
- [ ] Check the "Deployments" tab for build logs
- [ ] Check the "Logs" tab for runtime logs

### 5. Verify Deployment
- [ ] Bot should start and show: "Zoom Impact Bot starting… SHEET_NAME=Zoom Impact Bot Data"
- [ ] Test in Telegram with `/menu` command
- [ ] Verify all features work (Next, Slides, Guidelines, Recognition)

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that all dependencies are in requirements.txt
2. **Bot Doesn't Start**: Check environment variables are set correctly
3. **Google Sheets Access**: Ensure service account has access to your sheet
4. **Token Issues**: Verify BOT_TOKEN is correct

### Logs
- Railway provides real-time logs in the dashboard
- Look for startup messages and any error traces
- Bot will restart automatically if it crashes

### Environment Variables Format
```bash
# BOT_TOKEN
8310364034:AAEzkZMU2s6TqlRYg3yNJuaUZrNsEVnQ-G0

# GOOGLE_SERVICE_JSON (entire JSON content)
{"type":"service_account","project_id":"your-project-id",...}

# SHEET_NAME (optional)
Zoom Impact Bot Data
```

## Local Testing Before Deployment

Test your deployment script locally:

```bash
# Set environment variables
export BOT_TOKEN="your_token"
export GOOGLE_SERVICE_JSON='{"type":"service_account",...}'  # Full JSON
export SHEET_NAME="Zoom Impact Bot Data"

# Test the deployment script
python3 start.py
```

## Post-Deployment

1. **Monitor**: Check Railway logs regularly
2. **Update**: Push changes to GitHub for automatic redeployment
3. **Scale**: Railway handles scaling automatically
4. **Backup**: Your Google Sheets data is your backup

## Cost
- Railway offers free tier with usage limits
- Monitor usage in Railway dashboard
- Upgrade if needed for production use
