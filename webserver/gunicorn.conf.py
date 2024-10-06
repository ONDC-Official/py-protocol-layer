import logging

workers = 8
bind = "0.0.0.0:5555"
timeout = 300

# Logging setup
loglevel = 'info'
accesslog = '-'  # Log access logs to stdout
errorlog = '-'   # Log error logs to stdout

# Example of configuring logging with a specific handler
logging.basicConfig(level=logging.INFO,
                    format='%(process)d %(thread)d %(asctime)s [%(name)s][%(levelname)s]::%(message)s')
