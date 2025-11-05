from enum import IntEnum

class DynamicEnum(IntEnum):
    FOO = 1
    BAR = 2
    def __init__(self, value):
        super(IntEnum, self).__init__(value) 
        # print(f"Initialized {self.name} with value {self.value}")

    @classmethod
    def __getattr__(cls, name):
        if name not in ["tuz", "baz"]:
            return super(IntEnum, cls).__getattribute__(name)
        def generated_method(*args, **kwargs):
            print(f"Generated method '{name}' called with args={args}, kwargs={kwargs}")
            return f"Result of {name}"
        setattr(cls, name, generated_method)
        return generated_method

# Attach __getattr__ to the class, not instance
# DynamicEnum.__getattr__ = classmethod(DynamicEnum.__getattr__)

# Now call a dynamically generated method
DynamicEnum.baz(42)  # Generates and assigns 'baz' to the class
DynamicEnum.baz(99)  # Uses the cached method