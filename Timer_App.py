import tkinter as tk
from tkinter import messagebox
import time
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
import pygame
import sys
# Windowsの場合のみwinsoundをインポート
if sys.platform == "win32":
    import winsound
class UltimateTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Ultimate Clock App")
        self.root.geometry("550x750")
        
        # スタイルと音楽の初期化
        self.style = tb.Style(theme="darkly")
        pygame.mixer.init()

        # 変数管理
        self.sw_running = False
        self.sw_start_time = 0
        self.sw_elapsed = 0
        self.alarms = []
        
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_total = 0

        # --- メインレイアウト ---
        self.notebook = tb.Notebook(root, bootstyle="info")
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.tab_clock = tb.Frame(self.notebook, padding=20)
        self.tab_stopwatch = tb.Frame(self.notebook, padding=20)
        self.tab_timer = tb.Frame(self.notebook, padding=20)
        
        self.notebook.add(self.tab_clock, text="  ALARM  ")
        self.notebook.add(self.tab_stopwatch, text="  STOPWATCH  ")
        self.notebook.add(self.tab_timer, text="  TIMER  ")

        self.setup_clock_tab()
        self.setup_stopwatch_tab()
        self.setup_timer_tab()

        self.update_all()

    # --- タイマー画面 (NEW) ---
    def setup_timer_tab(self):
        # 円形メーター
        self.timer_meter = Meter(
            self.tab_timer, metersize=250, padding=20, amounttotal=100,
            amountused=0, metertype="full", subtext="seconds left",
            interactive=False, bootstyle="warning", textfont="-size 30 -weight bold"
        )
        self.timer_meter.pack()

        # 入力エリア
        input_frame = tb.Frame(self.tab_timer)
        input_frame.pack(pady=20)

        tb.Label(input_frame, text="Set Seconds:").pack(side=LEFT, padx=5)
        self.timer_input = tb.Spinbox(input_frame, from_=0, to=3600, width=10)
        self.timer_input.set(60)
        self.timer_input.pack(side=LEFT, padx=5)

        # 操作ボタン
        btn_frame = tb.Frame(self.tab_timer)
        btn_frame.pack(pady=10)

        self.t_start_btn = tb.Button(btn_frame, text="START TIMER", bootstyle="warning", command=self.start_timer, width=15)
        self.t_start_btn.grid(row=0, column=0, padx=5)

        tb.Button(btn_frame, text="RESET", bootstyle="secondary-outline", command=self.reset_timer).grid(row=0, column=1, padx=5)

    # --- 時計 & アラーム ---
    def setup_clock_tab(self):
        self.clock_label = tb.Label(self.tab_clock, text="00:00:00", font=("Helvetica", 50, "bold"), bootstyle="primary")
        self.clock_label.pack(pady=30)

        input_frame = tb.Labelframe(self.tab_clock, text=" Add Alarm ", padding=15)
        input_frame.pack(fill=X)

        self.hour_val = tb.Spinbox(input_frame, from_=0, to=23, width=5, format="%02.0f")
        self.hour_val.set(time.strftime("%H")); self.hour_val.pack(side=LEFT, padx=5)
        self.min_val = tb.Spinbox(input_frame, from_=0, to=59, width=5, format="%02.0f")
        self.min_val.set(time.strftime("%M")); self.min_val.pack(side=LEFT, padx=5)

        tb.Button(input_frame, text="+", bootstyle="info", command=self.add_alarm).pack(side=LEFT, padx=10)

        self.alarm_listbox = tk.Listbox(self.tab_clock, font=("Consolas", 12), bg="#2b2b2b", fg="white", height=8)
        self.alarm_listbox.pack(fill=BOTH, expand=True, pady=10)
        tb.Button(self.tab_clock, text="DELETE", bootstyle="danger-outline", command=self.remove_alarm).pack(fill=X)

    # --- ストップウォッチ ---
    def setup_stopwatch_tab(self):
        self.sw_label = tb.Label(self.tab_stopwatch, text="00:00:00", font=("Helvetica", 45, "bold"), bootstyle="success")
        self.sw_label.pack(pady=30)
        
        f = tb.Frame(self.tab_stopwatch)
        f.pack()
        self.sw_btn = tb.Button(f, text="START", bootstyle="success", command=self.start_stop_sw, width=10)
        self.sw_btn.grid(row=0, column=0, padx=5)
        tb.Button(f, text="RESET", bootstyle="danger-outline", command=self.reset_sw, width=10).grid(row=0, column=1, padx=5)

    # --- ロジック ---
    def update_all(self):
        # 1. 現在時刻 & アラーム
        now_struct = time.localtime()
        self.clock_label.config(text=time.strftime("%H:%M:%S", now_struct))
        current_hm = time.strftime("%H:%M", now_struct)
        if current_hm in self.alarms:
            self.trigger_alert(f"Alarm ({current_hm})")
            self.remove_alarm_by_val(current_hm)

        # 2. ストップウォッチ
        if self.sw_running:
            diff = self.sw_elapsed + (time.time() - self.sw_start_time)
            self.sw_label.config(text=self.format_time(diff))

        # 3. タイマー (NEW)
        if self.timer_running:
            now = time.time()
            self.timer_remaining = max(0, self.timer_total - (now - self.timer_start_time))
            self.timer_meter.configure(amountused=int(self.timer_remaining))
            
            if self.timer_remaining <= 0:
                self.timer_running = False
                self.trigger_alert("Timer Finished!")
                self.t_start_btn.config(state=NORMAL)

        self.root.after(100, self.update_all)

    def format_time(self, t):
        m, s = divmod(t, 60)
        return f"{int(m):02}:{int(s):02}:{int((t%1)*100):02}"

    def trigger_alert(self, msg):
        try: winsound.Beep(1000, 500) # Windows標準
        except: pass 
        messagebox.showinfo("Notification", msg)

    # --- タイマー操作 ---
    def start_timer(self):
        try:
            seconds = int(self.timer_input.get())
            if seconds > 0:
                self.timer_total = seconds
                self.timer_remaining = seconds
                self.timer_start_time = time.time()
                self.timer_running = True
                self.timer_meter.configure(amounttotal=seconds, amountused=seconds)
                self.t_start_btn.config(state=DISABLED)
        except: pass

    def reset_timer(self):
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_meter.configure(amountused=0)
        self.t_start_btn.config(state=NORMAL)

    # --- その他操作 (略) ---
    def add_alarm(self):
        t = f"{int(self.hour_val.get()):02}:{int(self.min_val.get()):02}"
        if t not in self.alarms:
            self.alarms.append(t); self.alarm_listbox.insert(tk.END, f" 🔔 {t}")

    def remove_alarm(self):
        s = self.alarm_listbox.curselection()
        if s: self.alarms.pop(s[0]); self.alarm_listbox.delete(s[0])

    def remove_alarm_by_val(self, val):
        if val in self.alarms:
            idx = self.alarms.index(val)
            self.alarms.pop(idx); self.alarm_listbox.delete(idx)

    def start_stop_sw(self):
        if not self.sw_running:
            self.sw_running = True; self.sw_start_time = time.time()
            self.sw_btn.config(text="STOP", bootstyle="danger")
        else:
            self.sw_running = False; self.sw_elapsed += time.time() - self.sw_start_time
            self.sw_btn.config(text="START", bootstyle="success")

    def reset_sw(self):
        self.sw_running = False; self.sw_elapsed = 0
        self.sw_label.config(text="00:00:00"); self.sw_btn.config(text="START", bootstyle="success")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = UltimateTimerApp(root)
    root.mainloop()
