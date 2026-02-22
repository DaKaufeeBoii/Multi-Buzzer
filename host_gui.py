import customtkinter as ctk
from network_manager import BuzzerServer
from audio_manager import audio_manager
import threading
import socket

class HostGUI(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        self.back_callback = back_callback
        self.server = BuzzerServer()
        self.buzzed_list = []
        self.first_buzzed = False

        self._setup_ui()
        self.server.on_buzz_received = self._handle_buzz
        
        if not self.server.start():
            self.first_buzzer_label.configure(text="Error: Port 12345 in use", text_color="red")
            self.reset_btn.configure(state="disabled")

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        back_btn = ctk.CTkButton(header_frame, text="← Back", width=80, command=self._on_back)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="Host Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left", padx=20)

        # Stats info
        self.stats_label = ctk.CTkLabel(header_frame, text="Session Buzzes: 0", font=ctk.CTkFont(size=12))
        self.stats_label.pack(side="right", padx=10)

        # Status
        status_label = ctk.CTkLabel(self, text=f"IP: {self._get_local_ip()} | Port: {self.server.port}", font=ctk.CTkFont(size=14))
        status_label.pack(pady=5)

        # First Buzzer Display
        self.first_buzzer_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="gray")
        self.first_buzzer_frame.pack(pady=20, padx=40, fill="x")
        
        self.first_buzzer_label = ctk.CTkLabel(self.first_buzzer_frame, text="Waiting for buzzes...", font=ctk.CTkFont(size=30, weight="bold"))
        self.first_buzzer_label.pack(pady=30)

        # List of buzzes area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Buzzer Sequence", label_font=ctk.CTkFont(weight="bold"))
        self.scroll_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # Bottom Button Frame
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=20, fill="x", padx=40)

        self.reset_btn = ctk.CTkButton(bottom_frame, text="RESET ALL", 
                                      fg_color="#e74c3c", hover_color="#c0392b",
                                      command=self._reset_buzzers,
                                      height=50,
                                      font=ctk.CTkFont(size=18, weight="bold"))
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Initial stats update
        self._update_stats()

    def _update_stats(self):
        self.stats_label.configure(text=f"Session Buzzes: {len(self.buzzed_list)}")

    def _handle_buzz(self, name, color):
        # We need to make sure UI updates are on the main thread
        self.after(0, lambda: self._update_ui_with_buzz(name, color))

    def _update_ui_with_buzz(self, name, color):
        if any(b['name'] == name for b in self.buzzed_list):
            return # Already buzzed

        self.buzzed_list.append({"name": name, "color": color})
        
        # Play unique sound for the person who buzzed
        audio_manager.play_sound(color)

        if not self.first_buzzed:
            self.first_buzzed = True
            self.first_buzzer_label.configure(text=f"WINNER: {name}", text_color=color)
            self.first_buzzer_frame.configure(border_color=color)
        
        # Add to list
        pos = len(self.buzzed_list)
        item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)
        
        lbl = ctk.CTkLabel(item_frame, text=f"{pos}. {name}", text_color=color, font=ctk.CTkFont(size=16))
        lbl.pack(side="left", padx=10)

    def _reset_buzzers(self):
        self.buzzed_list = []
        self.first_buzzed = False
        self.first_buzzer_label.configure(text="Waiting for buzzes...", text_color="white")
        self.first_buzzer_frame.configure(border_color="gray")
        
        # Clear scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        self.server.broadcast_reset()

    def _on_back(self):
        self.server.stop()
        self.back_callback()
