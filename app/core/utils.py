from sqlalchemy.orm import Session

from app.db.models import User
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    logging.info(f"Query-dan qaytgan user: {user}")
    return user
