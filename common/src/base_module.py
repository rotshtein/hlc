import os, sys
#sys.path.append('..')
from common.src.mqtt_client import MqttClient
from common.src.mqtt_message_protocol import Message
from paho.mqtt.client import Client, MQTTMessage
import threading
import queue
import logging
import signal
import inspect

MODULE_NAME = 'BaseModule'
debug_levels = {logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL}

MSG_TYPE_CHANGE_LOG_LEVEL = "All.change_log_level"

class BaseModule:
    MESSAGE_HANDLERS_SWITCHER = None
    GroupName = "Afron/#"
    logger = None

    SEND_TO_ALL = "Afron/all"

    MSG_TYPE_CHANGE_LOG_LEVEL = "All.change_log_level"

    def __init__(self, name: str, version: str, topics=None):
        self.log = self.init_logger(name)
        self.MESSAGE_HANDLERS_SWITCHER = {}
        self.name = name
        if self.already_running():
            self.log.warning("Module already running. Exiting ...")
            sys.exit(-1)
        self._version = version
        self.MESSAGE_HANDLERS_SWITCHER = {}
        if sys.platform != 'win32':
            self.register_term()
        self.q = queue.Queue()
        self.client = MqttClient(self.name)
        self.run_thread = True
        self.thread = None
        self.client.subscribe(self.on_message, BaseModule.GroupName)
        self.stop_thread = False
        self.main_thread = threading.Thread(target=self.module_thread, daemon=True, name=self.name+"_main_thread")
        # Utilities.save_pid_to_file(name)

    def start(self):
        self.main_thread.start();

    def stop(self):
        self.stop_thread = True
        if self.main_thread is not None and self.main_thread.is_alive():
            self.main_thread.join(1)

    def module_thread(self):
        pass

    def change_log_level_callback(self, client: object, userdata: object, msg: Message):
        try:
            if msg.value not in debug_levels:
                self.log.error("Failed to change log level to level %d" % msg.value)
            self.set_log_level(msg.value)
        except Exception as e:
            self.log.error ("Failed to change log level to level ", str(e))

    def set_log_level(self, level:int) -> bool:
        if level not in debug_levels:
            self.log.error("Failed to change log level to level %d" % level)
            return False
        for h in self.log.handlers:
            if h.name == 'file':
                h.level = level
                return True
        return False

    @staticmethod
    def init_logger(name: str):
        log = logging.getLogger('')
        log.setLevel(logging.INFO)
        fh = logging.FileHandler('/home/pi/' + name + '.log')
        fh.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        ch.name = 'console'

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.name = 'file'

        # add the handlers to the logger
        log.addHandler(fh)
        log.addHandler(ch)
        return log

    def on_message(self, client: Client, userdata: object, message: MQTTMessage):
        # print("on_message:", message.topic)
        message_payload = Message().fromByteArray(message.payload)
        if message.topic == self.MSG_TYPE_CHANGE_LOG_LEVEL:
            self.change_log_level_callback(client, userdata, message_payload)
        else:
            message_handler = self.MESSAGE_HANDLERS_SWITCHER.get(message.topic)
            # self.log.debug(self.name + " got message from type: {}".format(message_payload.message_type))
            if message_handler is not None:
                message_handler(client, userdata, message_payload)
    
    def receive_signal(self, signalNumber, frame):
        self.log.info('Received: %d' % signalNumber)
        self.log.debug ('Received: %d' % signalNumber)
        if signalNumber == signal.SIGTERM:
            self.log.info ('signal.SIGTERM received, stopping...')
            self.stop()
        return

    def register_term(self):
        signal.signal(signal.SIGHUP, self.receive_signal)
        signal.signal(signal.SIGINT, self.receive_signal)
        signal.signal(signal.SIGQUIT, self.receive_signal)
        signal.signal(signal.SIGILL, self.receive_signal)
        signal.signal(signal.SIGTRAP, self.receive_signal)
        signal.signal(signal.SIGABRT, self.receive_signal)
        signal.signal(signal.SIGBUS, self.receive_signal)
        signal.signal(signal.SIGFPE, self.receive_signal)
        signal.signal(signal.SIGUSR1, self.receive_signal)
        signal.signal(signal.SIGSEGV, self.receive_signal)
        signal.signal(signal.SIGUSR2, self.receive_signal)
        signal.signal(signal.SIGPIPE, self.receive_signal)
        signal.signal(signal.SIGALRM, self.receive_signal)
        signal.signal(signal.SIGTERM, self.receive_signal)

    @property
    def version(self) -> str:
        return self._version

    def already_running(self):
        try:
            frame_info = inspect.stack()
            if len(frame_info) > 3:
                process_name = os.path.basename(frame_info[3].filename)
            else:
                process_name = os.path.basename(frame_info[2].filename)
            if os.name == 'nt':
                process_list = ["xxxx"]
            else:
                cmd = os.popen("ps -ef  | grep %s | grep -v grep | awk '{print $9}'" % process_name)
                process_list = cmd.read().split('\n')
            c = 0
            for proc in process_list:
                if process_name in proc:
                    c += 1
                    if c >= 2:
                        return True
        except:
            self.log.error("Failed in check if the module already running")
        return False


