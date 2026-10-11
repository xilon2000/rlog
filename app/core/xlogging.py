import logging.config

from asgi_correlation_id import CorrelationIdFilter
from fastapi import Request, Response

from app.core.config import settings


logger = logging.getLogger(__name__)


def _is_swagger_request(request: Request) -> bool:
    return request.url.path in ["/docs", "/openapi.json"]

def _is_list_messages_request(request: Request) -> bool:
    return request.method == "GET" and request.url.path == "/remote_log/messages"

def _is_append_message_request(request: Request) -> bool:
    return request.method == "POST" and request.url.path == "/remote_log/messages"

def _is_replicate_message_request(request: Request) -> bool:
    return request.method == "POST" and request.url.path == "/remote_log/replicate_message"

def get_hostname(request: Request):
    return settings.NODE_ID if request.url.hostname == "localhost" else request.url.hostname

async def log_request(request: Request, call_next):
    if _is_swagger_request(request):
        return await call_next(request)
    
    if _is_list_messages_request(request):
        logger.info(f"REQUEST list_messages to {get_hostname(request)} {request.method} {request.url.path}")
        response: Response = await call_next(request)
        logger.info(f"RESPONSE list_messages to {get_hostname(request)} {request.method} {request.url.path} {response.status_code}")
        return response

    if _is_append_message_request(request):
        logger.info(f"REQUEST append_message to {get_hostname(request)} {request.method} {request.url.path}")
        response: Response = await call_next(request)
        logger.info(f"RESPONSE append_message to {get_hostname(request)} {request.method} {request.url.path} {response.status_code}")
        return response

    if _is_replicate_message_request(request):
        logger.info(f"REQUEST replicate_message to {get_hostname(request)} {request.method} {request.url.path}")
        response: Response = await call_next(request)
        logger.info(f"RESPONSE replicate_message to {get_hostname(request)} {request.method} {request.url.path} {response.status_code}")
        return response        

    return await call_next(request)


def configure_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'correlation_id_filter': {
                '()': CorrelationIdFilter,
            },
        },
        'formatters': {
            'system_console_formatter': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)d [None] %(message)s',
            },
            'app_console_formatter': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)d [%(correlation_id)s] %(message)s',
            },
        },
        'handlers': {
            'system_console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'system_console_formatter',
                'stream': 'ext://sys.stderr'
            },
            'app_console_handler': {
                'class': 'logging.StreamHandler',
                'filters': ['correlation_id_filter'],
                'formatter': 'app_console_formatter',
                'stream': 'ext://sys.stderr'
            },
        },
        'root': {
            'handlers': ['system_console_handler'],
            'level': 'INFO',
        },
        'loggers': {
            'app': {
                'level': 'INFO', 
                'handlers': ['app_console_handler'],
                'propagate': False,
            },
            'httpx': {
                'level': 'WARNING',
                'handlers': ['app_console_handler'],
                'propagate': False,
            },
            'httpcore': {
                'level': 'WARNING',
                'handlers': ['app_console_handler'],
                'propagate': False,
            },
            'asgi_correlation_id': {
                'level': 'WARNING',
                'handlers': ['app_console_handler'],
                'propagate': False,
            },
            'uvicorn': {
                'level': 'WARNING',
                'handlers': ['system_console_handler'],
                'propagate': False,
            },
            'uvicorn.error': {
                'level': 'WARNING',
                'handlers': ['system_console_handler'],
                'propagate': False,
            },
            'uvicorn.access': {
                'level': 'WARNING',
                'handlers': ['system_console_handler'],
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
