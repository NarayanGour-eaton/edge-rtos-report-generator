# GitHub Token Setup Guide

## 🔐 **GitHub Token Configuration for EATON Multi-Workflow Publisher**

The EATON multi-workflow publisher requires a GitHub token to access the GitHub Actions API. This guide shows you all the ways to configure it.

## 🚀 **Quick Setup Options**

### **Option 1: Environment Variable (Recommended)**
```batch
# Windows (PowerShell)
$env:GITHUB_TOKEN = "your_token_here"

# Windows (Command Prompt) 
set GITHUB_TOKEN=your_token_here

# Add to system environment variables for permanent setup
```

### **Option 2: Configuration File**
Edit `workflow_runs.json`:
```json
{
  "settings": {
    "github_token": "your_token_here",
    "repo_owner": "etn-ccis",
    "repo_name": "edge-rtos-github-builds"
  }
}
```

### **Option 3: Command Line**
```bash
python multi_publisher.py --github-token "your_token_here"
```

### **Option 4: Interactive Prompt**
The script will automatically prompt for the token if not found:
```
🔐 GitHub Token Configuration
---------------------------------
A GitHub token is required to access GitHub Actions API.
Enter GitHub token (hidden input): ****
✅ GitHub token entered successfully
```

## 📋 **Creating a GitHub Token**

### **Step-by-Step Instructions:**

1. **Go to GitHub Settings**: https://github.com/settings/tokens
2. **Click "Generate new token"** → "Generate new token (classic)"
3. **Set Token Name**: e.g., "EATON Regression Reports"
4. **Set Expiration**: Choose appropriate duration (90 days, 1 year, etc.)
5. **Select Permissions**:
   - ✅ **`repo`** (Full repository access) **OR**
   - ✅ **`actions:read`** (Read access to Actions) **AND**
   - ✅ **`metadata:read`** (Read repository metadata)
6. **Click "Generate token"**
7. **Copy the token** (you won't see it again!)

### **Required Permissions:**
```
For private repositories:
✅ repo (full access)

For public repositories (minimum):
✅ actions:read
✅ metadata:read
```

## 🛠️ **Usage Examples**

### **Daily Workflow with Environment Variable**
```batch
# Set once (permanent)
setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Then run normally
run_multi_workflow_report.bat
```

### **One-time Usage**
```bash
# With command line token
python multi_publisher.py --github-token "ghp_xxxx" --interactive

# Or let it prompt you
python multi_publisher.py --interactive
```

### **Batch/Automated Usage**
```bash
# Skip interactive prompts
python multi_publisher.py --no-token-prompt
```

## ⚠️ **Security Best Practices**

### **DO:**
- ✅ Use environment variables for daily workflow
- ✅ Set token expiration dates
- ✅ Use minimal required permissions
- ✅ Store tokens securely (password manager)
- ✅ Regenerate tokens periodically

### **DON'T:**
- ❌ Commit tokens to version control
- ❌ Share tokens in emails or chat
- ❌ Use tokens with unnecessary permissions
- ❌ Set tokens to never expire
- ❌ Store tokens in plain text files

### **Token Storage Priority:**
The script checks for tokens in this order:
1. **Command line argument** (`--github-token`)
2. **Configuration file** (`workflow_runs.json`)
3. **Environment variable** (`GITHUB_TOKEN`)
4. **Main config file** (`config.json`)
5. **Interactive prompt** (if in interactive mode)

## 🔍 **Troubleshooting**

### **Common Issues:**

**❌ "HTTP 401 Unauthorized"**
```
Solution: Token is invalid or expired
- Check token hasn't expired
- Verify token has correct permissions
- Regenerate token if needed
```

**❌ "HTTP 403 Forbidden"**
```
Solution: Insufficient permissions
- Add 'repo' permission for private repos
- Add 'actions:read' for public repos
- Verify repo owner/name is correct
```

**❌ "API rate limit exceeded"**
```
Solution: No token or wrong token
- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour
- Verify token is being used
```

### **Testing Your Token:**
```bash
# Test token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Test repository access
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/etn-ccis/edge-rtos-github-builds
```

## 📊 **Token Usage in Reports**

When configured correctly, you'll see:
```
✅ GitHub token configured: ghp_****...****
📊 Processing 2 workflows:
   • BFT_U575zi_q_dev: Run ID 17890913910 (H743)
   • BFT_h743zi_dev: Run ID 17890913911 (U575)
```

Without token:
```
⚠️ WARNING: No GitHub token configured!
   - API rate limits will be very low (60 requests/hour)
   - You may encounter authentication errors
```

## 🎯 **For EATON Team Usage**

### **Recommended Setup:**
1. **Individual tokens**: Each team member creates their own token
2. **Environment variable**: Set `GITHUB_TOKEN` in Windows environment
3. **Shared config**: Use `workflow_runs.json` for run IDs only (not tokens)
4. **CI/CD integration**: Use GitHub secrets for automated runs

### **Team Workflow:**
```batch
# One-time setup per developer
setx GITHUB_TOKEN "your_personal_token"

# Daily usage (no token prompts)
run_multi_workflow_report.bat
```

This ensures secure, efficient access to GitHub Actions data for all EATON regression reporting workflows.

---

## 🔗 **Quick Links**

- **Create Token**: https://github.com/settings/tokens
- **GitHub API Docs**: https://docs.github.com/en/rest/actions
- **Token Permissions**: https://docs.github.com/en/developers/apps/scopes-for-oauth-apps

**Need Help?** Check the console output - the script provides detailed guidance for token configuration!