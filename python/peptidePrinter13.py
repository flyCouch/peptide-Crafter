# ==============================================================================
# PROJECT:   PEPTIDE_MARK_I_V90_CARTESIAN_SNAP_FIX
# THEME:     Clinical Blue / Medical White
# FOCUS:     Alignment Fix | No Default Selection | Clean Placards
# __FILE__:  PeptidePrinter90.py
# __DATE__:  2026-04-03
# __TIME__:  22:10:00
# ==============================================================================

import customtkinter as ctk
import json
from datetime import datetime

# 25 Stations
AMINO_ACIDS = [
    "Alanine", "Arginine", "Asparagine", "Aspartic", "Cysteine",
    "Glutamine", "Glutamic", "Glycine", "Histidine", "Isoleucine",
    "Leucine", "Lysine", "Methionine", "Phenylal", "Proline",
    "Serine", "Threonine", "Tryptophan", "Tyrosine", "Valine"
]
SUPPORT_STATIONS = ["Deblock", "Activator", "Capping", "LAKE_UTIL", "WASH"]
STATION_NAMES = AMINO_ACIDS + SUPPORT_STATIONS

class StationData:
    def __init__(self, name):
        self.name = name
        self.reagent_ms = ctk.IntVar(value=250)
        self.activator_ms = ctk.IntVar(value=250)
        self.adv_release_ms = ctk.IntVar(value=50)
        self.pos_x = ctk.DoubleVar(value=0.0)
        self.pos_y = ctk.DoubleVar(value=0.0) 
        self.pos_z_travel = ctk.DoubleVar(value=5.0)  
        self.pos_z_strike = ctk.DoubleVar(value=15.5) 

class PeptideMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Console Header
        print(f"Project: PEPTIDE_MARK_I_V90 | __FILE__: PeptidePrinter90.py")
        print(f"Compile Date: {datetime.now().strftime('%Y-%m-%d')} | Time: {datetime.now().strftime('%H:%M:%S')}")

        self.title("Lyttle reSearch Peptide Crafting Control - CARTESIAN GANTRY")
        self.geometry("1850x1050")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name) for name in STATION_NAMES}
        
        # --- UI VARIABLES ---
        self.active_profile_name = ctk.StringVar(value="CARTESIAN_STABLE_V1")
        self.active_print_file = ctk.StringVar(value="NO_SEQUENCE_LOADED")
        self.total_req_time = ctk.StringVar(value="00:00:00")
        self.time_remaining = ctk.StringVar(value="00:00:00")
        
        self.cur_x = ctk.StringVar(value="000.00")
        self.cur_y = ctk.StringVar(value="000.00")
        self.cur_z = ctk.StringVar(value="000.00")
        
        # FIXED: Initialize as empty string so no radio button is lit by default
        self.active_station = ctk.StringVar(value="")
        
        self.jog_step = ctk.StringVar(value="1.0")
        self.speed_x = ctk.IntVar(value=2000)
        self.speed_y = ctk.IntVar(value=2000)
        self.speed_z = ctk.IntVar(value=1000)
        
        self.argon_psi = ctk.StringVar(value="5.00")
        self.pressure_factor = ctk.DoubleVar(value=1.0)
        self.o2_top = ctk.StringVar(value="20.9")
        self.o2_mid = ctk.StringVar(value="5.0")
        self.o2_bot = ctk.StringVar(value="0.1")

        self.setup_ui()

    def setup_ui(self):
        # --- 1. HEADER ---
        self.top_panel = ctk.CTkFrame(self, height=220, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x")
        self.top_panel.pack_propagate(False)

        p_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        p_frame.pack(side="left", padx=30, expand=True)
        ctk.CTkLabel(p_frame, text="CARTESIAN PROFILE", text_color="#62B6CB", font=("Arial", 12, "bold")).pack()
        ctk.CTkEntry(p_frame, textvariable=self.active_profile_name, width=220, height=40, font=("Arial", 16, "bold"), justify="center").pack(pady=5)
        p_btns = ctk.CTkFrame(p_frame, fg_color="transparent"); p_btns.pack()
        ctk.CTkButton(p_btns, text="LOAD", width=105, height=35, fg_color="#62B6CB", text_color="black").pack(side="left", padx=2)
        ctk.CTkButton(p_btns, text="SAVE", width=105, height=35, fg_color="#62B6CB", text_color="black").pack(side="left", padx=2)

        j_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        j_frame.pack(side="left", expand=True)
        ctk.CTkLabel(j_frame, text="FASTA SEQUENCE STREAM", text_color="#BEE9E8", font=("Arial", 12, "bold")).pack()
        ctk.CTkEntry(j_frame, textvariable=self.active_print_file, width=500, height=50, font=("Courier", 18, "bold"), text_color="#E63946", justify="center").pack(pady=5)
        f_row = ctk.CTkFrame(j_frame, fg_color="transparent"); f_row.pack()
        for txt in ["LOAD FASTA", "GENERATE G-CODE"]:
            ctk.CTkButton(f_row, text=txt, width=160, height=35, fg_color="#5FA8D3", text_color="black").pack(side="left", padx=5)

        a_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        a_frame.pack(side="right", padx=30, expand=True)
        ctk.CTkButton(a_frame, text="START", fg_color="#2D6A4F", width=180, height=140, font=("Arial", 32, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(a_frame, text="STOP", fg_color="#E63946", width=180, height=140, font=("Arial", 32, "bold")).pack(side="left", padx=10)

        # --- 2. MONITORING BAR ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0, height=120) 
        self.monitor_frame.pack(fill="x")
        self.monitor_frame.pack_propagate(False)
        m_inner = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        m_inner.place(relx=0.5, rely=0.5, anchor="center")
        
        t1 = ctk.CTkFrame(m_inner, fg_color="transparent"); t1.pack(side="left", padx=20)
        ctk.CTkLabel(t1, text="TOTAL CYCLE TIME", font=("Arial", 10, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t1, textvariable=self.total_req_time, font=("Courier", 36, "bold"), text_color="#1B4965").pack()
        
        dro_bg = ctk.CTkFrame(m_inner, fg_color="#1B4965", corner_radius=12, width=600, height=90)
        dro_bg.pack(side="left", padx=20); dro_bg.pack_propagate(False)
        dro_grid = ctk.CTkFrame(dro_bg, fg_color="transparent")
        dro_grid.place(relx=0.5, rely=0.5, anchor="center")
        for i, (axis, var) in enumerate([("X-AXIS", self.cur_x), ("Y-AXIS", self.cur_y), ("Z-AXIS", self.cur_z)]):
            cell = ctk.CTkFrame(dro_grid, fg_color="transparent", width=180)
            cell.grid(row=0, column=i, padx=5)
            ctk.CTkLabel(cell, text=axis, font=("Arial", 12, "bold"), text_color="#62B6CB").pack()
            ctk.CTkLabel(cell, textvariable=var, font=("Courier", 24, "bold"), text_color="white").pack()

        t2 = ctk.CTkFrame(m_inner, fg_color="transparent"); t2.pack(side="left", padx=20)
        ctk.CTkLabel(t2, text="REMAINING", font=("Arial", 10, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t2, textvariable=self.time_remaining, font=("Courier", 36, "bold"), text_color="#E63946").pack()

        # --- 3. WORK FRAME ---
        self.work_frame = ctk.CTkFrame(self, fg_color="#CAE9FF", corner_radius=0)
        self.work_frame.pack(fill="x")
        w_inner = ctk.CTkFrame(self.work_frame, fg_color="transparent")
        w_inner.pack(pady=10, padx=20, fill="x")

        # Jogging
        jog_col = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        jog_col.pack(side="left", padx=5)
        step_row = ctk.CTkFrame(jog_col, fg_color="transparent"); step_row.pack(pady=5)
        for s in ["0.1", "1.0", "10.0"]:
            ctk.CTkRadioButton(step_row, text=s, variable=self.jog_step, value=s, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        g = ctk.CTkFrame(jog_col, fg_color="transparent"); g.pack(padx=10, pady=5)
        for i, ax in enumerate(["X", "Y", "Z"]):
            ctk.CTkButton(g, text=f"{ax}-", width=45, height=30).grid(row=i, column=0, padx=2, pady=2)
            ctk.CTkButton(g, text=f"{ax}+", width=45, height=30).grid(row=i, column=1, padx=2, pady=2)
            ctk.CTkButton(g, text="HOME", fg_color="#1B4965", width=70, height=30, font=("Arial", 9, "bold")).grid(row=i, column=2, padx=(5, 2), pady=2)

        # Gantry Velocity
        sp_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sp_box.pack(side="left", padx=5, fill="y")
        ctk.CTkLabel(sp_box, text="GANTRY VELOCITY", font=("Arial", 11, "bold")).pack(pady=5)
        self.add_speed_control(sp_box, "X-TRAVEL", self.speed_x)
        self.add_speed_control(sp_box, "Y-TRAVEL", self.speed_y)
        self.add_speed_control(sp_box, "Z-STRIKE", self.speed_z)

        # Snap-Alignment (FIXED ALIGNMENT)
        sn_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sn_box.pack(side="left", expand=True, fill="both", padx=5)
        ctk.CTkLabel(sn_box, text="STATION SNAP-ALIGNMENT", font=("Arial", 11, "bold")).pack(pady=5)
        r_grid = ctk.CTkFrame(sn_box, fg_color="transparent"); r_grid.pack(expand=True, fill="both", padx=15, pady=5)
        for col in range(5): r_grid.grid_columnconfigure(col, weight=1)
        for i, name in enumerate(STATION_NAMES):
            ctk.CTkRadioButton(r_grid, text=name.upper(), variable=self.active_station, value=name, 
                             font=("Arial", 8, "bold")).grid(row=i//5, column=i%5, sticky="w", pady=2)

        # Atmosphere
        at_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=2, border_color="#1B4965", width=220)
        at_box.pack(side="right", fill="y", padx=5)
        at_box.pack_propagate(False)
        p_row = ctk.CTkFrame(at_box, fg_color="#1B4965", corner_radius=5)
        p_row.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(p_row, text="ARGON PSI", text_color="#62B6CB", font=("Arial", 9, "bold")).pack()
        psi_inner = ctk.CTkFrame(p_row, fg_color="transparent")
        psi_inner.pack()
        ctk.CTkLabel(psi_inner, textvariable=self.argon_psi, text_color="white", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkLabel(psi_inner, text=" (f):", text_color="#62B6CB", font=("Arial", 8)).pack(side="left", padx=(2, 0))
        ctk.CTkEntry(psi_inner, textvariable=self.pressure_factor, width=35, height=18, font=("Arial", 8), border_width=0).pack(side="left", padx=2)
        ctk.CTkButton(at_box, text="LAKE FILL", fg_color="#5FA8D3", text_color="black", height=28, font=("Arial", 10, "bold")).pack(pady=2, padx=10, fill="x")

        for loc, var in [("O2 TOP", self.o2_top), ("O2 MID", self.o2_mid), ("O2 BOT", self.o2_bot)]:
            o_row = ctk.CTkFrame(at_box, fg_color="#F0F5F9", corner_radius=5)
            o_row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(o_row, text=loc, font=("Arial", 8, "bold"), text_color="#1B4965").pack(side="left", padx=5)
            ctk.CTkLabel(o_row, textvariable=var, font=("Arial", 10, "bold"), text_color="#E63946").pack(side="right", padx=5)

        # --- 4. CLEAN PLACARDS ---
        self.card_frame = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.card_frame.pack(fill="both", expand=True, padx=20, pady=20)
        for i, name in enumerate(STATION_NAMES):
            card = ctk.CTkFrame(self.card_frame, border_width=1, border_color="#62B6CB", fg_color="white")
            card.grid(row=i//5, column=i%5, padx=3, pady=3, sticky="nsew")
            ctk.CTkLabel(card, text=name.upper(), font=("Arial", 11, "bold"), text_color="#1B4965").pack(pady=(10, 5))
            ctk.CTkButton(card, text="⚙", width=60, height=45, font=("Arial", 28), 
                        fg_color="transparent", text_color="#1B4965", hover_color="#BEE9E8",
                        command=lambda n=name: self.open_settings(n)).pack(pady=10)

        for c in range(5): self.card_frame.grid_columnconfigure(c, weight=1)
        for r in range(5): self.card_frame.grid_rowconfigure(r, weight=1)

    def add_speed_control(self, master, txt, var):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(fill="x", padx=10)
        ctk.CTkLabel(f, text=txt, font=("Arial", 9, "bold")).pack(side="left")
        ctk.CTkLabel(f, textvariable=var, font=("Arial", 9), text_color="#1B4965").pack(side="right")
        ctk.CTkSlider(master, from_=100, to=5000, variable=var, height=12, width=150).pack(padx=10, pady=(0, 5))

    def open_settings(self, name):
        data = self.storage[name]
        popup = ctk.CTkToplevel(self); popup.title(f"Calibration: {name}"); popup.geometry("550x720"); popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=f"COORDINATES: {name.upper()}", font=("Arial", 18, "bold")).pack(pady=15)
        
        p_box = ctk.CTkFrame(popup, fg_color="#F0F5F9", corner_radius=10); p_box.pack(fill="x", padx=25, pady=5)
        self.create_input(p_box, "X-Coordinate (mm):", data.pos_x)
        self.create_input(p_box, "Y-Coordinate (mm):", data.pos_y)
        self.create_input(p_box, "Z-Travel (Safe):", data.pos_z_travel)
        self.create_input(p_box, "Z-Strike (Plunge):", data.pos_z_strike)
        
        t_box = ctk.CTkFrame(popup, fg_color="transparent"); t_box.pack(fill="x", pady=10)
        r_f = ctk.CTkFrame(t_box, fg_color="transparent"); r_f.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(r_f, text=f"DISPENSE (ms):").pack(side="left")
        ctk.CTkEntry(r_f, textvariable=data.reagent_ms, width=75, justify="center").pack(side="left", padx=10)
        ctk.CTkButton(r_f, text="PURGE L-BARREL", width=120, fg_color="#E63946", font=("Arial", 10, "bold")).pack(side="right")
        
        if name in AMINO_ACIDS:
            a_f = ctk.CTkFrame(t_box, fg_color="transparent"); a_f.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(a_f, text="ACTIVATOR (ms):").pack(side="left")
            ctk.CTkEntry(a_f, textvariable=data.activator_ms, width=75, justify="center").pack(side="left", padx=10)
            ctk.CTkButton(a_f, text="PURGE ACTIV", width=120, fg_color="#E63946", font=("Arial", 10, "bold")).pack(side="right")
            self.create_input(t_box, "Adv Release (ms):", data.adv_release_ms)

        ctk.CTkButton(popup, text="Save to Profile", width=220, height=45, fg_color="#1B4965", command=popup.destroy).pack(pady=20)

    def create_input(self, master, label_text, variable):
        frame = ctk.CTkFrame(master, fg_color="transparent"); frame.pack(fill="x", padx=40, pady=4)
        ctk.CTkLabel(frame, text=label_text).pack(side="left")
        ctk.CTkEntry(frame, textvariable=variable, width=90, justify="center").pack(side="right")

if __name__ == "__main__":
    PeptideMarkI().mainloop()
