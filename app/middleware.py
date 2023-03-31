import logging
import random
import string
import time
from typing import Any, Awaitable, Callable, TypeAlias

from fastapi import Request

logger = logging.getLogger(__name__)

MiddlewareType: TypeAlias = Callable[[Request, Callable | None],
                                     Awaitable[Any]]


async def log_requests(request: Request,
                       call_next: MiddlewareType) -> Awaitable[Any]:
    """Промежуточный слой для логгирование запроса."""
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"REQUEST START rid={idem} "
                f"start request path={request.url.path}")
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Got error")
        raise
    finally:
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        logger.info(f"END REQUEST rid={idem}"
                    f" completed_in={formatted_process_time}ms")

    return response
