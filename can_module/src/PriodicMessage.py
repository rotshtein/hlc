from can_module.src.CanAction import CanAction
from typing import List


class PeriodicMessage(CanAction):
    def __init__(self, period:float, duration: float = None, id:int = 0,  Channel: str='can0') -> None:
        super().__init__(mask = -1)
        self.data = bytearray([0 * 8])
        self.id = id
        self.period = period
        self.duration = duration
        
                
    def start(self):
        self.data = self.build_buffer()
        self.send_periodic(data = self.data, id = self.id, period = self.period, duration = self.duration)
        
    def stop(self):
        self.stop_periodic()
         
    def set_message(self, data: bytes, period:float, id: int = -1, duration: float = None) -> bool:
        if not id == -1:
            self.id = id
        return self.send_periodic(data = data, id = self.id, period = period, duration = duration)

    def set_data(self, data: bytes) -> bool:
        return self.modify_priodic(data = data)
    
    
    def set_id(self, id:int) ->bool:
        self.id = id
        return self.modify_priodic(data = self.priodic_data, id = id)
   
    def update_data(self) -> bool:
        self.set_data(self.build_buffer())
        
    def build_buffer(self) -> bytes:
        self.data = [0 * 8]
        return self.data