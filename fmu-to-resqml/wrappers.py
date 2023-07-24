"""
    All wrapper functions
"""

def try_object_implemented(func): 
    def wrapper(*args, **kwargs):
        try:
            # Try to return the function value
            return func(*args, **kwargs)
        except Exception as e:
            # If the function returns a "Not implemented" error, return the exception arguments
            if len(e.args) > 1 and e.args[1] == 501:
                return e.args
            
            # If not, raise the exception further
            raise e
    
    return wrapper