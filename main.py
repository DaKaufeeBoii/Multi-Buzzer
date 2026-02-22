import customtkinter as ctk
import sys
import socket
from host_gui import HostGUI
from participant_gui import ParticipantGUI

class BuzzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI-CLUB Buzzer")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.current_frame = None
        self.show_home_menu()

    def show_home_menu(self):
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self, corner_radius=15)
        self.current_frame.pack(pady=50, padx=50, fill="both", expand=True)

        title_label = ctk.CTkLabel(self.current_frame, text="AI-CLUB Buzzer", font=ctk.CTkFont(size=40, weight="bold"))
        title_label.pack(pady=(50, 20))

        subtitle_label = ctk.CTkLabel(self.current_frame, text="Select your mode", font=ctk.CTkFont(size=20))
        subtitle_label.pack(pady=10)

        button_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        button_frame.pack(pady=50)

        host_button = ctk.CTkButton(button_frame, text="Join as Host", 
                                   command=self.join_as_host,
                                   width=200, height=50,
                                   font=ctk.CTkFont(size=18, weight="bold"))
        host_button.pack(side="left", padx=20)

        participant_button = ctk.CTkButton(button_frame, text="Join as Participant", 
                                          command=self.join_as_participant,
                                          width=200, height=50,
                                          font=ctk.CTkFont(size=18, weight="bold"))
        participant_button.pack(side="left", padx=20)

        # Volume Control
        volume_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        volume_frame.pack(pady=30)
        
        ctk.CTkLabel(volume_frame, text="Global Volume", font=ctk.CTkFont(size=14)).pack()
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=1, 
                                          command=self._update_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(pady=10)

        info_label = ctk.CTkLabel(self.current_frame, text=f"Local IP: {self.get_local_ip()}", font=ctk.CTkFont(size=12))
        info_label.pack(side="bottom", pady=20)

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
