"""Tests for ADK agent definitions and tool signatures."""

from unittest.mock import MagicMock, patch


class TestRootAgent:
    """Tests for the root ADK Agent structure."""

    def test_root_agent_imports(self):
        """Root agent module can be imported."""
        import agents.agent  # noqa: F401

    def test_root_agent_has_sub_agents(self):
        """Root agent has sub_agents attribute."""
        from agents.agent import root_agent
        assert root_agent is not None
        assert hasattr(root_agent, 'name')
        assert root_agent.name == "aita_lagun"

    def test_root_agent_has_before_callback(self):
        """Root agent has before_agent_callback."""
        from agents.agent import root_agent
        assert hasattr(root_agent, 'before_agent_callback')
        assert root_agent.before_agent_callback is not None

    def test_root_agent_has_sub_agent_list(self):
        """Root agent has at least 2 sub_agents."""
        from agents.agent import root_agent
        assert hasattr(root_agent, 'sub_agents')
        assert len(root_agent.sub_agents) >= 2

    def test_root_agent_entry_point_exists(self):
        """Module has a main entry point function."""
        import agents.agent
        assert hasattr(agents.agent, 'main') or hasattr(agents.agent, 'run_agent')



class TestInfoSaludAgent:
    """Tests for info_salud_agent.py."""

    def test_info_salud_imports(self):
        """Info salud agent module can be imported."""
        import agents.info_salud_agent  # noqa: F401

    def test_agent_is_adk_agent(self):
        """info_salud_agent exports an ADK Agent instance."""
        from agents.info_salud_agent import info_salud_agent
        from google.adk.agents import Agent
        assert isinstance(info_salud_agent, Agent)
        assert info_salud_agent.name == "info_salud"


class TestOrchestratorAgent:
    """Tests for orchestrator.py."""

    def test_orchestrator_imports(self):
        """Orchestrator module can be imported."""
        import agents.orchestrator  # noqa: F401

    def test_orchestrator_is_adk_agent(self):
        """orchestrator exports an ADK Agent instance."""
        from agents.orchestrator import recordatorio
        from google.adk.agents import Agent
        assert isinstance(recordatorio, Agent)
        assert recordatorio.name == "recordatorio"


class TestDetectLanguage:
    """Tests for the _detect_language async callback in agents/agent.py."""

    def _make_context(self, messages: list[str]):
        """Helper: build a mock CallbackContext with sequential user messages."""
        context = MagicMock()
        context.state = {}
        events = []
        for msg in messages:
            event = MagicMock()
            part = MagicMock()
            part.text = msg
            event.content.parts = [part]
            events.append(event)
        context.session.events = events
        return context

    async def test_detect_basque(self):
        """'gogoratu pastilla 8etan' detects Basque."""
        from agents.agent import _detect_language

        ctx = self._make_context(["gogoratu pastilla 8etan"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "eu"

    async def test_detect_spanish(self):
        """'recuerda tomarme la pastilla' detects Spanish."""
        from agents.agent import _detect_language

        ctx = self._make_context(["recuerda tomarme la pastilla"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "es"

    async def test_detect_english(self):
        """'remind me to take medicine' detects English."""
        from agents.agent import _detect_language

        ctx = self._make_context(["remind me to take medicine"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "en"

    async def test_fallback_to_english(self):
        """Text without language keywords falls back to English."""
        from agents.agent import _detect_language

        ctx = self._make_context(["some random text with no keywords"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "en"

    async def test_strong_signal_overwrites_existing_lang(self):
        """A strong keyword signal overrides a previously-set language."""
        from agents.agent import _detect_language

        ctx = self._make_context(["gogoratu pastilla 8etan"])
        ctx.state["lang"] = "de"  # pre-set from somewhere else
        await _detect_language(ctx)
        # "gogoratu" is a strong Basque signal → overwrites
        assert ctx.state["lang"] == "eu"

    async def test_weak_signal_keeps_existing_lang(self):
        """Text without strong keywords keeps the existing language unchanged."""
        from agents.agent import _detect_language

        ctx = self._make_context(["some random text with no keywords"])
        ctx.state["lang"] = "eu"  # pre-set
        await _detect_language(ctx)
        assert ctx.state["lang"] == "eu"  # unchanged

    async def test_hola_detects_spanish(self):
        """'hola' is a Spanish keyword, not English."""
        from agents.agent import _detect_language

        ctx = self._make_context(["hola"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "es"

    async def test_hello_detects_english(self):
        """'hello' is an English keyword, not Spanish."""
        from agents.agent import _detect_language

        ctx = self._make_context(["hello"])
        await _detect_language(ctx)
        assert ctx.state["lang"] == "en"


class TestMainEntryPoint:
    """Tests for the main() CLI entry point."""

    @patch("builtins.input")
    @patch("agents.agent.Runner")
    async def test_main_exits_immediately(self, mock_runner_cls, mock_input):
        """main() exits cleanly when user types 'exit'."""
        mock_input.return_value = "exit"

        from agents.agent import main

        await main()

        mock_input.assert_called_once()

    @patch("builtins.input")
    @patch("agents.agent.Runner")
    async def test_main_processes_one_message_then_exits(
        self, mock_runner_cls, mock_input
    ):
        """main() processes a user message and exits on 'exit'."""
        mock_input.side_effect = ["remind me at 8", "exit"]

        mock_runner = MagicMock()
        mock_runner_cls.return_value = mock_runner

        async def mock_run_async(**kwargs):
            event = MagicMock()
            event.is_final_response.return_value = True
            part = MagicMock()
            part.text = "Claro, te recuerdo."
            event.content.parts = [part]
            yield event

        mock_runner.run_async = mock_run_async

        from agents.agent import main

        await main()

        assert mock_runner_cls.called
        assert mock_input.call_count >= 2
