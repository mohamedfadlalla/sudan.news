# Logging
loglevel = "info"
# USE ABSOLUTE PATHS:
accesslog = "/var/www/sudanese_news/shared/logs/access.log"
errorlog = "/var/www/sudanese_news/shared/logs/error.log" 
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "sudan-news-api"

# Server mechanics
# USE ABSOLUTE PATH:
pidfile = "/var/www/sudanese_news/shared/logs/gunicorn.pid"
