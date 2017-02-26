def static_func_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate



def valid_field_filters(*filters):
    def decorate(Cls):
        Cls.__valid_filters__ = filters

        def __can_filter_on(filter):
            return filter in Cls.__valid_filters__

        Cls._can_filter_on = __can_filter_on
        return Cls
    return decorate


