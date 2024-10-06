import logging
import sys

#logger.basicConfig()
root = logging.getLogger()
root.setLevel(logging.INFO)
root.propagate = False

handler = logging.StreamHandler(sys.stdout)
#handler.setLevel(logger.INFO)
formatter = logging.Formatter('%(process)d %(thread)d %(asctime)s [%(name)s][%(levelname)s]::%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# Add werkzeug logs to the root logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)  # Set to same level as root logger
werkzeug_logger.addHandler(handler)


def log(*args,**kwargs):
    logging.info(*args)


def log_error(*args, **kwargs):
    logging.exception(*args)


def debug(*args,**kwargs):
    logging.debug(*args)