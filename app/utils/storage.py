import os
from app.core.config import settings
from datetime import datetime, timedelta
from typing import Optional


def generate_presigned_url(filename: str, expires_in: int = 3600) -> Optional[str]:
    file_path = os.path.join(settings.RECORDINGS_DIR, filename)
    
    if not os.path.exists(file_path):
        return None

    expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
    
    return f"/recordings/{filename}?expires={expiration_time.isoformat()}"