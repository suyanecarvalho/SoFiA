import datetime
import calendar
from sqlalchemy.orm import Session
from src.db.crud import crud_recurrence, crud_user
from src.db.models import models
from src.core.logger import logger
from src.db.schemas import transaction as transaction_schema
from src.services.transaction_service import TransactionService

class RecurrenceService:
    def __init__(self, db: Session):
        self.db = db
        # We keep TransactionService here for the actual creation of the record
        self.transaction_service = TransactionService(db)

    def process_daily_recurrences(self):
        """
        Main Engine: Checks all active rules and generates transactions if due.
        """
        logger.info("🔄 Starting Daily Recurrence Check...")
        active_rules = crud_recurrence.get_active_recurrences(self.db)
        today = datetime.date.today()
        count = 0

        for rule in active_rules:
            try:
                # Standard check based on "today"
                if self._is_due(rule, today):
                    # Determine specific date for this month
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    target_day = min(rule.recurrence_day, last_day)
                    tx_date = today.replace(day=target_day)

                    self._execute_recurrence(rule, tx_date)
                    count += 1
            except Exception as e:
                logger.error(f"Failed to process recurrence ID {rule.id}: {e}", exc_info=True)

        if count > 0:
            self.db.commit()
        logger.info(f"Recurrence Check Complete. Generated {count} transactions.")

    def ensure_salary_for_month(self, user_id: int, reference_date: datetime.date):
        """
        Triggered when a user creates a transaction manually.
        Checks if the User has a Salary Recurrence.
        If yes, checks if it has been generated for the 'reference_date' month.
        If not, generates it immediately.
        """
        try:
            user = crud_user.get_user(self.db, user_id)
            if not user or not user.salary_recurrence_id:
                return
            rule = self.db.query(models.RecurrentTransaction).filter(
                models.RecurrentTransaction.id == user.salary_recurrence_id,
                models.RecurrentTransaction.is_active == True
            ).first()
            if not rule:
                return
            start_of_month = reference_date.replace(day=1)
            last_day_num = calendar.monthrange(reference_date.year, reference_date.month)[1]
            end_of_month = reference_date.replace(day=last_day_num)
            existing_tx = crud_recurrence.get_recurrence_execution_for_period(
                self.db, rule.id, start_of_month, end_of_month
            )
            if not existing_tx:
                logger.info(f"💰 Triggering Missing Salary for {reference_date.strftime('%B %Y')}")
                payday_day = min(rule.recurrence_day, last_day_num)
                target_payday_date = reference_date.replace(day=payday_day)
                self._execute_recurrence(rule, target_payday_date)
                self.db.flush()

        except Exception as e:
            logger.error(f"Failed to ensure salary for month: {e}", exc_info=True)

    def _is_due(self, rule: models.RecurrentTransaction, today: datetime.date) -> bool:
        """
        Determines if the rule should run based on 'today'.
        """
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        target_day = min(rule.recurrence_day, last_day_of_month)
        if today.day < target_day:
            return False
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=last_day_of_month)
        existing_tx = crud_recurrence.get_recurrence_execution_for_period(
            self.db, rule.id, start_of_month, end_of_month
        )
        if existing_tx:
            return False
        return True

    def _execute_recurrence(self, rule: models.RecurrentTransaction, tx_date: datetime.date):
        """
        Clones the base transaction and links it to the recurrence rule.
        Accepts the specific date to execute on.
        """
        base = rule.base_transaction
        if not base:
            logger.warning(f"Recurrence {rule.id} has no base transaction. Skipping.")
            return
        new_tx_data = {
            "amount": base.amount,
            "description": base.description,
            "reference_date": tx_date,
            "transaction_type": base.transaction_type,
            "category_id": base.category_id
        }
        if base.transaction_type == "expense":
            schema_cls = transaction_schema.ExpenseCreate
            schema_data = {
                **new_tx_data,
                "transaction_type": "expense",
                "category_id": base.category_id
            }
        else:
            schema_cls = transaction_schema.IncomeCreate
            schema_data = {
                **new_tx_data,
                "transaction_type": "income",
                "category_id": None
            }
        tx_create = schema_cls(**schema_data)
        new_tx = self.transaction_service.create_transaction(
            user_id=rule.user_id,
            transaction_data=tx_create,
            check_salary_trigger=False
        )
        new_tx.created_by_recurrence_id = rule.id
        self.db.add(new_tx)
        logger.info(f"Generated recurrent transaction: {new_tx.description} for {tx_date}")