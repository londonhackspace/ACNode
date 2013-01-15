import logging

from flask import _request_ctx_stack

def set_default_format(app, fmt):
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.propagate = False

def add_context_filter(app, **kwargs):
    flt = ContextFilter(**kwargs)
    app.logger.addFilter(flt)

class ContextFilter(logging.Filter):
    def __init__(self, default=None, **kwargs):
        self.funcs = kwargs
        self.default = default

    def filter(self, record):
        ctx = _request_ctx_stack.top
        if ctx is None:
            for k in self.funcs.keys():
                setattr(record, k, self.default)

            return True

        for k, f in self.funcs.items():
            try:
                v = f(ctx)
            except AttributeError:
                v = None
            except Exception, e:
                logging.debug(e)
                v = None
            setattr(record, k, v)

        return True

