"""
TaskFlow's background worker.

Deliberately a simple polling loop rather than Celery + Redis/RabbitMQ -
the point of this service is to give you a genuine second process to
deploy, monitor, and reason about (for Helm/GitOps/observability later),
not to teach you a message broker. Swap in Celery later if you want the
extra depth; it's not required for any of the 5 projects.

Every POLL_INTERVAL_SECONDS, it looks for incomplete tasks older than
REMINDER_AFTER_MINUTES and logs a reminder. In a real system this is
where you'd send an email/Slack message instead of a log line.
"""
import os
import time
import datetime
import logging

from app.database import SessionLocal
from app import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker] %(message)s")
log = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
REMINDER_AFTER_MINUTES = int(os.getenv("REMINDER_AFTER_MINUTES", "10"))


def check_overdue_tasks():
    db = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=REMINDER_AFTER_MINUTES
        )
        overdue = (
            db.query(models.Task)
            .filter(models.Task.is_complete.is_(False))
            .filter(models.Task.created_at < cutoff)
            .all()
        )
        for task in overdue:
            log.info("Reminder: task #%s '%s' is still incomplete", task.id, task.title)
    finally:
        db.close()


def main():
    log.info(
        "Worker starting. Polling every %ss, reminding after %s minutes.",
        POLL_INTERVAL_SECONDS,
        REMINDER_AFTER_MINUTES,
    )
    while True:
        try:
            check_overdue_tasks()
        except Exception as exc:  # noqa: BLE001 - worker should never crash-loop on a transient DB error
            log.error("Error while checking overdue tasks: %s", exc)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
