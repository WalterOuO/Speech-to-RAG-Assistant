import pytest
from app.db.status_db import init_db, update_status, get_status
import os

def test_status_db_lifecycle():
    # init_db creates the table
    init_db()

    # Test update (Insert)
    update_status("test1.wav", "task_123", "processing")
    res = get_status("test1.wav")
    assert res is not None
    assert res["status"] == "processing"
    assert res["task_id"] == "task_123"

    # Test update (Upsert)
    update_status("test1.wav", "task_123", "completed")
    res = get_status("test1.wav")
    assert res["status"] == "completed"

    # Test missing
    assert get_status("nonexistent.wav") is None
