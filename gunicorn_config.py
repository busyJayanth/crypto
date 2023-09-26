# gunicorn_config.py

bind = "0.0.0.0:8000"  # Change this to the desired host and port
workers = 4  # You can adjust the number of workers based on your server's capacity
timeout = 120
gunicorn
