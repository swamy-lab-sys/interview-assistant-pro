from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import anthropic
import stripe

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import engine, get_db
from app.models import Base, User, UsageLog
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, generate_api_key
)
from pydantic import BaseModel, EmailStr


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Pydantic Models ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    subscription_tier: str
    questions_this_month: int
    questions_limit: int
    api_key: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class QuestionRequest(BaseModel):
    question: str
    resume: Optional[str] = None
    is_coding: bool = False


class QuestionResponse(BaseModel):
    answer: str
    tokens_used: int
    questions_remaining: int


class CheckoutResponse(BaseModel):
    checkout_url: str


# ============ Helper Functions ============

def get_questions_limit(tier: str) -> int:
    if tier == "pro" or tier == "enterprise":
        return settings.PRO_TIER_QUESTIONS_PER_MONTH
    return settings.FREE_TIER_QUESTIONS_PER_MONTH


async def check_and_reset_usage(user: User, db: AsyncSession):
    """Reset monthly usage if needed"""
    now = datetime.utcnow()
    if user.usage_reset_date is None or (now - user.usage_reset_date).days >= 30:
        user.questions_this_month = 0
        user.usage_reset_date = now
        await db.commit()


async def check_usage_limit(user: User):
    """Check if user has exceeded their usage limit"""
    limit = get_questions_limit(user.subscription_tier)
    if user.questions_this_month >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly limit of {limit} questions reached. Upgrade to Pro for unlimited access."
        )


# ============ Debug Route ============

@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to test configuration"""
    import traceback
    try:
        # Test password hashing
        test_hash = get_password_hash("test")
        hash_works = len(test_hash) > 0
    except Exception as e:
        hash_works = f"Error: {str(e)}"

    return {
        "database_url": settings.DATABASE_URL[:30] + "...",
        "hash_works": hash_works,
        "anthropic_key_set": bool(settings.ANTHROPIC_API_KEY),
    }


# ============ Auth Routes ============

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    import traceback
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            api_key=generate_api_key()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Generate token
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
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}\n{traceback.format_exc()}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

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


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await check_and_reset_usage(current_user, db)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier,
        questions_this_month=current_user.questions_this_month,
        questions_limit=get_questions_limit(current_user.subscription_tier),
        api_key=current_user.api_key
    )


@app.post("/api/auth/regenerate-api-key")
async def regenerate_api_key(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.api_key = generate_api_key()
    await db.commit()
    return {"api_key": current_user.api_key}


# ============ AI Question Route ============

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Check usage
    await check_and_reset_usage(current_user, db)
    await check_usage_limit(current_user)

    # Build prompt
    system_prompt = """You are an expert technical interview assistant. Provide clear, concise answers.

Rules:
- Start answering directly, no filler phrases like "Sure, I'd be happy to..."
- Be conversational but professional
- If it's a coding question, provide clean code with brief explanation
- Keep answers focused and interview-appropriate (1-3 minutes speaking time)
- Never invent experience - only reference what's in the resume if provided"""

    if request.resume:
        system_prompt += f"\n\nCandidate's Resume/Experience:\n{request.resume}"

    if request.is_coding:
        system_prompt += "\n\nThis is a coding question. Provide clean, working code with brief explanation."

    # Call Claude API
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": request.question}]
        )

        answer = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # Update usage
    current_user.questions_this_month += 1
    current_user.total_questions += 1

    # Log usage
    usage_log = UsageLog(
        user_id=current_user.id,
        question_text=request.question[:100] if request.question else None,  # Truncate for privacy
        response_length=len(answer),
        tokens_used=tokens_used
    )
    db.add(usage_log)
    await db.commit()

    return QuestionResponse(
        answer=answer,
        tokens_used=tokens_used,
        questions_remaining=get_questions_limit(current_user.subscription_tier) - current_user.questions_this_month
    )


# ============ Stripe Payment Routes ============

@app.post("/api/billing/create-checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": current_user.id}
        )
        current_user.stripe_customer_id = customer.id
        await db.commit()

    # Create checkout session
    checkout_session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": settings.STRIPE_PRICE_ID_MONTHLY,
            "quantity": 1
        }],
        mode="subscription",
        success_url="https://your-app.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://your-app.com/billing/cancel",
        metadata={"user_id": current_user.id}
    )

    return CheckoutResponse(checkout_url=checkout_session.url)


@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle subscription events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        if user_id:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = "pro"
                user.stripe_subscription_id = session.get("subscription")
                user.subscription_status = "active"
                await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        result = await db.execute(
            select(User).where(User.stripe_subscription_id == subscription["id"])
        )
        user = result.scalar_one_or_none()
        if user:
            user.subscription_tier = "free"
            user.subscription_status = "cancelled"
            await db.commit()

    return {"status": "success"}


@app.post("/api/billing/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    stripe.Subscription.modify(
        current_user.stripe_subscription_id,
        cancel_at_period_end=True
    )

    current_user.subscription_status = "cancelling"
    await db.commit()

    return {"message": "Subscription will be cancelled at end of billing period"}


# ============ Landing Page ============

TEMPLATES_DIR = Path(__file__).parent / "templates"


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    template_path = TEMPLATES_DIR / "index.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text())
    return HTMLResponse(content="<h1>Interview Assistant Pro API</h1><p>Version 1.0.0</p>")


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    template_path = TEMPLATES_DIR / "register.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text())
    return HTMLResponse(content="<h1>Register</h1>")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    template_path = TEMPLATES_DIR / "login.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text())
    return HTMLResponse(content="<h1>Login</h1>")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    template_path = TEMPLATES_DIR / "dashboard.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text())
    return HTMLResponse(content="<h1>Dashboard</h1>")


@app.get("/download", response_class=HTMLResponse)
async def download_page():
    template_path = TEMPLATES_DIR / "download.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text())
    return HTMLResponse(content="<h1>Download</h1>")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api")
async def api_root():
    return {"message": "Interview Assistant Pro API", "version": "1.0.0"}
