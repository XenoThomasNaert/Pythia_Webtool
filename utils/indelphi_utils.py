import io
import logging
from contextlib import redirect_stdout


def init_model_quiet(indelphi_module, celltype: str, logger: logging.Logger) -> None:
    """Call inDelphi.init_model() suppressing its stdout noise, log a clean message instead."""
    with redirect_stdout(io.StringIO()):
        indelphi_module.init_model(celltype=celltype)
    logger.info("inDelphi model selected — %s", celltype)
