#!/bin/bash
# Start telegram bot in background
python run_bot.py &
# Start Django
gunicorn diary.wsgi