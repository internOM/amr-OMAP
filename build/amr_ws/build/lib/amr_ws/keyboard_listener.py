import threading
import sys
import termios
import tty

stop_flag = False

def keyboard_listener():
    global stop_flag
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch.lower() == 'x':
                stop_flag = True
                print("Stop key pressed!")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

thread = threading.Thread(target=keyboard_listener, daemon=True)
thread.start()

while not stop_flag:
    pass
print("Listener verified, exiting.")
