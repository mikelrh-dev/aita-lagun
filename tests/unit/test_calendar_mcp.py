"""Tests for calendar_mcp.py FastMCP server."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_servers.calendar_mcp import _parse_time, crear_evento_calendar


class TestCalendarMCP:
    """Unit tests for the calendar MCP crear_evento_calendar tool."""

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_crear_evento_basic(self, mock_get_service):
        """Creates a calendar event with medication and time."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event123", "htmlLink": "https://calendar.google.com/"}

        result = crear_evento_calendar(medication="Sintrom", time="08:00")

        mock_service.events.assert_called_once()
        mock_events.insert.assert_called_once()
        call_kwargs = mock_events.insert.call_args[1]
        assert "body" in call_kwargs
        body = call_kwargs["body"]
        assert body["summary"] == "Recordatorio: Sintrom"
        assert "08:00" in body["start"]["dateTime"]

        assert result["status"] == "created"
        assert result["event_id"] == "event123"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_crear_evento_with_date(self, mock_get_service):
        """Creates a calendar event with a specific date."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event456"}

        result = crear_evento_calendar(
            medication="Paracetamol", time="14:30", date="2025-12-25"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert "2025-12-25" in body["start"]["dateTime"]
        assert result["status"] == "created"
        assert result["event_id"] == "event456"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_crear_evento_default_date_is_today(self, mock_get_service):
        """When no date is provided, uses today's date."""
        from datetime import date as date_mod

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event789"}

        crear_evento_calendar(medication="Ibuprofeno", time="20:00")

        body = mock_events.insert.call_args[1]["body"]
        today_str = date_mod.today().isoformat()
        assert today_str in body["start"]["dateTime"]


class TestParseTime:
    """Tests for the _parse_time helper function."""

    def test_hh_mm_format(self):
        """'08:00' stays as '08:00'."""
        assert _parse_time("08:00") == "08:00"

    def test_bare_hour(self):
        """'8' becomes '08:00'."""
        assert _parse_time("8") == "08:00"

    def test_bare_hour_two_digits(self):
        """'14' becomes '14:00'."""
        assert _parse_time("14") == "14:00"

    def test_am_without_space(self):
        """'8am' becomes '08:00'."""
        assert _parse_time("8am") == "08:00"

    def test_pm_with_space(self):
        """'8 pm' becomes '20:00'."""
        assert _parse_time("8 pm") == "20:00"

    def test_am_with_minutes(self):
        """'8:30am' becomes '08:30'."""
        assert _parse_time("8:30am") == "08:30"

    def test_pm_noon(self):
        """'12:00 PM' stays as '12:00'."""
        assert _parse_time("12:00 PM") == "12:00"

    def test_am_midnight(self):
        """'12:00 am' becomes '00:00'."""
        assert _parse_time("12:00 am") == "00:00"

    def test_invalid_raises_valueerror(self):
        """'invalid' raises ValueError with descriptive message."""
        with pytest.raises(ValueError, match="Could not parse time"):
            _parse_time("invalid")

    def test_invalid_time_in_crear_evento_returns_error(self):
        """crear_evento_calendar returns error dict when time is invalid."""
        result = crear_evento_calendar(medication="Test", time="invalid")
        assert result["status"] == "error"
        assert "Could not parse time" in result["error"]
