import customtkinter as ctk
from network_manager import BuzzerServer
from audio_manager import audio_manager
import threading
import socket

class HostGUI(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        
        # Base Game Show Colors
        self.bg_color = "#0B0B2A" # Deep Navy
        self.panel_color = "#16163A" # Lighter Navy/Purple
        self.accent_gold = "#FFD700" # Classic Gold
        self.accent_gold_hover = "#FFC000" # Bright Yellow/Gold
        self.configure(fg_color=self.bg_color)
        
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
        header_frame = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=0, border_width=0, border_color=self.accent_gold)
        header_frame.pack(fill="x", ipadx=10, ipady=10)
        
        # Adding a gold border line at the bottom of the header
        header_border = ctk.CTkFrame(self, fg_color=self.accent_gold, height=2, corner_radius=0)
        header_border.pack(fill="x")
        
        # Interior header content
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=5)
        
        back_btn = ctk.CTkButton(content_frame, text="← BACK", width=80, 
                                 command=self._on_back,
                                 fg_color="transparent", hover_color=self.bg_color,
                                 border_width=1, border_color=self.accent_gold,
                                 text_color=self.accent_gold, font=ctk.CTkFont(weight="bold"))
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(content_frame, text="HOST DASHBOARD", 
                                   font=ctk.CTkFont(family="Impact", size=28, weight="bold"),
                                   text_color=self.accent_gold)
        title_label.pack(side="left", padx=30)

        # Stats info
        self.stats_label = ctk.CTkLabel(content_frame, text="SESSION BUZZES: 0", 
                                        font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.stats_label.pack(side="right", padx=10)

        # Status
        status_label = ctk.CTkLabel(self, text=f"HOST IP: {self._get_local_ip()}   •   PORT: {self.server.port}", 
                                    font=ctk.CTkFont(size=14, weight="bold"), text_color="gray70")
        status_label.pack(pady=15)

        # First Buzzer Display
        self.first_buzzer_frame = ctk.CTkFrame(self, corner_radius=25, 
                                               fg_color=self.panel_color,
                                               border_width=3, border_color="gray30")
        self.first_buzzer_frame.pack(pady=(10, 20), padx=50, fill="x")
        
        self.first_buzzer_label = ctk.CTkLabel(self.first_buzzer_frame, text="WAITING FOR BUZZES...", 
                                               font=ctk.CTkFont(family="Impact", size=45, weight="bold"),
                                               text_color="gray50")
        self.first_buzzer_label.pack(pady=40)

        # List of buzzes area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="BUZZER SEQUENCE", 
                                                   label_font=ctk.CTkFont(size=14, weight="bold"),
                                                   label_text_color=self.accent_gold,
                                                   label_fg_color=self.panel_color,
                                                   fg_color=self.panel_color,
                                                   scrollbar_button_color=self.accent_gold,
                                                   border_width=2, border_color="gray30", corner_radius=15)
        self.scroll_frame.pack(pady=10, padx=50, fill="both", expand=True)

        # Bottom Button Frame
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=20, fill="x", padx=50)

        self.reset_btn = ctk.CTkButton(bottom_frame, text="RESET ALL / NEXT QUESTION", 
                                      fg_color="#A91B0D", hover_color="#D92110", # Deep red for warning/reset
                                      command=self._reset_buzzers,
                                      height=60, corner_radius=10,
                                      border_width=2, border_color="#FF4C4C",
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Initial stats update
        self._update_stats()

    def _update_stats(self):
        self.stats_label.configure(text=f"SESSION BUZZES: {len(self.buzzed_list)}")

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
            
            # Winner effect highlights
            display_color = color if color.lower() not in ["black", "darkgray"] else self.accent_gold
            
            self.first_buzzer_label.configure(text=f"WINNER: {name.upper()}", 
                                              text_color=display_color,
                                              font=ctk.CTkFont(family="Impact", size=55, weight="bold"))
            self.first_buzzer_frame.configure(border_color=display_color, border_width=5)
        
        # Add to list
        pos = len(self.buzzed_list)
        item_frame = ctk.CTkFrame(self.scroll_frame, fg_color=self.bg_color, corner_radius=8)
        item_frame.pack(fill="x", pady=4, padx=5)
        
        # Position badge
        pos_badge = ctk.CTkLabel(item_frame, text=f"#{pos}", 
                                 fg_color="gray20", text_color="white", 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 corner_radius=5, width=40, height=30)
        pos_badge.pack(side="left", padx=(5, 15), pady=5)

        # Player Name
        lbl_color = color if color.lower() not in ["black", "darkgray"] else "white"
        lbl = ctk.CTkLabel(item_frame, text=f"{name.upper()}", 
                           text_color=lbl_color, font=ctk.CTkFont(size=18, weight="bold"))
        lbl.pack(side="left")

    def _reset_buzzers(self):
        self.buzzed_list = []
        self.first_buzzed = False
        self.first_buzzer_label.configure(text="WAITING FOR BUZZES...", 
                                          text_color="gray50",
                                          font=ctk.CTkFont(family="Impact", size=45, weight="bold"))
        self.first_buzzer_frame.configure(border_color="gray30", border_width=3)
        
        self._update_stats()
        
        # Clear scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        self.server.broadcast_reset()

    def _on_back(self):
        self.server.stop()
        self.back_callback()
