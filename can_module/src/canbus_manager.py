#!/usr/bin/python
import sys, time
sys.path.append('/home/pi/hlc')

import signal
import pigpio_pwm
import syslog
import traceback
from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from common.src.base_module import BaseModule
from common.src.mqtt_message_protocol import Message
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import signal
from can_module.src.PrimaryControlMessage import PrimaryControlMessage
from can_module.src.ReturnStatusMessage import ReturnStatusMessage
from getkey import getkey, keys

VERSION = "1.0"
MAX_PWM_TIME = 1900.0
MIN_PWM_TIME = 1100.0
MID_PWM_TIME = 1500.0
MAX_SPEED = 10000
MAX_STEERING = 10000
DEFAULT_BRAKE = -2000
CAN_INTERFACE = 'can0'
TIME_BEFORE_BREAK_MS = 100




STEERING_PWM_INPUT_PIN = 17  # PI GPIO
SPEED_PWM_INPUT_PIN = 22     # PI GPIO

STATUS_TOPIC = "Afron/status"
EMERGENCY_TOPIC = "Afron/emergency"
ENGINE_TOPIC = "Afron/engine"
HANDBRAKE_TOPIC = "Afron/handbrake"
HD_TOPIC = "Afron/humandetection"
ULTRASONIC_TOPIC = "Afron/ultrasonic"
PWM_SPEED_TOPIC = "Afron/pwm_speed"
PWM_STEERING_TOPIC = "Afron/pwm_steering"

stop_run = False


@dataclass_json
@dataclass
class CanbusConfiguration:
    interface: str = "can0"
    bitrate: int = 500000


class CanbusManager(BaseModule):

    MSG_TYPE_CANBUS_STATUS = "CanbusManager.status"
    MSG_TYPE_HEARTBEAT_TIMEOUT = "CanbusManager.HeartbeatTimeout"

    def __init__(self, *args, **kwargs):
        super().__init__("CanbusManager", VERSION)
        self.PrimaryControlMessage = None
        self.HurtBeatMessage = None
        self.Emergency = False
        self.MESSAGE_HANDLERS_SWITCHER = {
            ENGINE_TOPIC: self.engine_callback,
            HANDBRAKE_TOPIC: self.handbrake_callback,
            HD_TOPIC: self.hd_callback,
            ULTRASONIC_TOPIC: self.ultrasonic_callback,
            EMERGENCY_TOPIC: self.emergency_callback
        }

    def emergency_callback(self, client, userdata,  msg: Message):
        print("emergency_callback")
        self.emergecy_stop()

    def hd_callback(self, client, userdata,  msg: Message):
        print("hd_callback")
        if msg.message:
            self.stop_engine()

    def ultrasonic_callback(self, client, userdata,  msg: Message):
        print("ultrasonic_callback")
        if msg.message:
            self.stop_engine()

    def engine_callback(self, client, userdata,  msg: Message):
        print("engine_callback", msg.message)
        if msg.message:
            self.start_engine()
        else:
            self.stop_engine()

    def handbrake_callback(self, client, userdata,  msg: Message):
        print("handbrake_callback")
        if msg.message:
            self.set_parking(True)
        else:
            self.set_parking(False)

    def module_thread(self):
        steering_pwn = pigpio_pwm.PulseWidthCounter(STEERING_PWM_INPUT_PIN)
        speed_pwm = pigpio_pwm.PulseWidthCounter(SPEED_PWM_INPUT_PIN)

        steering_pwn.start()
        speed_pwm.start()
        
        self.PrimaryControlMessage = PrimaryControlMessage(CAN_INTERFACE)
        self.HurtBeatMessage = ReturnStatusMessage(timeout_ms = 150, Channel = CAN_INTERFACE)
        
        self.PrimaryControlMessage.start()
                
        status = 0
        prev_speed = 1000
        prev_steering = 1000
        speed = 0
        steering = 0

        # for debug only - start the engine
        # self.start_engine()
        
        cnt = 0

        read_steering_is_aligned = False
        while not self.stop_thread:
            
            
            #print (speed,steering)
            try:
                if self.Emergency:
                        self.PrimaryControlMessage.set_gas_brake(-MAX_SPEED)
                else:        
                    if self.HurtBeatMessage.IsAlive():
                        cnt += 1

                        try:
                            steering = steering_pwn.pulse_width
                            if steering == 0:
                                steering = MID_PWM_TIME
                            ksteering = ((steering - MID_PWM_TIME) / (MID_PWM_TIME - MIN_PWM_TIME))  # -1 <= steering >= 1
                            
                                
                            if ksteering > 1:
                                ksteering = 1
                            if ksteering < -1:
                                ksteering = -1
                                
                            if prev_steering != ksteering:        
                                prev_steering = ksteering
                                set_steering = int(round(ksteering * MAX_STEERING)) 
                                if (set_steering < -9999):
                                    set_steering = -9999
                                self.PrimaryControlMessage.set_steering(set_steering)
                                
                                #self.PrimaryControlMessage.update_data()
                        except:
                                self.log.error("Steering error")
                                self.log.error(traceback.print_exc())
                        time.sleep(0.05) 
                        try:
                            speed = speed_pwm.pulse_width
                            if speed == 0:
                                speed = MID_PWM_TIME
                            kspeed = ((speed - MID_PWM_TIME) / (MID_PWM_TIME - MIN_PWM_TIME))  # -1 <= speed >= 1
                        
                            if kspeed > 1:
                                kspeed = 1
                            if kspeed < -1:
                                kspeed = -1
                            
                            if prev_speed != kspeed:
                                prev_speed = kspeed
                                
                                set_speed = int(round(kspeed * MAX_SPEED))
                                #if set_speed < 10:
                                #    set_speed = DEFAULT_BRAKE
                                self.PrimaryControlMessage.set_gas_brake(set_speed)
                                #self.PrimaryControlMessage.update_data()
                                print (speed, set_speed)

                        except:
                            self.log.error("Speed error")
                            self.log.error(traceback.print_exc())
                            
                        #print (speed,steering)
                    else:
                        #self.PrimaryControlMessage.set_gas_brake(-MAX_SPEED)
                        pass
                self.PrimaryControlMessage.update_data()
                 # ??
            except:
                self.log.error(traceback.print_exc())
        self.PrimaryControlMessage.stop()

    def set_parking(self, state):
        print("set_parking=", state)

    def stop_engine(self):
        print("stop_engine")

    def start_engine(self):
        print("start_engine")

    def emergecy_stop(self):
        self.Emergency = True
        print("emergecy_stop")
        
    def clear_emergecy_stop(self):
        self.Emergency = False
        print("clear_emergecy_stop")

def signal_handler(sig, frame):
    global stop_run
    stop_run = True


def main():
    global stop_run
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    canbus = CanbusManager()
    canbus.start()

    while not stop_run:
        try:
            key = getkey()
            if key == '?':
                print(canbus.get_last_heartbeat().to_json())
            elif key == 'q':
                canbus.emergecy_stop()
                stop_run = True
                
        except Exception as e:
            canbus.log.error(e)

    canbus.stop()
    canbus.log.info("Exit")


if __name__ == "__main__":
    main()
