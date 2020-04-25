import argparse
from memorpy import *
from ctypes import *
from ctypes.wintypes import *
from memorpy.WinStructures import PAGE_READWRITE
import win32ui
import win32gui
import sys
import win32process
import numpy as np
import ast
import operator as op
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

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

allowed = string.digits
def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))


def eval_expr(expr):
    try:
        #filtered = list(filter(allowed.__contains__, expr))
        #filtered = ''.join(filtered)
        return str(eval_(ast.parse(expr, mode='eval').body))
    except:
        return ''
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

#print(mem.Address(modules["shadowrealm.exe"]).read())


def aob_scan(mem, start, size, pattern=None, offset=0, entity_check=False):
    all_the_bytes = mem.process.read(mem.Address(start), type='bytes', maxlen=size)
    matches = re.finditer(pattern, all_the_bytes)
    #print(all_the_bytes)
    results = []
    found = False
    for match in matches:
        span = match.span()
        if span:
            address = start + span[0] + offset
            addressval = mem.Address(address).read(type='string', errors='ignore')
            #print(addressval)
            if "= ?" in addressval:
                if not found:
                    found = True
                    results.append(addressval)
                mem.Address(address).write('X  -  X = ?answer the following question:', type='bytes')
    return results


previous_message = ''
#windowname = 'Shadow Realm - ' + raw_input('What is your character name?')
#windowname = "Shadow Realm - " + raw_input('What is your character name?')
#print(windowname)
#game_hwnd = win32gui.FindWindow(None, windowname)



mods = modules["shadowrealm.exe"]
windowname = 'Shadow Realm '
if args.name is None:
    windowname = 'Shadow Realm - {}'.format(raw_input('What is your character name?').strip())
else:
    windowname = 'Shadow Realm - {}'.format(args.name.strip())
game_hwnd = win32gui.FindWindow(None, windowname)
print(game_hwnd)
def checkforchallenge():
    while True:
        time.sleep(0.2)
        regions = mem.process.iter_region(start_offset=mods, protec=PAGE_READWRITE)
        challengemessage = ''
        for start, size in regions:
            res = aob_scan(mem, start, size, pattern='answer the following', offset=0)
            if res is not None:
                challengemessage += ''.join(res)

        if challengemessage is None or challengemessage is '':
            continue
        print(challengemessage + "\n")
        challengemessage = challengemessage.lower()
        challengemessage = challengemessage.replace(" ", "")
        #challengekeywords = ['=?']
        
        #if not seconds_passed(newnaswerepoch, 5) or challengemessage == previous_message:
            #continue
        #print(challengemessage)
        previous_message = challengemessage
        newlines = challengemessage.splitlines()
        answer = ""
        #print(previous_message)
        for line in newlines:
            if "=?" not in line:
                continue
            #previous_line = line
            parsed = line
            #parsed = parsed.replace("S", "5")
            #parsed = parsed.replace("s", "5")
            #parsed = parsed.replace("g", "6")
            try:
                regexres = ''
                regexres = re.search(r'\d{0,2}.\-\d{0,2}|\d{0,2}\+\d{0,2}|\d{0,2}\*\d{0,2}|\d{0,2}\/\d{0,2}', parsed).group() or ''
                regexres = regexres.replace("=?", "")
                answer = eval_expr(regexres)
                sendstring(answer, game_hwnd, True)
                print("Final question: " + regexres)
                print("Final answer: " + answer)
                break
            except:
                print('Exception in check for challenge when doing regex')

checkforchallenge()
#finalresults = []
#for start, size in regions:
    #res = aob_scan(mem, start, size, pattern='Please answer the following question', offset=0)
    #if res not None:
        #finalresults.append(res)
#print(json.dumps(finalresults))
#regions = mem.process.iter_region(start_offset=modules["shadowrealm.exe"], protec=PAGE_READWRITE)


#l=[x for x in mem.umem_search("An orb has spawned use the ")]
#for i in l:
    #print(i.read())
