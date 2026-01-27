# Vercel Environment Variables Setup

## 🚨 Action Required: Add Environment Variables to Vercel

Your code is deployed but **environment variables are missing** in Vercel. This causes AEM tools to fail in production.

## ✅ Step-by-Step Instructions

### 1. Go to Vercel Dashboard

Visit: https://vercel.com/dashboard

### 2. Navigate to Project Settings

1. Click on your **"rag-demo"** project
2. Click **"Settings"** tab (top navigation)
3. Click **"Environment Variables"** (left sidebar)

### 3. Add Each Variable

Click **"Add New"** and add these 5 variables:

#### Variable 1: OPENAI_API_KEY
- **Name:** `OPENAI_API_KEY`
- **Value:** Copy from your `.env` file (starts with `sk-proj-...`)
- **Environment:** Select all (Production, Preview, Development)

#### Variable 2: LANGSMITH_API_KEY
- **Name:** `LANGSMITH_API_KEY`
- **Value:** Copy from your `.env` file (starts with `lsv2_pt_...`)
- **Environment:** Select all

#### Variable 3: LANGSMITH_PROJECT
- **Name:** `LANGSMITH_PROJECT`
- **Value:** `rag demo`
- **Environment:** Select all

#### Variable 4: AEM_SERVER
- **Name:** `AEM_SERVER`
- **Value:** `https://author-p18253-e46622.adobeaemcloud.com`
- **Environment:** Select all

#### Variable 5: AEM_TOKEN
- **Name:** `AEM_TOKEN`
- **Value:** Copy the entire token from your `.env` file (1346 characters starting with `eyJhbGc...`)
- **Environment:** Select all

### 4. Copy Values from Local .env

To get the exact values, open your local `.env` file:

```bash
# Location
/Users/ynaka/Documents/RAG-demo/.env

# Contents to copy:
OPENAI_API_KEY=sk-proj-oja-ul6ZaYIK... (164 characters)
LANGSMITH_API_KEY=lsv2_pt_e901c344292a... (51 characters)
LANGSMITH_PROJECT=rag demo
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_TOKEN=eyJhbGciOiJSUzI1NiIs... (1346 characters - copy entire value)
```

**⚠️ IMPORTANT:** Copy the **entire** value for each variable, especially the long tokens!

### 5. Redeploy (Automatic)

After adding all variables:
1. Vercel will automatically redeploy your app
2. Wait 1-2 minutes for the deployment to complete
3. Test at: https://rag-demo-one.vercel.app/

## 🧪 Testing After Setup

Try these queries on production:

### ✅ Should Work After Setup:
- "can you list my AEM sites" → Shows list of 16 sites
- "list templates" → Shows available templates
- "get info for diomicrosite" → Shows site info
- "calculate 5 + 3" → Returns 8

### 📚 Should Work Already:
- "what is AEM?" → Returns documentation answer
- "how does AEM work?" → Returns documentation answer

## 🔍 Verify Variables Are Set

After adding variables, go to:
1. Vercel Dashboard → Your Project
2. Settings → Environment Variables
3. You should see 5 variables listed

## ❌ Troubleshooting

### Issue: Still not working after adding variables

**Solution:** Manually trigger a redeploy
1. Go to Deployments tab in Vercel
2. Click the three dots (...) on the latest deployment
3. Click "Redeploy"

### Issue: Token expired error

**Solution:** Generate a new AEM token
1. Get new token from AEM Developer Console
2. Update `AEM_TOKEN` in Vercel
3. Update locally in `.env` file too
4. Redeploy

### Issue: "Missing environment variable" error

**Solution:** Make sure all 5 variables are set
- Check spelling exactly matches (case-sensitive)
- Verify all environments are selected (Production, Preview, Development)
- No extra spaces in names or values

## 📊 Current Configuration

**Local (.env):**
- ✅ All variables configured
- ✅ Working correctly

**Vercel (Production):**
- ⚠️ Variables need to be added
- 🔧 Action required: Follow steps above

## 🔐 Security Notes

- ✅ Never commit `.env` to git (already in `.gitignore`)
- ✅ Vercel environment variables are encrypted
- ✅ Variables are only accessible to your backend functions
- ✅ Never exposed to browser/frontend
- ⚠️ Rotate tokens regularly
- ⚠️ Use service accounts for production

## 📝 Quick Checklist

- [ ] Go to Vercel Dashboard
- [ ] Navigate to Settings → Environment Variables
- [ ] Add `OPENAI_API_KEY`
- [ ] Add `LANGSMITH_API_KEY`
- [ ] Add `LANGSMITH_PROJECT`
- [ ] Add `AEM_SERVER`
- [ ] Add `AEM_TOKEN` (entire 1346 character value)
- [ ] Wait for automatic redeploy
- [ ] Test at https://rag-demo-one.vercel.app/
- [ ] Try "can you list my AEM sites"

## ✅ Success Criteria

When properly configured, you should see:

```
User: "can you list my AEM sites"

Response:
✅ Tool Executed: aem-list-sites

📁 Sites in /content

Found 16 site(s):

1. diomicrosite
2. valuebridge
3. demo
...
```

## 🎯 Why This Is Needed

- **Local:** Variables loaded from `.env` file ✅
- **Vercel:** No `.env` file (gitignored) → Must add manually ⚠️

The same code that works locally needs the same environment variables in production!

---

**Next Step:** Add the 5 environment variables in Vercel Settings now! 🚀
