import customtkinter as ctk
from network_manager import BuzzerClient
from audio_manager import audio_manager
import threading

class ParticipantGUI(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        self.back_callback = back_callback
        self.client = None
        self.name = ""
        self.color = "Red"
        self.is_buzzed = False

        self._setup_join_screen()

    def _setup_join_screen(self):
        self.clear_frame()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=50, padx=50, fill="both", expand=True)

        ctk.CTkLabel(container, text="Join Game", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

        self.name_entry = ctk.CTkEntry(container, placeholder_text="Your Name", width=300, height=40)
        self.name_entry.pack(pady=10)

        self.ip_entry = ctk.CTkEntry(container, placeholder_text="Host IP Address", width=300, height=40)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=10)

        ctk.CTkLabel(container, text="Select Color", font=ctk.CTkFont(size=16)).pack(pady=10)
        
        # Get dynamic colors from audio manager
        colors = audio_manager.get_available_colors()
        if not colors:
            colors = ["Red"]
            
        self.color_var = ctk.StringVar(value=colors[0])
        color_menu = ctk.CTkOptionMenu(container, values=colors, variable=self.color_var, width=300, height=40)
        color_menu.pack(pady=10)

        self.join_btn = ctk.CTkButton(container, text="Join Server", 
                                     command=self._join_server,
                                     width=300, height=50,
                                     font=ctk.CTkFont(size=18, weight="bold"))
        self.join_btn.pack(pady=30)
        
        back_btn = ctk.CTkButton(container, text="Cancel", fg_color="transparent", border_width=1, command=self.back_callback)
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
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(info_frame, text=f"Playing as: {self.name}", font=ctk.CTkFont(size=14)).pack(side="left")
        
        color_indicator = ctk.CTkFrame(info_frame, width=20, height=20, corner_radius=10, fg_color=self.color)
        color_indicator.pack(side="right", padx=10)
        ctk.CTkLabel(info_frame, text=f"Color: {self.color}", font=ctk.CTkFont(size=14)).pack(side="right")

        # The Buzzer Button
        self.buzzer_btn = ctk.CTkButton(self, text="BUZZ", 
                                       command=self._buzz,
                                       fg_color=self.color,
                                       hover_color=self.color,
                                       width=300, height=300,
                                       corner_radius=150,
                                       font=ctk.CTkFont(size=40, weight="bold"))
        self.buzzer_btn.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(self, text="Ready!", font=ctk.CTkFont(size=20))
        self.status_label.pack(pady=10)

        # Hint label
        ctk.CTkLabel(self, text="Tip: Press SPACE to buzz", font=ctk.CTkFont(size=12), text_color="gray").pack()

        # Bind spacebar to buzz
        self.winfo_toplevel().bind("<space>", lambda e: self._buzz())

        # Leave Button
        leave_btn = ctk.CTkButton(self, text="Leave Game", 
                                 fg_color="transparent", border_width=1,
                                 command=self._on_back)
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
        original_color = self.color
        self.buzzer_btn.configure(fg_color="white", text_color="black")
        
        def finalize():
            self.buzzer_btn.configure(state="disabled", fg_color="gray", text_color="white")
            self.status_label.configure(text="BUZZED!", text_color=self.color)
            
        self.after(100, finalize)

    def _handle_reset(self):
        self.after(0, self._ui_reset)

    def _ui_reset(self):
        self.is_buzzed = False
        self.buzzer_btn.configure(state="normal", fg_color=self.color)
        self.status_label.configure(text="Ready!", text_color="white")

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
