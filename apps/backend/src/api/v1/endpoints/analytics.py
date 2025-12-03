from typing import List
from fastapi import APIRouter, Depends, status
from src.api.deps import get_analytics_service
from src.services.analytics_service import AnalyticsService
from src.db.schemas import analytics as analytics_schema

router = APIRouter()

@router.get(
    "/summary",
    response_model=analytics_schema.DashboardSummary,
    status_code=status.HTTP_200_OK,
    summary="Get summary cards (Balance, Income, Expenses)"
)
def get_dashboard_summary(
        service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Returns data for the top 4 cards of the dashboard:
    - Total Balance (Lifetime)
    - Current Month Revenue (+ % vs last month)
    - Current Month Expenses (+ % vs last month)
    - Current Month Savings (+ % of revenue)
    """
    return service.get_summary_cards()


@router.get(
    "/spending-by-category",
    response_model=List[analytics_schema.CategorySpending],
    status_code=status.HTTP_200_OK,
    summary="Get expenses grouped by category for the current month"
)
def get_spending_by_category(
        service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Data for the Pie Chart. Returns categories with their total amounts
    and percentage share of total expenses for the current month.
    """
    return service.get_spending_by_category()


@router.get(
    "/monthly-evolution",
    response_model=List[analytics_schema.MonthlyEvolution],
    status_code=status.HTTP_200_OK,
    summary="Get historical evolution of income vs expenses"
)
def get_monthly_evolution(
        months: int = 6,
        service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Data for the Bar Chart. Returns monthly totals for the last N months.
    """
    return service.get_monthly_evolution(months=months)