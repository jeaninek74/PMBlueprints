# PMBlueprints API Documentation

Complete API reference for the PMBlueprints platform.

## Base URL

**Production:** `https://pmblueprints-production.vercel.app`

## Authentication

Most API endpoints require authentication. Use one of the following methods:

### Session-Based Authentication
1. Login via `/auth/login` endpoint
2. Session cookie will be set automatically
3. Include cookie in subsequent requests

### Demo Access
- Use `/demo-login` endpoint for testing
- Provides full Professional plan access

## API Endpoints

### Templates API

#### List All Templates
```http
GET /api/templates
```

**Query Parameters:**
- `industry` (optional) - Filter by industry
- `category` (optional) - Filter by category
- `search` (optional) - Search templates by name/description

**Response:**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Project Charter",
      "description": "Professional charter template...",
      "industry": "General",
      "category": "Project Planning",
      "downloads": 0,
      "rating": 4.5,
      "file_type": "xlsx",
      "file_size": 52428
    }
  ],
  "total": 964
}
```

#### Get Template Details
```http
GET /api/templates/<id>
```

**Response:**
```json
{
  "id": 1,
  "name": "Project Charter",
  "description": "Professional charter template for general projects...",
  "industry": "General",
  "category": "Project Planning",
  "downloads": 0,
  "rating": 4.5,
  "file_type": "xlsx",
  "file_size": 52428,
  "has_formulas": true,
  "has_fields": true,
  "pmi_compliant": true,
  "integration_ready": true
}
```

#### Download Template
```http
POST /api/templates/<id>/download
```

**Authentication:** Required

**Response:**
- File download (Excel/Word format)
- Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

---

### AI Generation API

#### Generate Custom Template
```http
POST /api/ai/generate
```

**Authentication:** Required

**Request Body:**
```json
{
  "description": "Create a risk management plan for a software project",
  "industry": "Technology",
  "project_type": "Software Development",
  "additional_requirements": "Include GDPR compliance section"
}
```

**Response:**
```json
{
  "success": true,
  "template": {
    "content": "# Risk Management Plan\n\n...",
    "format": "markdown",
    "quality_score": 0.95,
    "bias_score": 0.02
  },
  "metadata": {
    "generation_time": 2.3,
    "model": "gpt-4",
    "tokens_used": 1500
  }
}
```

#### Get AI Suggestions
```http
GET /api/ai/suggestions
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": 1,
      "category": "Risk Management",
      "priority": "high",
      "title": "Review project risk register",
      "description": "Conduct weekly risk assessment...",
      "action_url": "/templates?category=Risk+Management"
    }
  ],
  "total": 45
}
```

#### Get AI Metrics
```http
GET /api/ai/metrics
```

**Authentication:** Required (Admin only)

**Response:**
```json
{
  "total_generations": 1250,
  "avg_quality_score": 0.92,
  "avg_generation_time": 2.1,
  "total_tokens_used": 1500000
}
```

---

### Payment API

#### Get Pricing Plans
```http
GET /payment/api/plans
```

**Response:**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price": 0,
      "interval": "month",
      "features": [
        "10 template downloads",
        "Basic templates",
        "Email support"
      ]
    },
    {
      "id": "professional",
      "name": "Professional",
      "price": 29,
      "interval": "month",
      "features": [
        "Unlimited downloads",
        "All 960+ templates",
        "AI template generation",
        "Platform integrations",
        "Priority support"
      ],
      "popular": true
    },
    {
      "id": "enterprise",
      "name": "Enterprise",
      "price": 99,
      "interval": "month",
      "features": [
        "Everything in Professional",
        "Custom templates",
        "Advanced analytics",
        "Dedicated support",
        "White-label options"
      ]
    }
  ]
}
```

#### Subscribe to Plan
```http
POST /payment/api/subscribe
```

**Authentication:** Required

**Request Body:**
```json
{
  "plan_id": "professional"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subscription activated",
  "subscription": {
    "plan": "professional",
    "status": "active",
    "current_period_end": "2025-11-11T00:00:00Z"
  }
}
```

#### Cancel Subscription
```http
POST /payment/api/cancel
```

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "Subscription cancelled",
  "cancellation_date": "2025-11-11T00:00:00Z"
}
```

---

### Monitoring API

#### Health Check
```http
GET /api/monitoring/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T23:00:00Z",
  "uptime": 86400,
  "version": "1.0.0"
}
```

#### Get Performance Metrics
```http
GET /api/monitoring/metrics
```

**Response:**
```json
{
  "requests": {
    "total": 10000,
    "successful": 9950,
    "failed": 50,
    "error_rate": 0.005
  },
  "performance": {
    "avg_response_time": 185,
    "min_response_time": 50,
    "max_response_time": 2500
  },
  "cache": {
    "hits": 8500,
    "misses": 1500,
    "hit_rate": 0.85
  }
}
```

#### Get Detailed Statistics
```http
GET /api/monitoring/stats
```

**Authentication:** Required (Admin only)

**Response:**
```json
{
  "requests": {
    "total": 10000,
    "by_endpoint": {
      "/api/templates": 5000,
      "/api/ai/generate": 1000,
      "/": 4000
    }
  },
  "errors": {
    "total": 50,
    "by_type": {
      "404": 30,
      "500": 15,
      "403": 5
    }
  },
  "activity": {
    "downloads": 2500,
    "ai_generations": 1000,
    "active_users": 150
  }
}
```

---

## Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": true,
  "message": "Error description",
  "code": "ERROR_CODE",
  "status": 400
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RATE_LIMIT` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Free Plan:** 100 requests/hour
- **Professional Plan:** 1000 requests/hour
- **Enterprise Plan:** 10000 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1633046400
```

---

## Webhooks

### Stripe Webhooks

PMBlueprints listens for Stripe webhook events:

**Endpoint:** `POST /payment/webhook`

**Events:**
- `payment_intent.succeeded` - Payment successful
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Subscription changed
- `customer.subscription.deleted` - Subscription cancelled

---

## SDK & Libraries

### Python Example
```python
import requests

# Get all templates
response = requests.get('https://pmblueprints-production.vercel.app/api/templates')
templates = response.json()['templates']

# Generate AI template
data = {
    'description': 'Risk management plan',
    'industry': 'Technology'
}
response = requests.post(
    'https://pmblueprints-production.vercel.app/api/ai/generate',
    json=data,
    cookies={'session': 'your_session_cookie'}
)
template = response.json()['template']
```

### JavaScript Example
```javascript
// Get all templates
fetch('https://pmblueprints-production.vercel.app/api/templates')
  .then(res => res.json())
  .then(data => console.log(data.templates));

// Generate AI template
fetch('https://pmblueprints-production.vercel.app/api/ai/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    description: 'Risk management plan',
    industry: 'Technology'
  }),
  credentials: 'include'
})
  .then(res => res.json())
  .then(data => console.log(data.template));
```

---

## Support

For API support and questions:
- **Email:** api@pmblueprints.com
- **Documentation:** https://pmblueprints-production.vercel.app/docs
- **GitHub Issues:** https://github.com/jeaninek74/PMBlueprints/issues

---

*Last Updated: October 11, 2025*

