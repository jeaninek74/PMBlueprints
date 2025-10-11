"""
PMBlueprints Performance Monitoring Module
Comprehensive application performance monitoring and metrics tracking
"""

import os
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

# Performance metrics storage (in-memory for now, can be moved to Redis/database)
performance_metrics = {
    'requests': defaultdict(int),
    'response_times': defaultdict(list),
    'errors': defaultdict(int),
    'template_downloads': defaultdict(int),
    'ai_generations': defaultdict(int),
    'user_activity': defaultdict(int),
    'database_queries': defaultdict(list),
    'cache_hits': 0,
    'cache_misses': 0
}

class PerformanceMonitor:
    """Application Performance Monitoring (APM) class"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize monitoring with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
        # Register monitoring routes
        from flask import Blueprint, jsonify
        monitor_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
        
        @monitor_bp.route('/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': self.get_uptime()
            })
        
        @monitor_bp.route('/metrics')
        def get_metrics():
            """Get performance metrics"""
            return jsonify(self.get_performance_metrics())
        
        @monitor_bp.route('/stats')
        def get_stats():
            """Get detailed statistics"""
            return jsonify(self.get_detailed_stats())
        
        app.register_blueprint(monitor_bp)
    
    def before_request(self):
        """Track request start time"""
        g.start_time = time.time()
        g.request_id = f"{datetime.utcnow().timestamp()}-{request.remote_addr}"
    
    def after_request(self, response):
        """Track request completion and metrics"""
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # Convert to ms
            
            # Track metrics
            endpoint = request.endpoint or 'unknown'
            performance_metrics['requests'][endpoint] += 1
            performance_metrics['response_times'][endpoint].append(response_time)
            
            # Log slow requests (> 1000ms)
            if response_time > 1000:
                logger.warning(f"Slow request: {endpoint} took {response_time:.2f}ms")
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response
    
    def teardown_request(self, exception=None):
        """Track errors"""
        if exception:
            endpoint = request.endpoint or 'unknown'
            performance_metrics['errors'][endpoint] += 1
            logger.error(f"Request error in {endpoint}: {exception}")
    
    def get_uptime(self):
        """Get application uptime"""
        # This is a simplified version; in production, track actual start time
        return "N/A (stateless serverless)"
    
    def get_performance_metrics(self):
        """Get aggregated performance metrics"""
        metrics = {
            'total_requests': sum(performance_metrics['requests'].values()),
            'total_errors': sum(performance_metrics['errors'].values()),
            'endpoints': {},
            'cache': {
                'hits': performance_metrics['cache_hits'],
                'misses': performance_metrics['cache_misses'],
                'hit_rate': self._calculate_cache_hit_rate()
            },
            'activity': {
                'template_downloads': sum(performance_metrics['template_downloads'].values()),
                'ai_generations': sum(performance_metrics['ai_generations'].values()),
                'active_users': sum(performance_metrics['user_activity'].values())
            }
        }
        
        # Calculate average response times per endpoint
        for endpoint, times in performance_metrics['response_times'].items():
            if times:
                metrics['endpoints'][endpoint] = {
                    'requests': performance_metrics['requests'][endpoint],
                    'avg_response_time': sum(times) / len(times),
                    'min_response_time': min(times),
                    'max_response_time': max(times),
                    'errors': performance_metrics['errors'][endpoint]
                }
        
        return metrics
    
    def get_detailed_stats(self):
        """Get detailed statistics for dashboard"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'performance': self.get_performance_metrics(),
            'top_endpoints': self._get_top_endpoints(10),
            'error_rate': self._calculate_error_rate(),
            'slow_queries': self._get_slow_queries()
        }
    
    def _calculate_cache_hit_rate(self):
        """Calculate cache hit rate percentage"""
        total = performance_metrics['cache_hits'] + performance_metrics['cache_misses']
        if total == 0:
            return 0.0
        return (performance_metrics['cache_hits'] / total) * 100
    
    def _calculate_error_rate(self):
        """Calculate overall error rate percentage"""
        total_requests = sum(performance_metrics['requests'].values())
        total_errors = sum(performance_metrics['errors'].values())
        if total_requests == 0:
            return 0.0
        return (total_errors / total_requests) * 100
    
    def _get_top_endpoints(self, limit=10):
        """Get top endpoints by request count"""
        sorted_endpoints = sorted(
            performance_metrics['requests'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {'endpoint': endpoint, 'count': count}
            for endpoint, count in sorted_endpoints[:limit]
        ]
    
    def _get_slow_queries(self):
        """Get slow database queries"""
        slow_queries = []
        for query, times in performance_metrics['database_queries'].items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > 100:  # Queries slower than 100ms
                    slow_queries.append({
                        'query': query[:100],  # Truncate for display
                        'avg_time': avg_time,
                        'count': len(times)
                    })
        return sorted(slow_queries, key=lambda x: x['avg_time'], reverse=True)[:10]


def track_template_download(template_id):
    """Track template download"""
    performance_metrics['template_downloads'][template_id] += 1
    logger.info(f"Template download tracked: {template_id}")


def track_ai_generation(user_id=None):
    """Track AI template generation"""
    key = user_id or 'anonymous'
    performance_metrics['ai_generations'][key] += 1
    logger.info(f"AI generation tracked for user: {key}")


def track_user_activity(user_id):
    """Track user activity"""
    performance_metrics['user_activity'][user_id] += 1


def track_database_query(query, execution_time):
    """Track database query performance"""
    query_key = query[:50]  # Use first 50 chars as key
    performance_metrics['database_queries'][query_key].append(execution_time)


def track_cache_hit():
    """Track cache hit"""
    performance_metrics['cache_hits'] += 1


def track_cache_miss():
    """Track cache miss"""
    performance_metrics['cache_misses'] += 1


def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            # Log if function is slow
            if execution_time > 500:
                logger.warning(f"Slow function: {func.__name__} took {execution_time:.2f}ms")
            
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


def log_error(error, context=None):
    """Log error with context for error tracking"""
    error_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'error': str(error),
        'type': type(error).__name__,
        'context': context or {},
        'endpoint': request.endpoint if request else 'N/A',
        'method': request.method if request else 'N/A',
        'url': request.url if request else 'N/A'
    }
    
    logger.error(f"Error logged: {json.dumps(error_data)}")
    
    # In production, send to error tracking service (e.g., Sentry)
    # sentry_sdk.capture_exception(error)


# Initialize monitoring
monitor = PerformanceMonitor()

