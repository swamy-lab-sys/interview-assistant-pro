# Interview Assistant Pro - SaaS Backend

This is the monetizable SaaS backend for Interview Assistant Pro.

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────┐
│   User's Computer   │         │   Your Server (Render)   │
│                     │         │                          │
│  ┌───────────────┐  │         │  ┌────────────────────┐  │
│  │ Local Client  │  │  API    │  │  FastAPI Backend   │  │
│  │ - Audio       │──┼────────►│  │  - Auth/Users      │  │
│  │ - Whisper STT │  │         │  │  - Stripe Billing  │  │
│  │ - Display     │◄─┼─────────│  │  - Claude Proxy    │  │
│  └───────────────┘  │         │  │  - Usage Tracking  │  │
│                     │         │  └────────────────────┘  │
└─────────────────────┘         │           │              │
                                │           ▼              │
                                │  ┌────────────────────┐  │
                                │  │  PostgreSQL DB     │  │
                                │  │  - Users           │  │
                                │  │  - Subscriptions   │  │
                                │  │  - Usage Logs      │  │
                                │  └────────────────────┘  │
                                └──────────────────────────┘
```

## Features

- **User Authentication** - Email/password registration and login
- **API Key Management** - Each user gets unique API key for local client
- **Stripe Integration** - Subscription payments ($29/month Pro tier)
- **Usage Tracking** - Monitor questions per user per month
- **Free Tier** - 50 questions/month to attract users
- **Claude AI Proxy** - Your API key, users don't need their own

## Quick Deploy to Render

1. Push this code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create New → Blueprint
4. Connect your repo, select the `saas_backend` folder
5. Set environment variables:
   - `ANTHROPIC_API_KEY` - Your Claude API key
   - `STRIPE_SECRET_KEY` - From Stripe dashboard
   - `STRIPE_WEBHOOK_SECRET` - From Stripe webhooks
   - `STRIPE_PRICE_ID_MONTHLY` - Create a $29/month product in Stripe

## Stripe Setup

1. Create account at [stripe.com](https://stripe.com)
2. Create a Product: "Interview Assistant Pro - $29/month"
3. Get the Price ID (starts with `price_`)
4. Set up webhook endpoint: `https://your-app.onrender.com/api/billing/webhook`
5. Add webhook secret to environment variables

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get account info
- `POST /api/auth/regenerate-api-key` - New API key

### AI
- `POST /api/ask` - Ask interview question (requires auth)

### Billing
- `POST /api/billing/create-checkout` - Get Stripe checkout URL
- `POST /api/billing/webhook` - Stripe webhook handler
- `POST /api/billing/cancel` - Cancel subscription

## Local Development

```bash
cd saas_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your-key
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID_MONTHLY=price_...
EOF

# Run server
uvicorn app.main:app --reload
```

## Revenue Potential

| Users | Free (50%) | Pro (50%) | Monthly Revenue |
|-------|------------|-----------|-----------------|
| 100   | 50         | 50        | $1,450          |
| 500   | 250        | 250       | $7,250          |
| 1000  | 500        | 500       | $14,500         |
| 5000  | 2500       | 2500      | $72,500         |

## Costs

- **Render**: Free tier or $7/month for better performance
- **PostgreSQL**: Free on Render
- **Claude API**: ~$0.50 per hour of interview (with caching)
- **Stripe**: 2.9% + $0.30 per transaction

## Marketing Ideas

1. **Product Hunt Launch** - Great for dev tools
2. **LinkedIn Ads** - Target job seekers
3. **Reddit** - r/cscareerquestions, r/leetcode
4. **YouTube** - Demo videos, interview tips
5. **SEO** - Blog posts about interview prep
6. **Affiliate Program** - Let users earn referral fees
