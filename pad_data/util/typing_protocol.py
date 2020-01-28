from typing import Dict, Protocol

# type hint for an instance of a non specific dataclass
# https://stackoverflow.com/questions/54668000

class IsDataclass(Protocol):
    __dataclass_fields__: Dict

# TODO: create base class for skill effects
class IsSkillEffect(IsDataclass):
    pass
