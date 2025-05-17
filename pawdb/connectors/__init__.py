import logging
from pythonjsonlogger import jsonlogger


# create a custom JSON formatter to remove null values
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        return {key: value for key, value in log_record.items() if value is not None}


# Configure logger
logger = logging.getLogger("pawdb")
logger.setLevel(logging.INFO)

# Add a JSON formatter to the logger
if not logger.hasHandlers():
    stream_handler = logging.StreamHandler()
    json_formatter = CustomJsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(method)s %(query)s %(rows)s %(execution_time)s"
    )
    stream_handler.setFormatter(json_formatter)
    logger.addHandler(stream_handler)
