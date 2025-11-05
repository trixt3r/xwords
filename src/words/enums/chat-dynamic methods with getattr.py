# magic method __call__
# The __call__ magic method in Python allows an instance of a class to be called as if it were a function. This is part of Python's data model and contributes to its expressive, flexible object-oriented design.

# 🧠 What __call__ Does
# When you define __call__ in a class, you're telling Python how to behave when an object of that class is "called" using parentheses — just like a regular function.

# python
class Greeter:
    def __init__(self, greeting):
        self.greeting = greeting

    def __call__(self, name):
        return f"{self.greeting}, {name}!"

greet = Greeter("Hello")
print(greet("Vincent"))  # Output: Hello, Vincent!
# 🔍 Use Cases
# Function-like objects: Useful when you want objects to behave like functions but retain state.

# Decorators: Many decorators are implemented as classes with __call__.

# Machine learning models: In frameworks like PyTorch, models are often callable objects.

# Custom control logic: You can encapsulate complex behavior in a class and trigger it with a simple call.

# 🧩 Comparison with Other Magic Methods
# Magic Method	Purpose	Example Usage
# __init__	Constructor	obj = MyClass()
# __str__	String representation	str(obj)
# __call__	Make instance callable	obj()
# __getitem__	Indexing	obj[key]
# Would you like to explore how __call__ interacts with closures, decorators, or metaclasses?


# is it possible for __getattr__ to return a method
# Yes, __getattr__ can absolutely return a method — and this is a powerful pattern in Python for dynamic behavior.

# 🧪 How It Works
# __getattr__(self, name) is called only when the attribute name is not found through the usual lookup. If you return a callable (like a function or method), it behaves just like any other method.

# Here’s a simple example:

# python
class DynamicMethods:
    def __getattr__(self, name):
        def method(*args, **kwargs):
            return f"Method '{name}' called with args={args} kwargs={kwargs}"
        return method

obj = DynamicMethods()
print(obj.foo(1, 2))  # Method 'foo' called with args=(1, 2) kwargs={}
print(obj.bar(x=42))  # Method 'bar' called with args=() kwargs={'x': 42}
# 🔍 Use Cases
# Dynamic APIs: Useful when method names encode behavior (e.g., get_user_by_id, fetch_data_from_source).

# Proxy objects: Forward method calls to another object or service.

# Mocking/stubbing: In testing, you can simulate arbitrary method calls.

# Domain-specific languages: Build expressive interfaces where method names are part of the syntax.

# ⚠️ Caveats
# __getattr__ only triggers for missing attributes. If the attribute exists, it won't be called.

# Be cautious with introspection tools like dir() or hasattr() — they may not reflect dynamically generated methods unless you override __dir__.

# Would you like to explore how this interacts with __getattribute__, or how to bind these dynamic methods with proper self references using types.MethodType?

# and is it possible for getattr to generate a method and assign it to class level ?
# Yes, Vincent — it’s possible for __getattr__ to dynamically generate a method and assign it to the class level, but it requires explicit mutation of the class dictionary. This is a powerful metaprogramming technique that blends dynamic attribute resolution with persistent behavior.

# 🧪 Example: Dynamic Method Creation and Class-Level Assignment
# python
class AutoMethod:
    def __getattr__(self, name):
        def generated_method(*args, **kwargs):
            print(f"Generated method '{name}' called with args={args}, kwargs={kwargs}")
            return f"Result of {name}"

        # Assign to class so future calls don't go through __getattr__
        setattr(self.__class__, name, generated_method)
        return generated_method

obj = AutoMethod()
obj.foo(1, 2)   # Triggers __getattr__, generates and assigns 'foo'
obj.foo(3, 4)   # Now uses the class-level method directly
# 🔍 What’s Happening
# The first call to obj.foo(1, 2) triggers __getattr__, which creates foo and binds it to the class.

# The second call to obj.foo(3, 4) bypasses __getattr__ entirely — the method now exists on the class.

# ⚠️ Caveats and Considerations
# Thread safety: If multiple threads access the same object, race conditions may occur during assignment.

# Instance vs class scope: Assigning to self.__class__ affects all instances. If you want per-instance behavior, assign to self.

# Binding: Methods assigned this way are not automatically bound to self. You may need to wrap them using types.MethodType:

# python
# import types
# setattr(self.__class__, name, types.MethodType(generated_method, self))

# Would you like to explore how this pattern compares to using metaclasses or decorators for dynamic method injection?

#################################################
# can i use this pattern with int enum ?
# Yes, Vincent — you can use this dynamic method-generation pattern with IntEnum, but with important caveats due to how Enum classes are structured in Python.

# 🧠 Enum Constraints
# Python’s Enum (including IntEnum) is designed to be immutable and closed after creation:

# You cannot add members to an Enum after it's defined.

# You can add methods dynamically, but only to the class — not to individual enum members.

# __getattr__ can be used on the class to intercept missing attributes, but it won’t be triggered on enum members.

# ✅ What You Can Do
# You can define __getattr__ on the IntEnum class to dynamically generate methods and assign them to the class:

# python
from enum import IntEnum

class DynamicEnum(IntEnum):
    FOO = 1
    BAR = 2

    def __getattr__(cls, name):
        def generated_method(*args, **kwargs):
            print(f"Generated method '{name}' called with args={args}, kwargs={kwargs}")
            return f"Result of {name}"
        setattr(cls, name, generated_method)
        return generated_method
def test1():
    # Attach __getattr__ to the class, not instance
    DynamicEnum.__getattr__ = classmethod(DynamicEnum.__getattr__)

    # Now call a dynamically generated method
    DynamicEnum.baz(42)  # Generates and assigns 'baz' to the class
    DynamicEnum.baz(99)  # Uses the cached method

# test1()


# ⚠️ Limitations
# Enum members like DynamicEnum.FOO won’t trigger __getattr__ — only the class itself (DynamicEnum) will.

# You must use classmethod or metaclass logic to intercept at the class level.

# If you want per-member behavior, consider subclassing with custom methods or using a metaclass.

# 🧬 Alternative: Metaclass for Enum
# For deeper control, you can define a metaclass that injects methods dynamically:

# python
from enum import IntEnum, EnumMeta


class DynamicMeta(EnumMeta):
    def __getattr__(cls, name):
        if name not in ["custom","baz"]:
            return super().__getattribute__(name)
        def generated_method(*args, **kwargs):
            print(f"[Meta] Generated '{name}' with args={args}")
            return f"Meta result of {name}"
        print(f"NEW METHOD {name}    ")
        setattr(cls, name, generated_method)
        return generated_method


class MetaEnum(IntEnum, metaclass=DynamicMeta):
    A = 1
    B = 2

# MetaEnum2 = MetaEnum("MetaEnum", [("A", 1),("B",2)])

MetaEnum.custom(123)  # Works via metaclass

MetaEnum.custom(456)  # Works via metaclass
MetaEnum.A.custom(12)
MetaEnum.B.baz(43)

# 🧬 Dynamic Subclassing of IntEnum
# You can use EnumMeta directly to create a new enum class at runtime:

# python
from enum import IntEnum, EnumMeta

def create_enum_subclass(name, base_enum, members, init_func=None):
    # Prepare the class dictionary
    class_dict = {}

    # Optionally inject a custom __init__
    if init_func:
        class_dict['__init__'] = init_func

    # Create the new Enum class dynamically
    return EnumMeta(name, (base_enum,), class_dict)(members)

def test3():
    # Example: define members as a dict
    members = {
        'ALPHA': (10, "First"),
        'BETA': (20, "Second"),
        'GAMMA': (30, "Third")
    }

    # Custom __init__ to handle tuple values
    def custom_init(self, value, label):
        self.label = label

    # Create the subclass
    NewStatus = create_enum_subclass("NewStatus", IntEnum, members, custom_init)

    print(NewStatus.ALPHA.value)   # 10
    print(NewStatus.ALPHA.label)   # "First"

# test3()

# 🧠 Key Concepts
# EnumMeta(name, bases, class_dict) dynamically creates an enum class.

# The members argument must be a mapping of names to values.

# If values are tuples, your __init__ must unpack them accordingly.

# You can inject methods, properties, or even override __new__ if needed.

# ⚠️ Caveats
# You cannot mutate enum members after creation.

# All members must conform to the expected signature of __init__.

# If you override __new__, you must return a proper instance of the enum base.