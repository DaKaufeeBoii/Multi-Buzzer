import customtkinter as ctk
from network_manager import BuzzerClient
from audio_manager import audio_manager
import threading

class ParticipantGUI(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        
        # Base Game Show Colors
        self.bg_color = "#0B0B2A" # Deep Navy
        self.panel_color = "#16163A" # Lighter Navy/Purple
        self.accent_gold = "#FFD700" # Classic Gold
        self.accent_gold_hover = "#FFC000" # Bright Yellow/Gold
        self.configure(fg_color=self.bg_color)
        
        self.back_callback = back_callback
        self.client = None
        self.name = ""
        self.color = "Red"
        self.is_buzzed = False

        self._setup_join_screen()

    def _setup_join_screen(self):
        self.clear_frame()
        
        container = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=20, 
                                 border_width=2, border_color=self.accent_gold)
        container.pack(pady=50, padx=60, fill="both", expand=True)

        ctk.CTkLabel(container, text="PLAYER SIGN-IN", 
                     font=ctk.CTkFont(family="Impact", size=48, weight="bold"),
                     text_color=self.accent_gold).pack(pady=(40, 30))

        self.name_entry = ctk.CTkEntry(container, placeholder_text="ENTER YOUR NAME", 
                                       width=350, height=50, corner_radius=10,
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       border_color=self.accent_gold, border_width=1)
        self.name_entry.pack(pady=15)

        self.ip_entry = ctk.CTkEntry(container, placeholder_text="HOST IP ADDRESS", 
                                     width=350, height=50, corner_radius=10,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     border_color=self.accent_gold, border_width=1)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=15)

        ctk.CTkLabel(container, text="SELECT PODIUM COLOR", 
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=(20, 10))
        
        # Get dynamic colors from audio manager
        colors = audio_manager.get_available_colors()
        if not colors:
            colors = ["Red"]
            
        self.color_var = ctk.StringVar(value=colors[0])
        color_menu = ctk.CTkOptionMenu(container, values=colors, variable=self.color_var, 
                                       width=350, height=50, corner_radius=10,
                                       fg_color=self.bg_color, button_color=self.accent_gold, button_hover_color=self.accent_gold_hover,
                                       dropdown_fg_color=self.panel_color,
                                       font=ctk.CTkFont(size=16, weight="bold"))
        color_menu.pack(pady=5)

        self.join_btn = ctk.CTkButton(container, text="JOIN GAME", 
                                     command=self._join_server,
                                     width=350, height=60, corner_radius=10,
                                     fg_color=self.accent_gold, hover_color=self.accent_gold_hover,
                                     text_color=self.bg_color,
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.join_btn.pack(pady=40)
        
        back_btn = ctk.CTkButton(container, text="CANCEL", fg_color="transparent", 
                                 border_width=1, border_color=self.accent_gold, text_color=self.accent_gold,
                                 command=self.back_callback, font=ctk.CTkFont(weight="bold"))
        back_btn.pack(pady=10)

    def _join_server(self):
        name = self.name_entry.get().strip()
        host_ip = self.ip_entry.get().strip()
        
        if not name:
            return # Should show error
            
        self.client = BuzzerClient(host_ip)
        if self.client.connect():
            self.name = name
            self.color = self.color_var.get()
            self.client.on_reset_received = self._handle_reset
            self._setup_buzzer_screen()
        else:
            # Connection failed alert
            self.join_btn.configure(text="Connection Failed - Retry?")

    def _setup_buzzer_screen(self):
        self.clear_frame()
        
        # User Info Header
        info_frame = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=0, border_width=0)
        info_frame.pack(fill="x", ipadx=20, ipady=15)
        
        # Header bottom border
        header_border = ctk.CTkFrame(self, fg_color=self.color, height=4, corner_radius=0)
        header_border.pack(fill="x")
        
        player_label = ctk.CTkLabel(info_frame, text=f"PLAYER: {self.name.upper()}", 
                                    font=ctk.CTkFont(size=18, weight="bold"), 
                                    text_color="white")
        player_label.pack(side="left", padx=20)
        
        color_indicator = ctk.CTkFrame(info_frame, width=25, height=25, corner_radius=12, fg_color=self.color)
        color_indicator.pack(side="right", padx=(10, 20))
        ctk.CTkLabel(info_frame, text=f"TEAM {self.color.upper()}", 
                     font=ctk.CTkFont(size=16, weight="bold"), 
                     text_color="gray80").pack(side="right")

        # The Buzzer Button Area
        buzzer_container = ctk.CTkFrame(self, fg_color="transparent")
        buzzer_container.pack(expand=True, fill="both")

        self.buzzer_btn = ctk.CTkButton(buzzer_container, text="BUZZ", 
                                       command=self._buzz,
                                       fg_color=self.color,
                                       hover_color=self.color,
                                       width=350, height=350,
                                       corner_radius=175, # Make it perfectly round
                                       border_width=10, border_color="white", # Game show style rim
                                       font=ctk.CTkFont(family="Impact", size=60, weight="bold"))
        self.buzzer_btn.pack(pady=(40, 20))
        
        self.status_label = ctk.CTkLabel(buzzer_container, text="READY!", 
                                         font=ctk.CTkFont(family="Impact", size=32, weight="bold"),
                                         text_color="white")
        self.status_label.pack(pady=10)

        # Hint label
        ctk.CTkLabel(buzzer_container, text="TIP: PRESS THE SPACEBAR TO BUZZ IN", 
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="gray50").pack(pady=10)

        # Bind spacebar to buzz
        self.winfo_toplevel().bind("<space>", lambda e: self._buzz())

        # Leave Button
        leave_btn = ctk.CTkButton(buzzer_container, text="LEAVE GAME", 
                                 fg_color="transparent", border_width=1, border_color="gray50",
                                 text_color="gray70", hover_color=self.panel_color,
                                 command=self._on_back, font=ctk.CTkFont(weight="bold"))
        leave_btn.pack(side="bottom", pady=20)

    def _buzz(self):
        if not self.is_buzzed and self.client:
            self.is_buzzed = True
            self.client.send_buzz(self.name, self.color)
            audio_manager.play_sound(self.color)
            
            # Start animation
            self._animate_press()

    def _animate_press(self):
        """Creates a brief 'glow' effect before disabling."""
        self.buzzer_btn.configure(fg_color="white", text_color="black", border_color=self.accent_gold)
        
        def finalize():
            self.buzzer_btn.configure(state="disabled", fg_color="gray20", 
                                      text_color="gray50", border_color="gray40")
            
            # Using the specific color name handling similar to Host GUI
            display_color = self.color if self.color.lower() not in ["black", "darkgray"] else self.accent_gold
            self.status_label.configure(text="BUZZED IN!", text_color=display_color)
            
        self.after(100, finalize)

    def _handle_reset(self):
        self.after(0, self._ui_reset)

    def _ui_reset(self):
        self.is_buzzed = False
        self.buzzer_btn.configure(state="normal", fg_color=self.color, 
                                  text_color="white", border_color="white")
        self.status_label.configure(text="READY!", text_color="white")

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _on_back(self):
        # Remove spacebar binding when leaving
        try:
            self.winfo_toplevel().unbind("<space>")
        except Exception:
            pass
        if self.client:
            self.client.disconnect()
            self.client = None
        self.back_callback()
