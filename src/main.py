from __future__ import annotations

import uvicorn

from src.infrastructure.config.settings import get_settings
from src.presentation.app_factory import create_app

app = create_app()


def main() -> None:
    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=False)


if __name__ == "__main__":
    main()
