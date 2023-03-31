import random
import string
import logging
import time
from typing import Callable, TypeAlias
from fastapi import Request, Response


logger = logging.getLogger(__name__)

MiddlewareType: TypeAlias = Callable[[Request, Callable | None], Response]


async def log_requests(request: Request,
                       call_next: MiddlewareType) -> Response:
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
