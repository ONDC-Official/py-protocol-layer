import logging
import logging_loki
import os

def handle_logError(record):
    print(record)

def get_logger():


    handler = logging_loki.LokiHandler(
        url= os.getenv("LOKI_URL", "some-url")+"/loki/api/v1/push", 
        tags={"app": "buyer-protocol"},
        version='1',
        
    )
    handler.handleError = handle_logError
    logger = logging.getLogger("loki")
    logger.addHandler(handler)
    logger.log(level=1,msg="hello")
    return logger