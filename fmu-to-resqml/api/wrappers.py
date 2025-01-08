"""
All api wrapper functions
"""


def handle_exceptions(func: any) -> any:
    """
    Wrapper function for handling exceptions.
    """

    def wrapper(*args, **kwargs):
        try:
            # Try to return the function value
            return func(*args, **kwargs)
        except Exception as e:
            if len(e.args) <= 1:
                raise e
            status = e.args[1]

            # If the function returns a "Unauthorized", "Not Found" or "Not Implemented" error
            if status in [401, 404, 501]:
                return e.args

            # If not, raise the exception further
            raise e

    return wrapper
