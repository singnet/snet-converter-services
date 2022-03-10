def update_in_db(*decorator_args, **decorator_kwargs):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args) == 0:
                raise Exception('should be used in class method')
            func_self = args[0]
            try:
                data = func(*args, **kwargs)
                func_self.session.commit()
                return data
            except Exception as e:
                func_self.session.rollback()
                raise e

        return wrapper

    return decorator


def read_from_db(*decorator_args, **decorator_kwargs):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args) == 0:
                raise Exception('should be used in class method')
            func_self = args[0]
            try:
                data = func(*args, **kwargs)
                func_self.session.commit()
                return data
            except Exception as e:
                func_self.session.rollback()
                raise e

        return wrapper

    return decorator
