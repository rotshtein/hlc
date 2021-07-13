from abc import ABC
from dataclasses import dataclass
from bitstruct import *
from typing import ClassVar, Type
from typing import TypeVar


import can

#u – unsigned integer
# s – signed integer
# f – floating point number of 16, 32, or 64 bits
# b – boolean
# t – text (ascii or utf-8)
# r – raw, bytes
# p – padding with zeros, ignore
# P – padding with ones, ignore

T = TypeVar('T', bound='MessageWrapper')


@dataclass
class MessageWrapper(ABC):
    @classmethod
    def from_msg(cls:Type[T], msg: can.Message) -> T:
        parts = cls.format.unpack(msg.data)
        return cls(*parts)

    def to_msg(self):
        data:bytes = self.__class__.format.pack(*list(vars(self).values()))
        padded_data = data.ljust(8, b'\0')
        return can.Message(arbitration_id=self.__class__.id, data=padded_data, is_extended_id=False)

@dataclass
class Message70HLCSecondary(MessageWrapper):
    id: ClassVar[int] = 0x70
    format:ClassVar[CompiledFormat] = compile('p8 p2b1p2b1p1b1 u2p3b1p1b1 u8 u8')

    payload2_activation:bool = False
    lights_noise_cutoff:bool = False
    road_lights: bool = False
    transfer: int = 0
    horn_on:bool = False
    keyswitch_on:bool = False
    gears_direction:int = 0
    parking_brake:int = 0
    
@dataclass
class Message50HLCPrimary(MessageWrapper):
    id: ClassVar[int] = 0x50
    format:ClassVar[CompiledFormat] = compile('u8 u8 s16 s16 p8 u8')

    shutdown: int = 0
    estop: int = 0
    steering_position: int = 0
    gas_brake_position: int = 0
    llc_reset: int = 0