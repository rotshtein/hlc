import can
from can import Message
from threading import Thread
from typing import List

class CanAction:
    def __init__(self, mask = 0x7FF, id = 0, Channel = 'can0', Bustype='socketcan', Bitrate = 500000) -> None:
        self.channel = Channel
        self.id = id
        self.mask = mask
        self.bus = can.ThreadSafeBus(bustype=Bustype, channel=Channel, bitrate=Bitrate)
        self.last_message = None
        self.receice_message_count = 0 
        self.send_message_count = 0 
        
        self.send_count = 0
        self.receive_count = 0
        if not mask == -1:
            if not mask == 0:
                filter = [{"can_id": id, "can_mask": mask, "extended": False}]
                self.bus.set_filters(filter)
            self.Listiner = can.Listener()
            self.Listiner.on_message_received = self.on_message_received
            self.notifier = can.Notifier(self.bus, [self.Listiner], 0)
        self.priodic_task = None
        self.perioc_id = 0
        self.perioc_data = []
        

    #def __del__(self):
    #    self.bus.shutdown()

    def on_message_received(self, msg) -> None:
        if not ((msg.arbitration_id & self.mask) == self.id):
            return
        self.receice_message_count += 1
        self.last_message = msg
        self.on_message(msg)
    
    def on_message(self, msg):
        raise Exception(NotImplemented)
    
    def send(self,id: int, data, timeout=None) -> bool:
        try:
            msg = can.Message(arbitration_id=id, data=data, extended_id=False)
            return self.send_message(msg, timeout)
        except:
            return False
        
    def send_message(self,msg, timeout = None)->bool:
        try:
            if isinstance(msg,can.Message):
                self.send_message_count += 1
                self.bus.send(msg, timeout)
            else:
                return False
        except:
            return False
        return True
        
    def send_periodic(self, data: List[int], id: int,  period:float, duration: float = None) -> bool:
        try:
            self.perioc_id = id
            self.perioc_data = data
            msg = can.Message(arbitration_id=id, data=data, extended_id=False)
            self.priodic_task = self.bus.send_periodic(msg=msg, period=period,duration=duration)  
        except:
            return False
        return True
        
    def stop_periodic(self):
        if self.priodic_task is not None:
            self.priodic_task.srop()
            self.priodic_task = None
            
    def modify_priodic(self, data: bytes) -> bool:
        try:
            msg = can.Message(arbitration_id=self.id, data=data, extended_id=False)
            self.priodic_task.modify_data(msg)
        except:
            return False
        return True
        
        
    def stop_periodic(self)-> None:
        try:
            if self.priodic_task is not None:
                self.priodic_task.stop()
                self.priodic_task = None
        except:
            pass
    
        
    def recv(self, timeout = None) -> Message:
        return self.bus.recv(timeout)
    
    def __str__(self) -> str:
        return "CAN{0]: id={1}, Mask={2}".format(self.channel,self.id, self.mask)
    
    def get_data(self, msg) ->List[int]:
        if isinstance(msg) == can.Message:
            return msg.data
        return None
    
    def get_length(self, msg) ->int:
        if isinstance(msg) == can.Message:
            return msg.dlc
        return None
    
    def get_id(self, msg) ->int:
        if isinstance(msg) == can.Message:
            return msg.arbitration_id
        return None
            
if __name__ == '__main__':
    c = CanAction(id=0x51)
    c.send([0 * 8])