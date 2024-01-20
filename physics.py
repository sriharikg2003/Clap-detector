# model.py
import pyaudio
import struct
import math
import time

INITIAL_TAP_THRESHOLD = 0.08
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = 1.0 / 32768.0
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)
OVERSENSITIVE = 15.0 / INPUT_BLOCK_TIME
UNDERSENSITIVE = 120.0 / INPUT_BLOCK_TIME
MAX_TAP_BLOCKS = 0.15 / INPUT_BLOCK_TIME

class TapTester:
    def __init__(self, socketio):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS + 1
        self.quietcount = 0
        self.errorcount = 0
        self.clap_detected = False
        self.timer_start_time = time.time()
        self.start_time = time.time()
        self.stream_closed = False
        self.socketio = socketio

    def stop(self):
        self.stream_closed = True
        self.stream.stop_stream()
        self.stream.close()

    def find_input_device(self):
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            print(f"Device {i}: {devinfo['name']}")

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    print(f"Found an input: device {i} - {devinfo['name']}")
                    return i

        print("No preferred input found; using default input device.")
        return None

    def open_mic_stream(self):
        device_index = self.find_input_device()

        return self.pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=INPUT_FRAMES_PER_BLOCK,
        )

    def tap_detected(self, time):
        elapsed_time = int(time - self.start_time)
        print(f"Tapped at time: {elapsed_time} seconds")

        if 4 <= elapsed_time < 5:
            print("WIN")
            self.stop()
            self.clap_detected = True
            self.socketio.emit('result', {'message': 'WIN'})
        else:
            print("LOSE")
            self.stop()
            self.clap_detected = True
            self.socketio.emit('result', {'message': 'LOSE'})

    def listen(self, time):
        if self.stream_closed:
            return

        self.display_timer(time)

        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except Exception as e:
            if "Stream closed" not in str(e):
                self.errorcount += 1
                print(f"({self.errorcount}) Error recording: {e}")
            self.noisycount = 1
            self.stop()
            return

        amplitude = self.get_rms(block)
        if amplitude > self.tap_threshold:
            self.quietcount = 0
            self.noisycount += 1
        else:
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tap_detected(time)
            self.noisycount = 0
            self.quietcount += 1

    def display_timer(self, current_time):
        timer_value = int(current_time - self.timer_start_time)
        print(f"Counter: {timer_value}\r", end="", flush=True)
        return timer_value

    def get_rms(self, block):
        count = len(block) // 2
        shorts = struct.unpack(f"{count}h", block)

        sum_squares = sum((sample * SHORT_NORMALIZE) ** 2 for sample in shorts)
        return math.sqrt(sum_squares / count)
