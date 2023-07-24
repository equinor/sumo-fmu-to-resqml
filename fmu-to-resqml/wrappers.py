"""
    All wrapper functions
"""

def handle_exceptions(func): 
    def wrapper(*args, **kwargs):
        try:
            # Try to return the function value
            return func(*args, **kwargs)
        except Exception as e:
            if len(e.args) <= 1:
                raise e            
            status = e.args[1]

            # If the function returns a "Not Found" or "Not Implemented" error
            if status == 404 or status == 501:
                return e.args
            
            # If not, raise the exception further
            raise e
    
    return wrapper