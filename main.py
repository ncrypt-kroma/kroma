import pygame
from pygame.locals import *
from ctypes import windll, Structure, c_long, byref, wintypes
import sys
import ctypes


CF_UNICODETEXT = 13

user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

OpenClipboard = user32.OpenClipboard
OpenClipboard.argtypes = wintypes.HWND,
OpenClipboard.restype = wintypes.BOOL
CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL
EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL
GetClipboardData = user32.GetClipboardData
GetClipboardData.argtypes = wintypes.UINT,
GetClipboardData.restype = wintypes.HANDLE
SetClipboardData = user32.SetClipboardData
SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
SetClipboardData.restype = wintypes.HANDLE

GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = wintypes.HGLOBAL,
GlobalLock.restype = wintypes.LPVOID
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = wintypes.HGLOBAL,
GlobalUnlock.restype = wintypes.BOOL
GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
GlobalAlloc.restype = wintypes.HGLOBAL
GlobalSize = kernel32.GlobalSize
GlobalSize.argtypes = wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040


def put(s):
    data = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(data) + 2)
    pcontents = GlobalLock(handle)
    ctypes.memmove(pcontents, data, len(data))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


def colorToRGB(c):
    r = c & 255
    g = (c >> 8) & 255
    b = (c >> 16) & 255
    return r, g, b


pygame.init()
pygame.display.set_caption('KROMA')
fps_clock = pygame.time.Clock()
icon = pygame.image.load(r'KROMA_ASSETS\ICON.png')
pygame.display.set_icon(icon)
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
background = pygame.image.load(r"KROMA_ASSETS\backImage.png")
font = pygame.font.Font('KROMA_ASSETS\Gotham-Bold.otf', 21)
screen.blit(background, (0, 0))
background_color = old = (0, 0, 0)
rgb = (0, 0, 0)
lock = False
COUNTER = 0


class Node:
    def __init__(self, s, rbg, cords):
        self.s = s
        self.color = rbg
        self.cords = cords

    def display(self):
        screen.fill(self.color, (self.cords[0], self.cords[1], 32, 32))


grid = []
for x in range(5):
    for y in range(9):
        grid.append(Node(screen, (35, 35, 35), (406+(32*x)+(5*x), 58+(32*y)+(5*y))))


def text_objects(text, p1, p2):
    textSurface = font.render(text, True, (255, 255, 255))
    textSurface, textSurface.get_rect()
    TextSurf, TextRect = textSurface, textSurface.get_rect()
    TextRect.center = (p1, p2)
    screen.blit(TextSurf, TextRect)


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin
    if cmax == cmin:
        h = 0
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360
    if cmax == 0:
        s = 0
    else:
        s = (diff / cmax) * 100
    v = cmax * 100
    return int(h), int(s), int(v)


while True:
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    all_keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if all_keys[pygame.K_RSHIFT] or all_keys[pygame.K_LSHIFT] or all_keys[pygame.K_SPACE] or all_keys[pygame.K_KP_ENTER]:
        old = rgb
    if all_keys[pygame.K_RCTRL] or all_keys[pygame.K_r]:
        put(f"({old[0]}, {old[1]}, {old[2]})")
    if all_keys[pygame.K_RCTRL] or all_keys[pygame.K_c]:
        put('#%02x%02x%02x' % old)
    if all_keys[pygame.K_RCTRL] or all_keys[pygame.K_h]:
        put(f"({h}, {s}, {v})")

    for x in grid:
        x.display()
    screen.fill(old, (0, 0, 200, 400))
    screen.fill(background_color, (200, 0, 200, 400))
    screen.blit(background, (0, 0))
    x, y = queryMousePosition()
    hdc = windll.user32.GetDC(0)
    rgb = windll.gdi32.GetPixel(hdc, x, y)
    rgb = colorToRGB(rgb)
    background_color = rgb

    h, s, v = rgb_to_hsv(old[0], old[1], old[2])

    if click[0]:
        if 344 < mouse[1] < 382:
            print("ok")
            if 17 < mouse[0] < 135:
                put(f"({old[0]}, {old[1]}, {old[2]})")
            if 142 < mouse[0] < 260:
                put('#%02x%02x%02x' % old)
            if 265 < mouse[0] < 383:
                put(f"({h}, {s}, {v})")
        elif 13 < mouse[1] < 50:
            if 405 < mouse[0] < 472:
                grid[COUNTER].color = old
                COUNTER += 1
                if COUNTER == 45:
                    COUNTER = 0
        elif 55 < mouse[1] < 383:
            if 404 < mouse[0] < 583:
                old = rgb

    text_objects(str(old[0]), 157, 183)
    text_objects(str(old[1]), 249, 183)
    text_objects(str(old[2]), 340, 183)
    text_objects('#%02x%02x%02x' % old, 249, 243)
    text_objects(str(h) + "°", 157, 304)
    text_objects(str(s) + "%", 249, 304)
    text_objects(str(v) + "%", 340, 304)
    pygame.display.flip()

    fps_clock.tick(9)
