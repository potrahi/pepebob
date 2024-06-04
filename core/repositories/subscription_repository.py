import logging
from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.entities.subscription_entity import Subscription as SubscriptionEntity

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SubscriptionRepository:
    def get_list(self, session: Session) -> List[SubscriptionEntity]:
        logger.debug("Fetching list of subscriptions")
        result = session.execute(select(SubscriptionEntity)).scalars().all()
        subscriptions = list(result)
        logger.debug(f"Fetched subscriptions: {subscriptions}")
        return subscriptions

    def update_subscription(self, session: Session, id: int, since_id: int) -> None:
        logger.debug(f"Updating subscription id={id} with since_id={since_id}")
        session.execute(
            update(SubscriptionEntity)
            .where(SubscriptionEntity.id == id)
            .values(since_id=since_id)
        )
        session.commit()
        logger.debug(f"Subscription id={id} updated with since_id={since_id}")
