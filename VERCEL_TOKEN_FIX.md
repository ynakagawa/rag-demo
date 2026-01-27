# Vercel AEM Token Issue - URGENT FIX

## 🚨 Error in Production

```
❌ Failed to list sites
Error: Invalid character in header content ["Authorization"]
```

## ✅ Working Locally

The same token works perfectly in local environment:
- Token length: 1346 characters
- No newlines or invalid characters
- Format: Valid JWT token

## 🔍 Root Cause

The issue is likely how Vercel stores/passes the AEM_TOKEN environment variable. The token might have:
1. Extra whitespace/newlines added by Vercel UI
2. Not properly quoted when pasted
3. Truncated due to length (1346 chars)

## 🛠️ Solution: Clean the Token in Vercel

### Step 1: Remove Current Token in Vercel

1. Go to: https://vercel.com/dashboard
2. Click your "rag-demo" project
3. Settings → Environment Variables
4. Find `AEM_TOKEN`
5. Click "..." → Delete

### Step 2: Re-add Token (Carefully)

1. Click "Add New" environment variable
2. **Name:** `AEM_TOKEN` (exact spelling)
3. **Value:** Copy from command below

#### Get Clean Token:

**On Mac/Linux:**
```bash
cd /Users/ynaka/Documents/RAG-demo
cat .env | grep "^AEM_TOKEN=" | cut -d'=' -f2- | tr -d '\n\r' | pbcopy
```
This copies the clean token to your clipboard.

**Manual Copy:**
```bash
cd /Users/ynaka/Documents/RAG-demo
cat .env | grep "^AEM_TOKEN="
```
Then copy ONLY the value after `AEM_TOKEN=` (no quotes, no spaces)

4. **Paste** into Vercel value field
5. Select **all environments** (Production, Preview, Development)
6. Click "Save"

### Step 3: Verify Token Length

After pasting, verify in Vercel that:
- The value shows `1346 characters` or similar
- No truncation warning
- No extra quotes around the value

### Step 4: Force Redeploy

1. Go to Deployments tab
2. Click "..." on latest deployment
3. Click "Redeploy"

## 🧪 Test After Fix

Wait 1-2 minutes, then test:
```
https://rag-demo-one.vercel.app/
```

Query: `"list sites"`

Expected: Shows 16 AEM sites ✅

## 📋 Checklist

- [ ] Delete AEM_TOKEN from Vercel
- [ ] Copy clean token (no newlines)
- [ ] Re-add AEM_TOKEN to Vercel
- [ ] Verify 1346 characters saved
- [ ] Select all environments
- [ ] Redeploy
- [ ] Test in production

## 🔧 Alternative: Add Token Trimming in Code

If the above doesn't work, we can trim the token in code. Let me know and I'll add:

```python
aem_token = os.getenv('AEM_TOKEN', '').strip()
```

## ⚠️ Other Environment Variables

While fixing AEM_TOKEN, verify these are also set correctly:
- `OPENAI_API_KEY` (164 chars)
- `LANGSMITH_API_KEY` (51 chars)
- `LANGSMITH_PROJECT` = `rag demo`
- `AEM_SERVER` = `https://author-p18253-e46622.adobeaemcloud.com`

## 🎯 Why This Happens

Vercel's environment variable UI can sometimes:
- Add extra whitespace when pasting long values
- Not properly handle multi-line paste
- Truncate very long values

Solution: Always copy clean, single-line values without extra whitespace.

## ✅ Success Indicator

When working correctly in production, you'll see:
```
✅ Tool Executed: aem-list-sites

📁 Sites in /content
Found 16 site(s):
1. diomicrosite
2. valuebridge
...
```

---

**Action Required:** Re-add AEM_TOKEN in Vercel using clean copy method above! 🚀
