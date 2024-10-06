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

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)


def log(*args,**kwargs):
    logging.info(*args)


def log_error(*args, **kwargs):
    logging.exception(*args)


def debug(*args,**kwargs):
    logging.debug(*args)