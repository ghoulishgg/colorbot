# original: https://github.com/Seconb/Arsenal-Colorbot

from cv2 import findContours, threshold, dilate, inRange, cvtColor, COLOR_BGR2HSV, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_NONE, contourArea
from numpy import array, ones, uint8
from os import path, system
from mss import mss
from keyboard import is_pressed
from configparser import ConfigParser
from win32api import GetAsyncKeyState
from colorama import Fore, Style
from ctypes import windll
from time import sleep, time
from threading import Thread
from urllib.request import urlopen
from webbrowser import open as openwebpage
from pygetwindow import getActiveWindow

len = len
print = print
tuple = tuple
int = int
bool = bool
max = max
sleep = sleep
str = str

user32 = windll.user32

maindir = path.dirname(__file__)

switchmodes = ("Hold", "Toggle")
resetall = Style.RESET_ALL

system("title Colorbot")

if urlopen("https://raw.githubusercontent.com/ghoulishgg/colorbot/main/version.txt").read().decode("utf-8") != "v2.0\n":
    print(Style.BRIGHT + Fore.CYAN + "This version is outdated, please get the latest one at " + Fore.YELLOW + "https://github.com/ghoulishgg/colorbot/releases" + resetall)
    openwebpage("https://github.com/ghoulishgg/colorbot/releases")
    while True:
        pass

def string_tokey(string, key):
    if string.lower() == "leftclick" or "vk_lbutton" in string.lower():
        return 0x01
    elif string.lower() == "rightclick" or "vk_rbutton" in string.lower():
        return 0x02
    elif string.lower() == "middleclick" or "vk_mbutton" in string.lower():
        return 0x04
    elif string.lower() == "sidebutton1" or "vk_xbutton1" in string.lower():
        return 0x05
    elif string.lower() == "sidebutton2" or "vk_xbutton2" in string.lower():
        return 0x06
    else:
        try:
            is_pressed(string)
        except:
            print(f"Please change {key} to an existing key.")
            while True:
                pass
        return string
    

def isgameactive():
    try:
        return getActiveWindow().title == "Roblox"
    except:
        return False
    
def key_tostring(key):
    if key == 0x01:
        return "LeftClick"
    elif key == 0x02:
        return "RightClick"
    elif key == 0x04:
        return "MiddleClick"
    elif key == 0x05:
        return "SideButton1"
    elif key == 0x06:
        return "SideButton2"
    else:
        return str(key)
    
def float_tostring(val): # copied from stackoverflow
    result = ("%.15f" % val).rstrip("0").rstrip(".")
    return "0" if result == "-0" else result

config = ConfigParser()
config.optionxform = str

pyinstaller = maindir # path.dirname(maindir) > maindir

if path.isfile(pyinstaller + "/config.txt"):
    config.read(pyinstaller + "/config.txt")
elif path.isfile(pyinstaller + "/config.ini"):
    config.read(pyinstaller + "/config.ini")
else:
    print("No config file found, please redownload colorbot!")
    while True:
        pass

AIM_KEY = string_tokey(config.get("Config", "AIM_KEY"), "AIM_KEY")
SWITCH_MODE_KEY = string_tokey(config.get("Config", "SWITCH_MODE_KEY"), "SWITCH_MODE_KEY")
AIM_FOV = int(config.get("Config", "AIM_FOV"))
CAM_FOV = 0
try:
    CAM_FOV = int(config.get("Config", "CAM_FOV"))
except:
    CAM_FOV = AIM_FOV + 5
TRIGGERBOT_DELAY = float(config.get("Config", "TRIGGERBOT_DELAY"))
AIM_SPEED_X = float(config.get("Config", "AIM_SPEED_X"))
AIM_SPEED_Y = float(config.get("Config", "AIM_SPEED_Y"))
AIM_OFFSET_Y = int(config.get("Config", "AIM_OFFSET_Y"))
AIM_OFFSET_X = int(config.get("Config", "AIM_OFFSET_X"))
COLOR = str(config.get("Config", "COLOR"))
UPPER_COLOR = tuple(map(int, config.get("Config", "UPPER_COLOR").split(", ")))
LOWER_COLOR = tuple(map(int, config.get("Config", "LOWER_COLOR").split(", ")))

if TRIGGERBOT_DELAY > 99999:
    TRIGGERBOT_DELAY = 99999

sct = mss()

sqrt_fov = AIM_FOV * AIM_FOV

screenshot = sct.monitors[1]
screenshot["left"] = int((screenshot["width"] * 0.5) - CAM_FOV * 0.5)
screenshot["top"] = int((screenshot["height"] * 0.5) - CAM_FOV * 0.5)
screenshot["width"] = CAM_FOV
screenshot["height"] = CAM_FOV

offset_x = CAM_FOV * 0.5 - AIM_OFFSET_X
offset_y = CAM_FOV * 0.5 - AIM_OFFSET_Y

ones3_uint = ones((3, 3), uint8)
sct_grab = sct.grab
mouse_event = user32.mouse_event

class colorbot:
    def __init__(self):
        self.aimtoggled = False
        self.switchmode = 0
        self.__clicks = 0
        self.__shooting = False
        if COLOR.lower() == "blue":
            self.colorname = Fore.BLUE
            self.__upper = array((123, 255, 217), dtype="uint8")
            self.__lower = array((113, 206, 189), dtype="uint8")
        elif COLOR.lower() == "pink" or COLOR.lower() == "magenta" or COLOR.lower() == "purple":
            self.colorname = Fore.MAGENTA
            self.__upper = array((150, 255, 201), dtype="uint8")
            self.__lower = array((150, 255, 200), dtype="uint8")
        elif COLOR.lower() == "green":
            self.colorname = Fore.GREEN
            self.__upper = array((60, 255, 201), dtype="uint8")
            self.__lower = array((60, 255, 201), dtype="uint8")
        elif COLOR.lower() == "cyan":
            self.colorname = Fore.CYAN
            self.__upper = array((90, 255, 201), dtype="uint8")
            self.__lower = array((90, 255, 201), dtype="uint8")
        elif COLOR.lower() == "yellow":
            self.colorname = Fore.YELLOW
            self.__upper = array((38, 255, 203), dtype="uint8")
            self.__lower = array((30, 255, 201), dtype="uint8")
        elif COLOR.lower() == "black":
            self.colorname = Fore.WHITE
            self.__upper = array((0, 0, 0), dtype="uint8")
            self.__lower = array((0, 0, 0), dtype="uint8")
        elif COLOR.lower() == "red":
            self.colorname = Fore.RED
            self.__upper = array((0, 255, 201), dtype="uint8")
            self.__lower = array((0, 255, 201), dtype="uint8")
        elif COLOR.lower() == "0000ff" or COLOR.lower() == "badbusiness":
            self.colorname = Fore.BLUE
            self.__upper = array((123, 255, 255), dtype="uint8")
            self.__lower = array((120, 147, 69), dtype="uint8")
        elif COLOR.lower() == "aimblox":
            self.colorname = Fore.LIGHTRED_EX
            self.__upper = array((4, 225, 206), dtype="uint8")
            self.__lower = array((0, 175, 119), dtype="uint8")
        elif COLOR.lower() == "custom":
            self.colorname = Fore.WHITE
            self.__upper = array(UPPER_COLOR, dtype="uint8")
            self.__lower = array(LOWER_COLOR, dtype="uint8")
        else:
            print("The color is incorrect please set it one of these, Yellow, Pink/Purple, Blue, Green, Cyan, 0000ff, Aimblox or Custom")
            while True:
                pass

    def __stop(self):
        oldclicks = self.__clicks
        sleep(.05)
        if self.__clicks == oldclicks:
            mouse_event(0x0004)

    def __delayedaim(self):
        self.__shooting = True
        sleep(TRIGGERBOT_DELAY)
        mouse_event(0x0002)
        self.__clicks += 1
        Thread(target = self.__stop).start()
        self.__shooting = False

    def process(self):
        if isgameactive():
            contours, hierarchy = findContours(threshold(dilate(inRange(cvtColor(array(sct_grab(screenshot)), COLOR_BGR2HSV), self.__lower, self.__upper), ones3_uint, iterations=5), 60, 255, THRESH_BINARY)[1], RETR_EXTERNAL, CHAIN_APPROX_NONE)
            if len(contours) != 0:
                contour = max(contours, key=contourArea)
                topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                x = topmost[0] - offset_x
                y = topmost[1] - offset_y
                distance = x*x + y*y
                if distance <= sqrt_fov and distance >= 1:
                    mouse_event(0x0001, int(x * AIM_SPEED_X), int(y * AIM_SPEED_Y), 0, 0)
                if distance <= 100:
                    if TRIGGERBOT_DELAY != 0:
                        if self.__shooting == False:
                            Thread(target = self.__delayedaim).start()
                    else:
                        mouse_event(0x0002)
                        self.__clicks += 1
                        Thread(target = self.__stop).start()

    def aimtoggle(self):
        self.aimtoggled = not self.aimtoggled

    def modeswitch(self):
        if self.switchmode == 0:
            self.switchmode = 1
        elif self.switchmode == 1:
            self.switchmode = 0

def print_banner(bot):
    system("cls")
    print(Style.BRIGHT + Fore.CYAN + "colorbot for Arsenal!" + Fore.RED + " Credits to @etheralaimer" + resetall)
    print(Style.BRIGHT + Fore.GREEN + "Join our discord server for updates and configs https://discord.gg/APmRJGRu9f" + resetall)
    print(Style.BRIGHT + Fore.MAGENTA + "Make sure you fullscreen your Roblox window and are in the web version!" + resetall)
    print(Style.BRIGHT + Fore.YELLOW + "====== Controls ======" + resetall)
    print("Aimbot Keybind       :", Fore.YELLOW + key_tostring(AIM_KEY) + resetall)
    print("Change Mode          :", Fore.YELLOW + key_tostring(SWITCH_MODE_KEY) + resetall)
    print(Style.BRIGHT + Fore.YELLOW + "==== Information =====" + resetall)
    print("Aimbot Mode          :", Fore.CYAN + switchmodes[bot.switchmode] + resetall)
    print("Aimbot FOV           :", Fore.CYAN + str(AIM_FOV) + resetall)
    print("Camera FOV           :", Fore.CYAN + str(CAM_FOV) + Style.RESET_ALL)
    print("Triggerbot Delay     :", Fore.CYAN + float_tostring(TRIGGERBOT_DELAY) + resetall)
    print("Sensitivity          :", Fore.CYAN + "X: " + float_tostring(AIM_SPEED_X) + " Y: " + float_tostring(AIM_SPEED_Y) + resetall)
    print("Aim Offsets          :", Fore.CYAN + "X: " + str(AIM_OFFSET_X) + " Y: " + str(AIM_OFFSET_Y) + resetall)
    if bot.aimtoggled:
        print("Currently Aiming     :", Fore.GREEN + "Yes" + resetall)
    else:
        print("Currently Aiming     :", Fore.RED + "No" + resetall)
    if COLOR.lower() == "custom":
        print("Upper Color          :", Fore.CYAN + str(bot.colorname + str(UPPER_COLOR)) + resetall)
        print("Lower Color          :", Fore.CYAN + str(bot.colorname + str(LOWER_COLOR)))
    else:
        print("Enemy Color          :", Fore.CYAN + str(bot.colorname + COLOR))
    sleep(0.3)

try:
    with open(maindir + "/lastlaunch.txt", "r+") as buffer:
        currenttime = time()
        if currenttime - float(buffer.read()) >= 17990:
            openwebpage("https://discord.gg/APmRJGRu9")
            buffer.write(str(currenttime))
except:
    openwebpage("https://discord.gg/APmRJGRu9")
    with open(maindir + "/lastlaunch.txt", "w+") as buffer:
        buffer.write(str(time()))

if __name__ == "__main__":
    bot = colorbot()
    del colorbot
    del urlopen
    del mss
    del openwebpage
    del ConfigParser
    del string_tokey
    del maindir
    print_banner(bot)
    while True:
        if SWITCH_MODE_KEY == 0x01 or SWITCH_MODE_KEY == 0x02 or SWITCH_MODE_KEY == 0x04:
            if GetAsyncKeyState(SWITCH_MODE_KEY) < 0:
                bot.modeswitch()
                print_banner(bot)
        elif SWITCH_MODE_KEY == 0x05 or SWITCH_MODE_KEY == 0x06:
            if bool(user32.GetKeyState(SWITCH_MODE_KEY) & 0x80):
                bot.modeswitch()
                print_banner(bot)
        elif is_pressed(SWITCH_MODE_KEY):
            bot.modeswitch()
            print_banner(bot)

        sleep(0.1)

        if AIM_KEY == 0x01 or AIM_KEY == 0x02 or AIM_KEY == 0x04:
            if GetAsyncKeyState(AIM_KEY) < 0:
                if bot.switchmode == 0:
                    while GetAsyncKeyState(AIM_KEY) < 0:
                        if not bot.aimtoggled:
                            bot.aimtoggle()
                            print_banner(bot)
                            while bot.aimtoggled: 
                                bot.process()
                                if not GetAsyncKeyState(AIM_KEY) < 0:
                                    bot.aimtoggle()
                                    print_banner(bot)
                else:
                    bot.aimtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if GetAsyncKeyState(AIM_KEY) < 0:
                            bot.aimtoggle()
                            print_banner(bot)
        elif AIM_KEY == 0x05 or AIM_KEY == 0x06:
            if bool(user32.GetKeyState(AIM_KEY) & 0x80):
                if bot.switchmode == 0:
                    while bool(user32.GetKeyState(AIM_KEY) & 0x80):
                        if not bot.aimtoggled:
                            bot.aimtoggle()
                            print_banner(bot)
                            while bot.aimtoggled: 
                                bot.process()
                                if not bool(user32.GetKeyState(AIM_KEY) & 0x80):
                                    bot.aimtoggle()
                                    print_banner(bot)
                else:
                    bot.aimtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if bool(user32.GetKeyState(AIM_KEY) & 0x80):
                            bot.aimtoggle()
                            print_banner(bot)
        elif is_pressed(AIM_KEY):
            if bot.switchmode == 0:
                while is_pressed(AIM_KEY):
                    if not bot.aimtoggled:
                        bot.aimtoggle()
                        print_banner(bot)
                        while bot.aimtoggled:
                            bot.process()
                            if not is_pressed(AIM_KEY):
                                bot.aimtoggle()
                                print_banner(bot)
            else: 
                bot.aimtoggle()
                print_banner(bot)
                while bot.aimtoggled:
                    bot.process()
                    if is_pressed(AIM_KEY):
                        bot.aimtoggle()
                        print_banner(bot)
