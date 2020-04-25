import argparse
from memorpy import *
from ctypes import *
from ctypes.wintypes import *
from memorpy.WinStructures import PAGE_READWRITE
import win32gui
import win32process
import win32api
import win32con

def sendenter(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    #win32api.SendMessage(hwndChild, win32con.WM_CHAR, 0x28, 0)

def sendstring(strtosend, hwnd, enter):
    for char in strtosend:
        win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
    if enter:
        sendenter(hwnd)


parser = argparse.ArgumentParser()
parser.add_argument("--pid")
parser.add_argument("--name")
args = parser.parse_args()
mem = None
if args.pid is None:
    mem=MemWorker(pid=int(raw_input("What is the process ID?").strip())) #you can also select a process by its name with the kwarg name=
else:
    mem=MemWorker(pid=int(args.pid.strip())) 

modules = mem.process.list_modules()

def aob_scan(mem, start, size, pattern=None, offset=0, entity_check=False):
    all_the_bytes = mem.process.read(mem.Address(start), type='bytes', maxlen=size)
    matches = re.finditer(pattern, all_the_bytes)
    results = []
    for match in matches:
        span = match.span()
        if span:
            address = start + span[0] + offset
            addressval = mem.Address(address).read(type='string', errors='ignore')
            results.append(addressval)
            mem.Address(address).write('Please type the following sequence:\nXXX', type='bytes')
    return results


previous_answer = ''

mods = modules["shadowrealm.exe"]
windowname = 'Shadow Realm '
if args.name is None:
    windowname = 'Shadow Realm - {}'.format(raw_input('What is your character name?').strip())
else:
    windowname = 'Shadow Realm - {}'.format(args.name.strip())
game_hwnd = win32gui.FindWindow(None, windowname)
print(game_hwnd)
def checkforchallenge():
    previous_answer = ''
    while True:
        time.sleep(0.2)
        regions = mem.process.iter_region(start_offset=mods, protec=PAGE_READWRITE)
        challengemessage = ''
        for start, size in regions:
            res = aob_scan(mem, start, size, pattern='Please type the following sequence:\n\w\w\w', offset=0)
            if res is not None:
                challengemessage += ''.join(res)

        if challengemessage is None or challengemessage is '':
            continue
        
        newlines = challengemessage.splitlines()
        for i in range(len(newlines)):
            line = newlines[i]
            if "Please type the following sequence:" in line:
                line = line.replace("Please type the following sequence:", "")
            if previous_answer == line or line == 'XXX' or line is None:
                continue
            try:
                previous_answer = line
                print("Line: " + line)
                sendstring(line, game_hwnd, True)
                break
            except:
                print('Exception in check for challenge')

checkforchallenge()