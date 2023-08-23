import logging
import logging_loki


def handle_logError(record):
    print(record)

def get_logger():


    handler = logging_loki.LokiHandler(
        url="http://192.168.11.146:3100/loki/api/v1/push", 
        tags={"app": "buyer-protocol"},
        version='1',
        
    )
    handler.handleError = handle_logError
    logger = logging.getLogger("loki")
    logger.addHandler(handler)
    logger.log(level=1,msg="hello")
    return logger