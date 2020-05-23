class DataObject(object):
    def __init__(self, required_attributes):
        self._required_attributes = required_attributes
        self._built = False

    def __call__(self, cls, *args, **kwargs):
        def build(inner_self):
            for attr in self._required_attributes:
                try:
                    object.__getattribute__(inner_self, _get_req_attr_real_name(attr))
                except AttributeError:
                    raise ValueError("Missing required attribute %s" % attr)
            self._built = True

            if hasattr(inner_self, "post_build"):
                inner_self.post_build()

            return inner_self

        def _get_req_attr_real_name(req_attr_name) -> str:
            return "_" + req_attr_name

        def __getattribute__(inner_self, name):
            if self._built or name == "build":
                if name in self._required_attributes:
                    name = _get_req_attr_real_name(name)
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

        cls.build = build
        cls.__getattribute__ = __getattribute__
        cls.__str__ = __str__
        cls.__repr__ = __str__
        return cls
