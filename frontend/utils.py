# SJSU CMPE 138 SPRING 2026 TEAM6
import os, time

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

num_ticks = 2
num_cycles = 3
def print_load(msg: str | None, duration: float = 1):
    print('\033[?25l', end='')
    for x in range(num_cycles):
        if msg:
            print(f'\r{msg}\033[K', end='', flush=True)
        time.sleep(duration / (num_ticks * num_cycles))
        for y in range(num_ticks):
            print('.', end='', flush=True)
            time.sleep(duration / (num_ticks * num_cycles))
    print('\033[?25h')

def reconnect():
    from db_connector import db
    if not db.is_connected():
        db.reconnect()