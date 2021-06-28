from can_module.src.CanAction import CanAction
from datetime import datetime

MESSGAE_ID: int = 0x60

class ReturnStatusMessage(CanAction):
    def __init__(self, timeout_ms: float = 150.0, Channel: str='can0') -> None:
        super().__init__(mask=0x7ff, id=MESSGAE_ID, Channel=Channel)
        self.last_received = datetime.now()
        self.message_timeout = timeout_ms  # micro to mili
         
    def on_message(self, msg) -> None:
        self.last_received = datetime.now()
        
        
    def build_buffer(self) -> bytes:
        self.data = [0 * 8]
        return self.data
    
    def IsAlive(self):
        return  ((datetime.now() - self.last_received).total_seconds()) * 1000 <= self.message_timeout
    
    
        
        
    