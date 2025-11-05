# 🧬 Dynamic Subclassing of IntEnum
# You can use EnumMeta directly to create a new enum class at runtime:

# python
from enum import IntEnum, EnumMeta

def create_enum_subclass_generic(name, base_enum, members, methods={}):
    # Prepare the class dictionary
    class_dict = {}

    # Optionally inject a custom __init__
    for m in methods:
        class_dict[m] = methods[m]
    # if init_func:
    #     class_dict['__init__'] = init_func

    # Create the new Enum class dynamically
    return EnumMeta(name, (base_enum,), class_dict)(members)

def create_enum_subclass(name, base_enum, members, init_func=None):
    # Prepare the class dictionary
    class_dict = {}

    # Optionally inject a custom __init__
    if init_func:
        class_dict['__init__'] = init_func

    # class_dict._member_names = list(members.keys())

    # Create the new Enum class dynamically
    return EnumMeta(name, (base_enum,), class_dict)(members)

    # return EnumMeta(name, (base_enum,), class_dict)(members)

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
# 🧠 Key Concepts
# EnumMeta(name, bases, class_dict) dynamically creates an enum class.

# The members argument must be a mapping of names to values.

# If values are tuples, your __init__ must unpack them accordingly.

# You can inject methods, properties, or even override __new__ if needed.

# ⚠️ Caveats
# You cannot mutate enum members after creation.

# All members must conform to the expected signature of __init__.

# If you override __new__, you must return a proper instance of the enum base.