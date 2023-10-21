import os

bind = '0.0.0.0:' + str(os.getenv('PORT', 8000))
proc_name = 'Flask'
workers = 4
