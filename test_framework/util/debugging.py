
def debug(func):
    def wrapper(*args, **kwargs):
      print("DEBUG: %s %s %s" % (func.__name__, args, kwargs))
      return func(*args, **kwargs)
    return wrapper
  
      

