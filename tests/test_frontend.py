import pytest
from unittest.mock import patch, MagicMock
import requests

# Since streamlit is usually run as a script, we test the logic functions
# We inject streamlit as a mock to avoid importing the full streamlit lib in CI
with patch.dict("sys.modules", {"streamlit": MagicMock()}):
    from frontend import resolve_filename, wait_for_backend

def test_resolve_filename():
    # Exact match
    assert resolve_filename("test.wav") == ["test.wav"]
    # Priority match
    assert resolve_filename("test") == ["test.wav", "test.mp3", "test.mp4"]
    # Empty
    assert resolve_filename("") == []
    assert resolve_filename("   ") == []

def test_wait_for_backend_ready():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"messages": [], "ready": True}

        # We need to mock st.empty() etc via a mock streamlit
        with patch("frontend.st") as mock_st:
            assert wait_for_backend() is True

def test_wait_for_backend_not_ready():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"messages": ["loading..."], "ready": False}

        # To prevent infinite loop in test, we patch the loop to break after 1 iteration
        # or mock time.sleep to fail
        with patch("frontend.st") as mock_st, patch("time.sleep", side_effect=InterruptedError):
            with pytest.raises(InterruptedError):
                wait_for_backend()
