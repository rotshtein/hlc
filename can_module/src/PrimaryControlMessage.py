from can_module.src.PriodicMessage import PeriodicMessage
from struct import *
from enum import IntEnum


MESSGAE_ID: int = 0x50

class PrimaryControlMessageCommands(IntEnum):
    CLEAR = 0
    ESTOP = 0x0c
    RESET = 0x0a

class PrimaryControlMessage(PeriodicMessage):
    def __init__(self, Channel: str) -> None:
        super().__init__(period=0.02, duration = None, id=MESSGAE_ID, Channel=Channel)
        self.shutdown:PrimaryControlMessageCommands = PrimaryControlMessageCommands.CLEAR
        self.estop:PrimaryControlMessageCommands = PrimaryControlMessageCommands.CLEAR
        self.steering: int = 0
        self.gas_break: int = 0
        self.spare:int = 0
        self.reset:PrimaryControlMessageCommands = PrimaryControlMessageCommands.CLEAR
        #self.set_message(data = self.build_buffer(), period=0.2)
                
    def set_shutdown(self, value:int) -> None:
        self.shutdown = value
        
    def set_estop(self) -> None:
        self.estop = PrimaryControlMessageCommands.ESTOP
        
    def clear_estop(self) -> None:
        self.estop = PrimaryControlMessageCommands.CLEAR
        
    def set_steering(self, value:int) -> None:
        self.steering = value
        
    def set_gas_brake(self, value:int) -> None:
        self.gas_break = value
        
    def set_reset(self) -> None:
        self.reset = PrimaryControlMessageCommands.RESET
        
    def clear_reset(self) -> None:
        self.reset = PrimaryControlMessageCommands.CLEAR

        
    def build_buffer(self) -> bytes:
        self.data = pack(">BBhhBB",self.shutdown, self.estop, self.steering, self.gas_break, self.spare, self.reset)            
        return self.data
    
    def update_data(self) -> bool:
        self.set_data(self.build_buffer())
        
        
    