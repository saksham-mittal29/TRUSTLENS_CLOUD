from sqlalchemy.orm import Session

from app.models import User


def get_or_create_user(
    db: Session,
    firebase_uid: str
):
    """
    Find a user by Firebase UID.
    Create the user if they do not exist.
    """

    user = (
        db.query(User)
        .filter(User.firebase_uid == firebase_uid)
        .first()
    )

    if user:
        return user

    user = User(
        firebase_uid=firebase_uid
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
