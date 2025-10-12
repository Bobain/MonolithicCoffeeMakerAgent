"""Unit tests for cost budget enforcement."""

import time

import pytest

from coffee_maker.langfuse_observe.cost_budget import (
    BudgetConfig,
    BudgetExceededError,
    BudgetPeriod,
    CostBudgetEnforcer,
    create_budget_enforcer,
)


class TestBudgetConfig:
    """Tests for BudgetConfig."""

    def test_create_budget_config(self):
        """Test creating a budget configuration."""
        config = BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)

        assert config.amount == 10.0
        assert config.period == BudgetPeriod.DAILY
        assert config.hard_limit is True
        assert config.warning_threshold == 0.8

    def test_custom_warning_threshold(self):
        """Test custom warning threshold."""
        config = BudgetConfig(
            amount=10.0,
            period=BudgetPeriod.DAILY,
            warning_threshold=0.5,
        )

        assert config.warning_threshold == 0.5

    def test_soft_limit(self):
        """Test soft limit configuration."""
        config = BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY, hard_limit=False)

        assert config.hard_limit is False


class TestCostBudgetEnforcer:
    """Tests for CostBudgetEnforcer."""

    def test_create_enforcer(self):
        """Test creating a budget enforcer."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        assert BudgetPeriod.DAILY in enforcer.budgets

    def test_record_cost(self):
        """Test recording a cost."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(5.0)

        spent = enforcer.get_spent(BudgetPeriod.DAILY)
        assert spent == 5.0

    def test_record_cost_with_model(self):
        """Test recording cost for specific model."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(3.0, model="gpt-4")
        enforcer.record_cost(2.0, model="gpt-3.5")

        total = enforcer.get_spent(BudgetPeriod.DAILY)
        gpt4 = enforcer.get_spent(BudgetPeriod.DAILY, model="gpt-4")
        gpt35 = enforcer.get_spent(BudgetPeriod.DAILY, model="gpt-3.5")

        assert total == 5.0
        assert gpt4 == 3.0
        assert gpt35 == 2.0

    def test_budget_exceeded_raises_error(self):
        """Test that exceeding budget raises error."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY, hard_limit=True)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(8.0)

        with pytest.raises(BudgetExceededError) as exc_info:
            enforcer.record_cost(5.0)

        assert exc_info.value.budget == 10.0
        assert exc_info.value.current > 10.0
        assert exc_info.value.period == BudgetPeriod.DAILY

    def test_soft_limit_no_error(self):
        """Test that soft limit doesn't raise error."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY, hard_limit=False)}
        enforcer = CostBudgetEnforcer(budgets)

        # Should not raise even when over budget
        enforcer.record_cost(8.0)
        enforcer.record_cost(5.0)

        spent = enforcer.get_spent(BudgetPeriod.DAILY)
        assert spent == 13.0

    def test_get_remaining(self):
        """Test getting remaining budget."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(3.0)

        remaining = enforcer.get_remaining(BudgetPeriod.DAILY)
        assert remaining == 7.0

    def test_get_remaining_zero_when_exceeded(self):
        """Test that remaining is 0 when exceeded."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY, hard_limit=False)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(12.0)

        remaining = enforcer.get_remaining(BudgetPeriod.DAILY)
        assert remaining == 0.0

    def test_get_budget_status(self):
        """Test getting budget status."""
        budgets = {
            BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY),
            BudgetPeriod.MONTHLY: BudgetConfig(amount=100.0, period=BudgetPeriod.MONTHLY),
        }
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(4.0)

        status = enforcer.get_budget_status()

        assert "daily" in status
        assert "monthly" in status
        assert status["daily"]["budget"] == 10.0
        assert status["daily"]["spent"] == 4.0
        assert status["daily"]["remaining"] == 6.0
        assert status["daily"]["percentage"] == 40.0

    def test_can_afford(self):
        """Test checking if cost is affordable."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(7.0)

        assert enforcer.can_afford(2.0) is True
        assert enforcer.can_afford(5.0) is False

    def test_can_afford_with_soft_limit(self):
        """Test that soft limits allow overspending."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY, hard_limit=False)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(7.0)

        # Soft limit allows overspending
        assert enforcer.can_afford(10.0) is True

    def test_reset_budget(self):
        """Test resetting a budget."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(5.0)
        assert enforcer.get_spent(BudgetPeriod.DAILY) == 5.0

        enforcer.reset_budget(BudgetPeriod.DAILY)
        assert enforcer.get_spent(BudgetPeriod.DAILY) == 0.0

    def test_reset_all_budgets(self):
        """Test resetting all budgets."""
        budgets = {
            BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY),
            BudgetPeriod.MONTHLY: BudgetConfig(amount=100.0, period=BudgetPeriod.MONTHLY),
        }
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(5.0)

        enforcer.reset_budget()  # Reset all

        assert enforcer.get_spent(BudgetPeriod.DAILY) == 0.0
        assert enforcer.get_spent(BudgetPeriod.MONTHLY) == 0.0

    def test_multiple_budgets_tracked_separately(self):
        """Test that different budget periods track independently."""
        budgets = {
            BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY),
            BudgetPeriod.MONTHLY: BudgetConfig(amount=100.0, period=BudgetPeriod.MONTHLY),
        }
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(5.0)

        assert enforcer.get_spent(BudgetPeriod.DAILY) == 5.0
        assert enforcer.get_spent(BudgetPeriod.MONTHLY) == 5.0

    def test_budget_not_configured_returns_infinity(self):
        """Test that unconfigured budget returns infinite remaining."""
        enforcer = CostBudgetEnforcer({})

        remaining = enforcer.get_remaining(BudgetPeriod.DAILY)
        assert remaining == float("inf")


class TestBudgetAutoReset:
    """Tests for automatic budget reset based on time."""

    def test_hourly_budget_resets_after_hour(self):
        """Test that hourly budget resets after an hour."""
        budgets = {BudgetPeriod.HOURLY: BudgetConfig(amount=1.0, period=BudgetPeriod.HOURLY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(0.5)
        assert enforcer.get_spent(BudgetPeriod.HOURLY) == 0.5

        # Simulate time passing (1 hour + 1 second)
        enforcer._reset_times[BudgetPeriod.HOURLY] = time.time() - 3601

        # Next cost should trigger reset
        enforcer.record_cost(0.3)
        spent = enforcer.get_spent(BudgetPeriod.HOURLY)

        # Should only show the new cost, not cumulative
        assert spent == 0.3

    def test_daily_budget_resets_after_day(self):
        """Test that daily budget resets after a day."""
        budgets = {BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(5.0)

        # Simulate time passing (1 day + 1 second)
        enforcer._reset_times[BudgetPeriod.DAILY] = time.time() - 86401

        enforcer.record_cost(3.0)
        spent = enforcer.get_spent(BudgetPeriod.DAILY)

        assert spent == 3.0

    def test_total_budget_never_resets(self):
        """Test that total budget doesn't reset automatically."""
        budgets = {BudgetPeriod.TOTAL: BudgetConfig(amount=1000.0, period=BudgetPeriod.TOTAL)}
        enforcer = CostBudgetEnforcer(budgets)

        enforcer.record_cost(100.0)

        # Simulate time passing (way in the future)
        enforcer._reset_times[BudgetPeriod.TOTAL] = time.time() - 999999

        enforcer.record_cost(50.0)
        spent = enforcer.get_spent(BudgetPeriod.TOTAL)

        # Should be cumulative
        assert spent == 150.0


class TestCreateBudgetEnforcer:
    """Tests for create_budget_enforcer factory function."""

    def test_create_with_daily_budget(self):
        """Test creating enforcer with daily budget."""
        enforcer = create_budget_enforcer(daily_budget=10.0)

        assert BudgetPeriod.DAILY in enforcer.budgets
        assert enforcer.budgets[BudgetPeriod.DAILY].amount == 10.0

    def test_create_with_monthly_budget(self):
        """Test creating enforcer with monthly budget."""
        enforcer = create_budget_enforcer(monthly_budget=200.0)

        assert BudgetPeriod.MONTHLY in enforcer.budgets
        assert enforcer.budgets[BudgetPeriod.MONTHLY].amount == 200.0

    def test_create_with_total_budget(self):
        """Test creating enforcer with total budget."""
        enforcer = create_budget_enforcer(total_budget=1000.0)

        assert BudgetPeriod.TOTAL in enforcer.budgets
        assert enforcer.budgets[BudgetPeriod.TOTAL].amount == 1000.0

    def test_create_with_multiple_budgets(self):
        """Test creating enforcer with multiple budgets."""
        enforcer = create_budget_enforcer(
            daily_budget=5.0,
            monthly_budget=100.0,
            total_budget=500.0,
        )

        assert len(enforcer.budgets) == 3
        assert enforcer.budgets[BudgetPeriod.DAILY].amount == 5.0
        assert enforcer.budgets[BudgetPeriod.MONTHLY].amount == 100.0
        assert enforcer.budgets[BudgetPeriod.TOTAL].amount == 500.0

    def test_create_with_custom_warning_threshold(self):
        """Test creating with custom warning threshold."""
        enforcer = create_budget_enforcer(daily_budget=10.0, warning_threshold=0.5)

        assert enforcer.budgets[BudgetPeriod.DAILY].warning_threshold == 0.5

    def test_create_with_soft_limit(self):
        """Test creating with soft limit."""
        enforcer = create_budget_enforcer(daily_budget=10.0, hard_limit=False)

        assert enforcer.budgets[BudgetPeriod.DAILY].hard_limit is False
