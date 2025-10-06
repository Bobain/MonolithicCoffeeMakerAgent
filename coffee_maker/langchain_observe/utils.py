import inspect


def get_callers_modules():
    callers_modules = []
    for caller_frame_record in inspect.stack():
        calling_module = inspect.getmodule(caller_frame_record)
        if calling_module:
            callers_modules.append(calling_module.__name__)
        else:
            callers_modules.append(caller_frame_record.filename)
    return callers_modules
