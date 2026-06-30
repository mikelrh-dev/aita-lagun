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


class TestBuildRrule:
    """Pure function tests for _build_rrule — no mocking needed."""

    def test_none_returns_none(self):
        """None input returns None (no recurrence)."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule(None) is None

    def test_empty_string_returns_none(self):
        """Empty string returns None (backward compatible)."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("") is None

    def test_daily(self):
        """'daily' maps to FREQ=DAILY."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("daily") == ["RRULE:FREQ=DAILY"]

    def test_weekdays_shorthand(self):
        """'weekdays' maps to all weekdays."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("weekdays") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
        ]

    def test_weekly_single_day(self):
        """'weekly;MO' maps to FREQ=WEEKLY;BYDAY=MO."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("weekly;MO") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO"
        ]

    def test_weekly_multiple_days(self):
        """'weekly;MO,WE,FR' maps correctly."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("weekly;MO,WE,FR") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"
        ]

    def test_weekly_all_days(self):
        """'weekly;MO,TU,WE,TH,FR,SA,SU' maps correctly."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("weekly;MO,TU,WE,TH,FR,SA,SU") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU"
        ]

    def test_unsupported_raises_valueerror(self):
        """'monthly' raises ValueError."""
        from mcp_servers.calendar_mcp import _build_rrule

        with pytest.raises(ValueError, match="Unsupported recurrence"):
            _build_rrule("monthly")

    def test_weekly_no_days_raises(self):
        """'weekly' without days raises ValueError."""
        from mcp_servers.calendar_mcp import _build_rrule

        with pytest.raises(ValueError, match="Invalid weekly"):
            _build_rrule("weekly")

    def test_weekly_empty_days_raises(self):
        """'weekly;' with empty day list raises ValueError."""
        from mcp_servers.calendar_mcp import _build_rrule

        with pytest.raises(ValueError, match="Invalid weekly"):
            _build_rrule("weekly;")

    def test_invalid_day_code_raises(self):
        """'weekly;XX' raises ValueError with invalid day message."""
        from mcp_servers.calendar_mcp import _build_rrule

        with pytest.raises(ValueError, match="Invalid day code"):
            _build_rrule("weekly;XX")

    def test_case_normalization(self):
        """'WEEKLY;MO' (uppercase prefix) normalizes correctly."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("WEEKLY;MO") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO"
        ]

    def test_mixed_case_days(self):
        """'weekly;mo,we,fr' normalizes days to uppercase."""
        from mcp_servers.calendar_mcp import _build_rrule

        assert _build_rrule("weekly;mo,we,fr") == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"
        ]


class TestRecurrenceIntegration:
    """Integration tests for recurrence in crear_evento_calendar (mocked API)."""

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_daily_recurrence(self, mock_get_service):
        """Daily recurrence adds RRULE:FREQ=DAILY to event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event999"}

        result = crear_evento_calendar(
            medication="Sintrom", time="08:00", recurrence="daily"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert body["recurrence"] == ["RRULE:FREQ=DAILY"]
        assert body["summary"] == "Recordatorio: Sintrom"
        assert result["status"] == "created"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_weekly_single_day(self, mock_get_service):
        """weekly;MO maps to FREQ=WEEKLY;BYDAY=MO in event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1000"}

        result = crear_evento_calendar(
            medication="Sintrom", time="08:00", recurrence="weekly;MO"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert body["recurrence"] == ["RRULE:FREQ=WEEKLY;BYDAY=MO"]
        assert result["status"] == "created"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_weekly_multiple_days(self, mock_get_service):
        """weekly;MO,WE,FR maps to correct RRULE in event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1001"}

        result = crear_evento_calendar(
            medication="Sintrom", time="08:00", recurrence="weekly;MO,WE,FR"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert body["recurrence"] == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"
        ]
        assert result["status"] == "created"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_no_recurrence_default(self, mock_get_service):
        """No recurrence parameter = no recurrence field in event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1002"}

        crear_evento_calendar(medication="Sintrom", time="08:00")

        body = mock_events.insert.call_args[1]["body"]
        assert "recurrence" not in body

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_no_recurrence_empty_string(self, mock_get_service):
        """Empty string recurrence = no recurrence field in event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1003"}

        crear_evento_calendar(medication="Sintrom", time="08:00", recurrence="")

        body = mock_events.insert.call_args[1]["body"]
        assert "recurrence" not in body

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_unsupported_recurrence_returns_error(self, mock_get_service):
        """Unsupported pattern returns error dict and does NOT call API."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events

        result = crear_evento_calendar(
            medication="Test", time="08:00", recurrence="monthly"
        )

        assert result["status"] == "error"
        assert "Unsupported recurrence" in result["error"]
        mock_events.insert.assert_not_called()

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_weekly_without_days_returns_error(self, mock_get_service):
        """'weekly' (no days) returns error dict and does NOT call API."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events

        result = crear_evento_calendar(
            medication="Test", time="08:00", recurrence="weekly"
        )

        assert result["status"] == "error"
        assert "Invalid weekly" in result["error"]
        mock_events.insert.assert_not_called()

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_weekdays_shorthand(self, mock_get_service):
        """'weekdays' maps to all weekdays in event body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1004"}

        result = crear_evento_calendar(
            medication="Sintrom", time="08:00", recurrence="weekdays"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert body["recurrence"] == [
            "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
        ]
        assert result["status"] == "created"

    @patch("mcp_servers.calendar_mcp._get_calendar_service")
    def test_recurrence_with_date(self, mock_get_service):
        """Recurrence with explicit date sets both RRULE and date in body."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_insert = MagicMock()
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {"id": "event1005"}

        result = crear_evento_calendar(
            medication="Sintrom", time="08:00", date="2026-12-25",
            recurrence="daily"
        )

        body = mock_events.insert.call_args[1]["body"]
        assert body["recurrence"] == ["RRULE:FREQ=DAILY"]
        assert "2026-12-25" in body["start"]["dateTime"]
        assert result["status"] == "created"
