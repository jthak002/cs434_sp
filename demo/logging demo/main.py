import logging
import time
from log_test2 import another_module


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s: Line %(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel('DEBUG')

logger.info("This is an formation message")
logger.debug("This is an debug message")
logger.error("This is an error message")


for i in range(0, 10):
    logger.info("sleeping for 1s")
    time.sleep(1)

another_module()
