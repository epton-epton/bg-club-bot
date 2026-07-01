import asyncio
import logging

from bgclub.db.session import async_session_factory
from bgclub.services.sessions import send_session_reminders

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 60


async def session_reminder_loop() -> None:
    while True:
        try:
            async with async_session_factory() as session:
                sent = await send_session_reminders(session)
                if sent:
                    logger.info("Sent %s session reminder(s)", sent)
        except Exception:
            logger.exception("Session reminder loop failed")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
