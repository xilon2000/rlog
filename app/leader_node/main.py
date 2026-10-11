import logging

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.core.config import settings
from app.core.xlogging import configure_logging, log_request
from .lifespan import lifespan
from .router import router


configure_logging() 

def create_leader_app():
    app = FastAPI(
        title=settings.title,
        description= settings.description,
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    app.middleware("http")(log_request)
    app.add_middleware(CorrelationIdMiddleware, header_name=settings.correlation_id_header_name)
    
    app.include_router(router=router)

    return app
    
app = create_leader_app()

logger = logging.getLogger(__name__)
