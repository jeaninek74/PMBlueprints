# PMBlueprints Performance Monitoring

## Overview

The PMBlueprints platform includes comprehensive Application Performance Monitoring (APM) to track system health, performance metrics, user activity, and error rates in real-time.

## Features

### 1. **Real-Time Metrics Tracking**

The monitoring system automatically tracks:

- **Request Metrics**
  - Total requests per endpoint
  - Average response times
  - Min/max response times
  - Request distribution

- **Error Tracking**
  - Error count per endpoint
  - Error rate percentage
  - Error context and details

- **User Activity**
  - Template downloads
  - AI template generations
  - Active user count

- **Performance Metrics**
  - Database query times
  - Cache hit/miss rates
  - Slow query detection

### 2. **Monitoring Endpoints**

#### Health Check
```
GET /api/monitoring/health
```

Returns system health status and uptime information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T21:00:00.000Z",
  "uptime": "N/A (stateless serverless)"
}
```

#### Performance Metrics
```
GET /api/monitoring/metrics
```

Returns aggregated performance metrics.

**Response:**
```json
{
  "total_requests": 1250,
  "total_errors": 5,
  "endpoints": {
    "index": {
      "requests": 450,
      "avg_response_time": 125.5,
      "min_response_time": 45.2,
      "max_response_time": 350.8,
      "errors": 0
    }
  },
  "cache": {
    "hits": 850,
    "misses": 150,
    "hit_rate": 85.0
  },
  "activity": {
    "template_downloads": 320,
    "ai_generations": 45,
    "active_users": 78
  }
}
```

#### Detailed Statistics
```
GET /api/monitoring/stats
```

Returns comprehensive statistics including top endpoints, error rates, and slow queries.

### 3. **Monitoring Dashboard**

Access the visual monitoring dashboard at:
```
/monitoring/dashboard
```

**Features:**
- Real-time metrics visualization
- Interactive charts (Chart.js)
- Endpoint performance table
- Auto-refresh every 30 seconds
- Responsive design (Bootstrap 5)

**Dashboard Sections:**
1. **System Health** - Overall system status
2. **Key Metrics** - Total requests, avg response time, error rate, cache hit rate
3. **Activity Metrics** - Downloads, AI generations, active users
4. **Top Endpoints** - Bar chart of most-requested endpoints
5. **Response Time Distribution** - Line chart of response times
6. **Endpoint Details Table** - Detailed performance breakdown

### 4. **Automatic Performance Tracking**

The monitoring system automatically tracks performance for all requests using Flask middleware:

```python
from monitoring import monitor

# Initialize monitoring with Flask app
monitor.init_app(app)
```

**What's Tracked:**
- Request start time (before_request)
- Response time calculation (after_request)
- Error logging (teardown_request)
- Performance headers added to responses

**Response Headers:**
```
X-Response-Time: 125.50ms
X-Request-ID: 1728678000.123-192.168.1.1
```

### 5. **Custom Tracking Functions**

Track specific events in your code:

```python
from monitoring import (
    track_template_download,
    track_ai_generation,
    track_user_activity,
    track_database_query,
    track_cache_hit,
    track_cache_miss
)

# Track template download
track_template_download(template_id=123)

# Track AI generation
track_ai_generation(user_id='user123')

# Track user activity
track_user_activity(user_id='user123')

# Track database query performance
track_database_query(query='SELECT * FROM templates', execution_time=45.2)

# Track cache operations
track_cache_hit()
track_cache_miss()
```

### 6. **Performance Monitoring Decorator**

Use the `@monitor_performance` decorator to track function execution time:

```python
from monitoring import monitor_performance

@monitor_performance
def expensive_operation():
    # Your code here
    pass
```

**Features:**
- Automatic execution time tracking
- Logs warning if function takes > 500ms
- Error tracking and logging

### 7. **Error Logging**

Enhanced error logging with context:

```python
from monitoring import log_error

try:
    # Your code
    pass
except Exception as e:
    log_error(e, context={
        'user_id': user_id,
        'template_id': template_id,
        'action': 'download'
    })
```

**Error Log Format:**
```json
{
  "timestamp": "2025-10-11T21:00:00.000Z",
  "error": "File not found",
  "type": "FileNotFoundError",
  "context": {
    "user_id": "user123",
    "template_id": 456
  },
  "endpoint": "templates.download",
  "method": "GET",
  "url": "https://pmblueprints.com/templates/456/download"
}
```

## Configuration

### Environment Variables

No additional environment variables required. The monitoring system works out-of-the-box.

### Storage

Currently uses in-memory storage for metrics. For production at scale, consider:

1. **Redis** - For distributed metrics storage
2. **PostgreSQL** - For persistent metrics history
3. **Time-series database** - InfluxDB, TimescaleDB for advanced analytics

### Integration with External APM Services

The monitoring module is designed to integrate with external APM services:

#### Sentry (Error Tracking)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

#### New Relic (APM)
```python
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

app = Flask(__name__)
```

#### Datadog (APM)
```python
from ddtrace import patch_all
patch_all()
```

## Performance Optimization Tips

### 1. **Slow Request Detection**

Requests taking > 1000ms are automatically logged as warnings:
```
WARNING: Slow request: templates.download took 1250.50ms
```

### 2. **Slow Query Detection**

Database queries > 100ms are flagged in the `/api/monitoring/stats` endpoint.

### 3. **Cache Optimization**

Monitor cache hit rate to optimize caching strategy:
- **Target:** > 80% cache hit rate
- **Action:** If < 80%, review caching strategy

### 4. **Error Rate Monitoring**

Monitor error rate to identify issues:
- **Target:** < 1% error rate
- **Action:** If > 1%, investigate error logs

### 5. **Response Time Targets**

Recommended response time targets:
- **API endpoints:** < 200ms
- **Page loads:** < 500ms
- **Database queries:** < 100ms
- **AI generation:** < 5000ms

## Alerts and Notifications

### Setting Up Alerts

For production environments, set up alerts for:

1. **High Error Rate** - > 5% errors in 5-minute window
2. **Slow Response Times** - Average > 1000ms for 5 minutes
3. **High Request Volume** - > 1000 requests/minute
4. **Low Cache Hit Rate** - < 70% for 10 minutes

### Alert Channels

Configure alerts through:
- Email notifications
- Slack webhooks
- PagerDuty integration
- SMS alerts (Twilio)

## Best Practices

### 1. **Regular Monitoring**

- Check dashboard daily
- Review weekly performance trends
- Investigate anomalies immediately

### 2. **Performance Baselines**

Establish baselines for:
- Average response time
- Typical request volume
- Normal error rate

### 3. **Capacity Planning**

Use metrics to plan for:
- Traffic spikes
- Database scaling
- Cache optimization
- CDN configuration

### 4. **Security Monitoring**

Monitor for:
- Unusual request patterns
- High error rates (potential attacks)
- Suspicious user activity

## Troubleshooting

### Dashboard Not Loading

1. Check if monitoring blueprint is registered
2. Verify user is authenticated
3. Check browser console for errors

### Metrics Not Updating

1. Verify monitoring middleware is initialized
2. Check if requests are being tracked
3. Review application logs

### High Memory Usage

If in-memory metrics storage grows too large:
1. Implement metric rotation (keep last 1000 entries)
2. Move to Redis for distributed storage
3. Archive old metrics to database

## Future Enhancements

Planned improvements:

1. **Persistent Metrics Storage** - PostgreSQL/Redis integration
2. **Advanced Analytics** - Trend analysis, anomaly detection
3. **Custom Dashboards** - User-configurable dashboards
4. **Alert Management** - Built-in alerting system
5. **API Rate Limiting** - Per-user rate limit tracking
6. **Geographic Analytics** - Request distribution by region
7. **User Journey Tracking** - End-to-end user flow analysis

## Support

For monitoring-related issues:
- Check application logs
- Review this documentation
- Contact support at https://help.manus.im

---

**Last Updated:** October 11, 2025  
**Version:** 1.0  
**Author:** Manus AI

