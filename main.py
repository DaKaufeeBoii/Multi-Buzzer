import customtkinter as ctk
import sys
import socket
import webbrowser
from host_gui import HostGUI
from participant_gui import ParticipantGUI

class BuzzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Multi-Buzzer")
        self.geometry("900x650")
        
        # Base Game Show Colors
        self.bg_color = "#0B0B2A" # Deep Navy
        self.panel_color = "#16163A" # Lighter Navy/Purple
        self.accent_gold = "#FFD700" # Classic Gold
        self.accent_gold_hover = "#FFC000" # Bright Yellow/Gold
        
        self.configure(fg_color=self.bg_color)

        self.current_frame = None
        self.show_home_menu()

    def show_home_menu(self):
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=self.panel_color, 
                                          border_width=2, border_color=self.accent_gold)
        self.current_frame.pack(pady=60, padx=60, fill="both", expand=True)

        # Main Title (Glowing/Gold look)
        title_label = ctk.CTkLabel(self.current_frame, text="Multi-Buzzer", 
                                   font=ctk.CTkFont(family="Impact", size=60, weight="bold"), 
                                   text_color=self.accent_gold)
        title_label.pack(pady=(40, 10))

        subtitle_label = ctk.CTkLabel(self.current_frame, text="THE ULTIMATE GAME SHOW EXPERIENCE", 
                                      font=ctk.CTkFont(size=18, weight="bold"), 
                                      text_color="white")
        subtitle_label.pack(pady=(0, 30))

        button_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        button_frame.pack(pady=40)

        host_button = ctk.CTkButton(button_frame, text="JOIN AS HOST", 
                                   command=self.join_as_host,
                                   width=250, height=60,
                                   fg_color=self.bg_color,
                                   hover_color=self.panel_color,
                                   border_width=2, border_color=self.accent_gold,
                                   text_color=self.accent_gold,
                                   font=ctk.CTkFont(size=20, weight="bold"))
        host_button.pack(side="left", padx=20)

        participant_button = ctk.CTkButton(button_frame, text="JOIN AS PARTICIPANT", 
                                          command=self.join_as_participant,
                                          width=250, height=60,
                                          fg_color=self.accent_gold,
                                          hover_color=self.accent_gold_hover,
                                          text_color=self.bg_color,
                                          font=ctk.CTkFont(size=20, weight="bold"))
        participant_button.pack(side="left", padx=20)

        # Volume Control
        volume_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        volume_frame.pack(pady=20)
        
        ctk.CTkLabel(volume_frame, text="GLOBAL VOLUME", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack()
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=1, 
                                          button_color=self.accent_gold, button_hover_color=self.accent_gold_hover,
                                          progress_color=self.accent_gold,
                                          command=self._update_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(pady=5)

        credits_button = ctk.CTkButton(self.current_frame, text="CREDITS", 
                                       command=self.show_credits,
                                       width=100, height=30,
                                       fg_color="transparent",
                                       hover_color=self.panel_color,
                                       border_width=1, border_color=self.accent_gold,
                                       text_color=self.accent_gold,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        credits_button.pack(side="bottom", pady=(0, 20))

        info_label = ctk.CTkLabel(self.current_frame, text=f"HOST IP: {self.get_local_ip()}", 
                                  font=ctk.CTkFont(size=14, weight="bold"), 
                                  text_color="gray60")
        info_label.pack(side="bottom", pady=(20, 10))

    def show_credits(self):
        credits_window = ctk.CTkToplevel(self)
        credits_window.title("Credits")
        credits_window.geometry("400x350")
        credits_window.configure(fg_color=self.bg_color)
        credits_window.attributes("-topmost", True)
        
        # Center the window relative to main app
        credits_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (350 // 2)
        credits_window.geometry(f"+{x}+{y}")
        
        title = ctk.CTkLabel(credits_window, text="CREDITS", 
                             font=ctk.CTkFont(family="Impact", size=30, weight="bold"), 
                             text_color=self.accent_gold)
        title.pack(pady=(30, 20))

        plug1 = ctk.CTkLabel(credits_window, text="Created by: DaKaufeeBoii", 
                             font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        plug1.pack(pady=(5, 10))
        
        plug2 = ctk.CTkLabel(credits_window, text="Instagram", 
                             font=ctk.CTkFont(size=16, underline=True), text_color="#4DA6FF", cursor="hand2")
        plug2.pack(pady=5)
        plug2.bind("<Button-1>", lambda e: webbrowser.open_new("https://instagram.com/4002_saitarun"))

        plug3 = ctk.CTkLabel(credits_window, text="GitHub", 
                             font=ctk.CTkFont(size=16, underline=True), text_color="#4DA6FF", cursor="hand2")
        plug3.pack(pady=5)
        plug3.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/DaKaufeeBoii"))
        
        plug4 = ctk.CTkLabel(credits_window, text="LinkedIn", 
                             font=ctk.CTkFont(size=16, underline=True), text_color="#4DA6FF", cursor="hand2")
        plug4.pack(pady=5)
        plug4.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.linkedin.com/in/sai-tarun-reddy-velagala-24135229b/"))
        
        close_btn = ctk.CTkButton(credits_window, text="CLOSE", 
                                  command=credits_window.destroy,
                                  width=120, height=35,
                                  fg_color=self.bg_color,
                                  hover_color=self.panel_color,
                                  border_width=2, border_color=self.accent_gold,
                                  text_color=self.accent_gold,
                                  font=ctk.CTkFont(size=14, weight="bold"))
        close_btn.pack(pady=(30, 10))

    def _update_volume(self, value):
        from audio_manager import audio_manager
        audio_manager.set_volume(value)

    def join_as_host(self):
        self.clear_frame()
        self.current_frame = HostGUI(self, self.show_home_menu)
        self.current_frame.pack(fill="both", expand=True)

    def join_as_participant(self):
        self.clear_frame()
        self.current_frame = ParticipantGUI(self, self.show_home_menu)
        self.current_frame.pack(fill="both", expand=True)

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

if __name__ == "__main__":
    app = BuzzerApp()
    app.mainloop()
