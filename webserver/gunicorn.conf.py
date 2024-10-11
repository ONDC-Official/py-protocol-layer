import os
from logging import Filter


# Health check log filter
class IgnoreHealthCheckFilter(Filter):
    def filter(self, record):
        if "GET / " in record.getMessage():
            return False
        return True


# Gunicorn configuration
workers = 2  # Number of worker processes
threads = 4  # Number of threads per worker
timeout = 600  # Worker timeout in seconds

# Fetch PORT from environment variable, default to 8000 if not set
port = os.getenv('PORT', '8000')
bind = f"0.0.0.0:{port}"


# Logging configuration
logconfig_dict = {
    'version': 1,
    'filters': {
        'ignore_health_check': {
            '()': IgnoreHealthCheckFilter,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'access',
            'filters': ['ignore_health_check'],
        },
    },
    'loggers': {
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'formatters': {
        'access': {
            'format': '%(process)d %(thread)d %(asctime)s [%(name)s][%(levelname)s]::%(message)s',
        },
    },
}