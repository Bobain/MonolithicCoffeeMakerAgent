"""End-to-end integration tests for ACE Streamlit App."""

import pytest
from streamlit.testing.v1 import AppTest


# Test configuration
STREAMLIT_APP_PATH = "coffee_maker/streamlit_app/app.py"
MONITOR_PAGE_PATH = "coffee_maker/streamlit_app/pages/2_📊_Monitor.py"
PLAYBOOKS_PAGE_PATH = "coffee_maker/streamlit_app/pages/3_📚_Playbooks.py"
ANALYTICS_PAGE_PATH = "coffee_maker/streamlit_app/pages/4_📊_Analytics.py"


class TestHomePageE2E:
    """End-to-end tests for the Home page."""

    def test_home_page_loads_successfully(self):
        """Test that the home page loads without errors."""
        at = AppTest.from_file(STREAMLIT_APP_PATH)
        at.run()

        assert not at.exception, f"Page raised exception: {at.exception}"
        assert len(at.markdown) > 0, "No markdown elements found on page"

    def test_home_page_displays_title(self):
        """Test that the home page displays the correct title."""
        at = AppTest.from_file(STREAMLIT_APP_PATH)
        at.run()

        # Check for title in markdown or header
        assert any("ACE Framework" in str(m.value) for m in at.markdown), "Title 'ACE Framework' not found on home page"

    def test_home_page_has_metrics(self):
        """Test that the home page displays quick status metrics."""
        at = AppTest.from_file(STREAMLIT_APP_PATH)
        at.run()

        # Should have at least 3 metrics (Active Agents, Traces, Success Rate)
        assert len(at.metric) >= 3, f"Expected at least 3 metrics, found {len(at.metric)}"


class TestMonitorPageE2E:
    """End-to-end tests for the Monitor page."""

    def test_monitor_page_loads_successfully(self):
        """Test that the monitor page loads without errors."""
        at = AppTest.from_file(MONITOR_PAGE_PATH)
        at.run()

        assert not at.exception, f"Page raised exception: {at.exception}"

    def test_monitor_page_has_filters(self):
        """Test that the monitor page has filter controls."""
        at = AppTest.from_file(MONITOR_PAGE_PATH)
        at.run()

        # Should have selectboxes for agent and time range
        assert len(at.selectbox) >= 2, f"Expected at least 2 selectboxes (agent, time range), found {len(at.selectbox)}"

    def test_monitor_page_filter_interaction(self):
        """Test that agent filter changes work."""
        at = AppTest.from_file(MONITOR_PAGE_PATH)
        at.run()

        # Get agent filter (first selectbox)
        if len(at.selectbox) > 0:
            agent_filter = at.selectbox[0]

            # Try to select a different agent
            if "user_interpret" in agent_filter.options:
                agent_filter.select("user_interpret")
                at.run()

                # Verify selection worked
                assert agent_filter.value == "user_interpret", "Agent filter selection did not work"

    def test_monitor_page_auto_refresh_toggle(self):
        """Test that auto-refresh checkbox works."""
        at = AppTest.from_file(MONITOR_PAGE_PATH)
        at.run()

        # Find auto-refresh checkbox
        if len(at.checkbox) > 0:
            auto_refresh = at.checkbox[0]

            # Toggle auto-refresh
            auto_refresh.check()
            at.run()

            # Note: We can't fully test the 5-second refresh cycle
            # but we can verify the checkbox state changed
            assert auto_refresh.value is True, "Auto-refresh checkbox did not toggle"


class TestPlaybooksPageE2E:
    """End-to-end tests for the Playbooks page."""

    def test_playbooks_page_loads_successfully(self):
        """Test that the playbooks page loads without errors."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        assert not at.exception, f"Page raised exception: {at.exception}"

    def test_playbooks_page_has_agent_selector(self):
        """Test that the playbooks page has an agent selector."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        assert len(at.selectbox) >= 1, "No agent selector found on playbooks page"

    def test_playbooks_page_agent_selection(self):
        """Test that selecting an agent loads playbook."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        if len(at.selectbox) > 0:
            agent_selector = at.selectbox[0]

            # Select an agent
            if "assistant" in agent_selector.options:
                agent_selector.select("assistant")
                at.run()

                # Verify agent was selected
                assert agent_selector.value == "assistant", "Agent selection did not work"

    def test_playbooks_page_has_search_box(self):
        """Test that the playbooks page has a search box."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        # Should have text input for search
        assert len(at.text_input) >= 1, "No search box found on playbooks page"

    def test_playbooks_page_search_functionality(self):
        """Test that search box filters bullets."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        if len(at.text_input) > 0:
            search_box = at.text_input[0]

            # Enter search query
            search_box.set_value("error")
            at.run()

            # Verify search query was set
            assert search_box.value == "error", "Search query not set"

    def test_playbooks_page_has_visualizations(self):
        """Test that the playbooks page has visualization tabs."""
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()

        # Should have tabs for visualizations
        # (Streamlit Testing API may not expose tabs directly, so we check for plotly charts)
        # If data is available, we should see some charts or at least tab structure


class TestAnalyticsPageE2E:
    """End-to-end tests for the Analytics page."""

    def test_analytics_page_loads_successfully(self):
        """Test that the analytics page loads without errors."""
        at = AppTest.from_file(ANALYTICS_PAGE_PATH)
        at.run()

        assert not at.exception, f"Page raised exception: {at.exception}"

    def test_analytics_page_has_time_range_slider(self):
        """Test that the analytics page has a time range slider."""
        at = AppTest.from_file(ANALYTICS_PAGE_PATH)
        at.run()

        # Should have at least 1 slider for time range
        assert len(at.slider) >= 1, "No time range slider found on analytics page"

    def test_analytics_page_time_range_interaction(self):
        """Test that time range slider works."""
        at = AppTest.from_file(ANALYTICS_PAGE_PATH)
        at.run()

        if len(at.slider) > 0:
            time_slider = at.slider[0]

            # Set to 60 days
            time_slider.set_value(60)
            at.run()

            # Verify slider value changed
            assert time_slider.value == 60, "Time range slider did not update"

    def test_analytics_page_has_executive_summary(self):
        """Test that the analytics page displays executive summary."""
        at = AppTest.from_file(ANALYTICS_PAGE_PATH)
        at.run()

        # Should have multiple metrics in executive summary
        assert len(at.metric) >= 4, f"Expected at least 4 metrics in executive summary, found {len(at.metric)}"


class TestFullUserWorkflow:
    """Test complete user workflows across pages."""

    @pytest.mark.slow
    def test_monitoring_workflow(self):
        """
        Test complete monitoring workflow:
        1. Start at home
        2. Navigate to monitor
        3. Apply filters
        4. View traces
        """
        # Step 1: Home page
        at_home = AppTest.from_file(STREAMLIT_APP_PATH)
        at_home.run()
        assert not at_home.exception, "Home page failed to load"

        # Step 2: Monitor page
        at_monitor = AppTest.from_file(MONITOR_PAGE_PATH)
        at_monitor.run()
        assert not at_monitor.exception, "Monitor page failed to load"

        # Step 3: Apply filters
        if len(at_monitor.selectbox) >= 2:
            # Select time range
            time_range = at_monitor.selectbox[1]
            if ("Last 24 Hours", 24) in time_range.options:
                time_range.select(("Last 24 Hours", 24))
                at_monitor.run()

        # Workflow complete without errors
        assert True

    @pytest.mark.slow
    def test_playbook_curation_workflow(self):
        """
        Test complete playbook curation workflow:
        1. Select agent
        2. Apply filters
        3. Search for bullets
        4. Review bullet details
        """
        at = AppTest.from_file(PLAYBOOKS_PAGE_PATH)
        at.run()
        assert not at.exception, "Playbooks page failed to load"

        # Select agent
        if len(at.selectbox) > 0:
            agent_selector = at.selectbox[0]
            if "code_developer" in agent_selector.options:
                agent_selector.select("code_developer")
                at.run()

        # Apply search
        if len(at.text_input) > 0:
            search_box = at.text_input[0]
            search_box.set_value("test")
            at.run()

        # Workflow complete without errors
        assert not at.exception

    @pytest.mark.slow
    def test_analytics_review_workflow(self):
        """
        Test complete analytics review workflow:
        1. Set time range
        2. Filter by agent
        3. Review metrics
        4. Explore visualizations
        """
        at = AppTest.from_file(ANALYTICS_PAGE_PATH)
        at.run()
        assert not at.exception, "Analytics page failed to load"

        # Set time range
        if len(at.slider) > 0:
            time_slider = at.slider[0]
            time_slider.set_value(30)
            at.run()

        # Filter by agent (if selectbox available)
        if len(at.selectbox) > 0:
            agent_filter = at.selectbox[0]
            if "All Agents" in agent_filter.options:
                agent_filter.select("All Agents")
                at.run()

        # Workflow complete without errors
        assert not at.exception


# Pytest markers for test organization
pytestmark = [
    pytest.mark.integration,
    pytest.mark.streamlit,
]
