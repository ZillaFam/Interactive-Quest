"""Windows global-input adapter and console runner."""
import ctypes
from ctypes import wintypes
import queue
import sys
import threading
import time

from engine import Game


class GlobalInput:
    def __init__(self, events):
        self.events = events
        self.ready = threading.Event()
        self.error = None
        self.thread_id = None
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.thread.start()
        if not self.ready.wait(5):
            raise RuntimeError("Global input listener did not start")
        if self.error:
            raise RuntimeError(self.error)

    def stop(self):
        if self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)
            self.thread.join(timeout=2)

    def run(self):
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        hook_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, hook_type, wintypes.HINSTANCE, wintypes.DWORD]
        user32.SetWindowsHookExW.restype = wintypes.HANDLE
        user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallNextHookEx.restype = ctypes.c_ssize_t
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        self.thread_id = kernel32.GetCurrentThreadId()
        # Only event timestamps enter the game. Never inspect key codes or text.
        def keyboard(code, message, data):
            if code >= 0 and message in (0x0100, 0x0104):
                self.events.put(("input", time.monotonic()))
            return user32.CallNextHookEx(None, code, message, data)

        def mouse(code, message, data):
            if code >= 0 and message in (0x0201, 0x0204, 0x0207, 0x020B):
                self.events.put(("input", time.monotonic()))
            return user32.CallNextHookEx(None, code, message, data)

        callbacks = [hook_type(keyboard), hook_type(mouse)]
        hooks = []
        try:
            module = kernel32.GetModuleHandleW(None)
            for kind, callback in zip((13, 14), callbacks):
                hook = user32.SetWindowsHookExW(kind, callback, module, 0)
                if not hook:
                    raise ctypes.WinError(ctypes.get_last_error())
                hooks.append(hook)
            self.ready.set()
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        except Exception as exc:
            self.error = str(exc)
            self.ready.set()
        finally:
            for hook in hooks:
                user32.UnhookWindowsHookEx(hook)

