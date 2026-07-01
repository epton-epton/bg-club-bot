from pydantic import BaseModel

from bgclub_api.schemas.announcement import AnnouncementOut
from bgclub_api.schemas.event import EventOut


class FeedOut(BaseModel):
    events: list[EventOut]
    announcements: list[AnnouncementOut]
