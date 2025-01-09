from loguru import logger

logger.add(
    "logs.log",
    colorize=True,
    format="[{time}] | {level: ^8} | {name: ^15} | {function: ^15} | {line: ^3} | msg: {message}",
    level="DEBUG",
)
logger = logger.opt(colors=True)
