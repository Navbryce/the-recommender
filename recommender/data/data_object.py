class DataObject(object):
    def __init__(self, required_attributes):
        self._required_attributes = required_attributes
        self._built = False

    def __call__(self, other_class_new, *args, **kwargs):
        def __new__(cls, *args, **kwargs):
            cls.build = build
            cls.__getattribute__ = __getattribute__
            cls.__str__ = __str__
            cls.__repr__ = __str__
            return super(cls.__class__, cls).__new__(cls, *args, **kwargs)

        def build(inner_self):
            for attr in self._required_attributes:
                if (
                    object.__getattribute__(inner_self, _get_req_attr_real_name(attr))
                    is None
                ):
                    raise ValueError("Missing required attribute %s" % attr)
            self._built = True
            return inner_self

        def _get_req_attr_real_name(req_attr_name) -> str:
            return "_" + req_attr_name

        def __getattribute__(inner_self, name):
            if self._built or name == "build":
                return object.__getattribute__(inner_self, name)
            raise ValueError("Not yet built")

        def __str__(inner_self) -> str:
            class_name = inner_self.__class__.__name__
            attributes_string = ", ".join(
                [
                    str(getattr(inner_self, _get_req_attr_real_name(attr)))
                    for attr in self._required_attributes
                ]
            )
            return "%s {%s}" % (class_name, attributes_string)

        return __new__
