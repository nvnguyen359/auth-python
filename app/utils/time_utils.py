# Hàm xử lý ngày 
# app/utils/time_utils.py
from datetime import datetime, timedelta
from typing import Tuple

def today() -> Tuple[datetime, datetime]:
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    return start, end

def yesterday() -> Tuple[datetime, datetime]:
    now = datetime.now()
    end = datetime(now.year, now.month, now.day)
    start = end - timedelta(days=1)
    return start, end

def last7days() -> Tuple[datetime, datetime]:
    now = datetime.now()
    start = now - timedelta(days=7)
    return start, now

def last15days() -> Tuple[datetime, datetime]:
    now = datetime.now()
    start = now - timedelta(days=15)
    return start, now
