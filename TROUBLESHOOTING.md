# Interview Assistant Pro - Troubleshooting Guide

## Current Issue: Login Not Working on Render.com

### Symptoms
- User registers successfully
- Login fails or returns errors
- Dashboard not accessible

---

## Potential Causes & Fixes

### 1. Database Not Persisting (Most Likely)

**Problem:** Render free tier uses ephemeral filesystem - SQLite database resets on each deploy/restart.

**Fix:** Switch to PostgreSQL or use Render's persistent disk.

**File to edit:** `saas_backend/app/config.py`

```python
# Current (SQLite - doesn't persist on Render):
DATABASE_URL: str = "sqlite+aiosqlite:///./interview_assistant.db"

# Change to PostgreSQL:
DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./interview_assistant.db")
```

**Then in Render Dashboard:**
1. Add PostgreSQL database (or use external free one like Neon.tech)
2. Add environment variable: `DATABASE_URL=postgresql+asyncpg://user:pass@host/db`

---

### 2. JWT Secret Key Issue

**Problem:** SECRET_KEY not set or changes between restarts.

**Check in Render Dashboard → Environment Variables:**
```
SECRET_KEY=<generate-a-random-32-char-string>
```

**Generate a key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 3. CORS Issue

**Problem:** Frontend and API on same domain but CORS blocking.

**File:** `saas_backend/app/main.py` (line 43-49)

**Current:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check:** `saas_backend/app/config.py`
```python
CORS_ORIGINS: str = "*"  # Should allow all for testing
```

---

### 4. Password Hashing Issue (bcrypt)

**Problem:** bcrypt version mismatch causing password verification to fail.

**File:** `saas_backend/requirements.txt`

**Ensure this line exists:**
```
bcrypt>=4.0.0,<5.0.0
```

**NOT bcrypt 5.x** (has breaking changes with passlib)

---

### 5. API Key Authentication vs JWT

**Problem:** Client uses API key (`iva_xxx`), web uses JWT token.

**Auth flow in `saas_backend/app/auth.py`:**
- Web login → Returns JWT token → Stored in localStorage
- Client → Uses API key from dashboard

**Check `get_current_active_user` function handles both:**
```python
# Should check for both:
# 1. Bearer <jwt_token>
# 2. Bearer <api_key> (starts with "iva_")
```

---

## Files to Review

| File | Purpose |
|------|---------|
| `saas_backend/app/main.py` | API routes, login/register endpoints |
| `saas_backend/app/auth.py` | JWT creation, password hashing, API key auth |
| `saas_backend/app/config.py` | Database URL, secret key, settings |
| `saas_backend/app/models.py` | User model, database schema |
| `saas_backend/app/database.py` | Database connection |
| `saas_backend/app/templates/login.html` | Login form, JS fetch calls |
| `saas_backend/app/templates/dashboard.html` | Dashboard, token usage |

---

## Debug Steps

### 1. Check API Health
```bash
curl https://interview-assistant-api-pro.onrender.com/health
# Should return: {"status":"healthy"}
```

### 2. Check Debug Endpoint
```bash
curl https://interview-assistant-api-pro.onrender.com/api/debug
# Shows: database_url, hash_works, anthropic_key_set
```

### 3. Test Registration
```bash
curl -X POST https://interview-assistant-api-pro.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"testpass123"}'
```

### 4. Test Login
```bash
curl -X POST https://interview-assistant-api-pro.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"testpass123"}'
```

### 5. Check Render Logs
Go to Render Dashboard → Your Service → Logs

Look for:
- Database connection errors
- Password hash errors
- JWT decode errors

---

## Environment Variables Needed on Render

```
SECRET_KEY=<random-64-char-hex-string>
ANTHROPIC_API_KEY=sk-ant-xxxxx
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname  (optional, for PostgreSQL)
CORS_ORIGINS=*
```

---

## Quick Fix: Add Better Error Logging

Edit `saas_backend/app/main.py`, update login endpoint:

```python
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    import traceback
    try:
        result = await db.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_access_token(data={"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                questions_this_month=user.questions_this_month,
                questions_limit=get_questions_limit(user.subscription_tier),
                api_key=user.api_key
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}\n{traceback.format_exc()}")
```

---

## Project Structure

```
/home/venkat/InterviewVoiceAssistant/
├── saas_backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, all routes
│   │   ├── auth.py          # Authentication logic
│   │   ├── config.py        # Settings (DATABASE_URL, SECRET_KEY)
│   │   ├── database.py      # DB connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── templates/
│   │       ├── index.html
│   │       ├── register.html
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       └── download.html
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml
├── interview_assistant_client.py  # Distributable client
├── interview_pro_client.py        # Voice mode client
└── dist/
    └── InterviewAssistant-Linux   # Built executable
```

---

## Deployed URLs

| Service | URL |
|---------|-----|
| Main Site | https://interview-assistant-api-pro.onrender.com |
| Register | https://interview-assistant-api-pro.onrender.com/register |
| Login | https://interview-assistant-api-pro.onrender.com/login |
| Dashboard | https://interview-assistant-api-pro.onrender.com/dashboard |
| Download | https://interview-assistant-api-pro.onrender.com/download |
| Health Check | https://interview-assistant-api-pro.onrender.com/health |
| Debug | https://interview-assistant-api-pro.onrender.com/api/debug |

---

## GitHub

- Repo: https://github.com/swamy-lab-sys/interview-assistant-pro
- Release: https://github.com/swamy-lab-sys/interview-assistant-pro/releases/tag/v1.0.0
- Download: https://github.com/swamy-lab-sys/interview-assistant-pro/releases/download/v1.0.0/InterviewAssistant-Linux

---

## Next Steps

1. Check `/api/debug` endpoint for configuration status
2. Check Render logs for specific error messages
3. If database issue → Add PostgreSQL (Neon.tech free tier)
4. If bcrypt issue → Verify requirements.txt has `bcrypt>=4.0.0,<5.0.0`
5. Test with curl commands above to isolate the issue
