# ==============================================================================
# PROJECT:   PEPTIDE_MARK_I_V115_GCODE_LOADER
# THEME:     Clinical Blue / Medical White
# FOCUS:     Added LOAD G-CODE Button | No Other Changes
# __FILE__:  PeptidePrinter115.py
# __DATE__:  2026-04-04
# __TIME__:  14:45:00
# ==============================================================================

import customtkinter as ctk
import json
from datetime import datetime

# 30 Stations
AMINO_ACIDS = [
    "Alanine", "Arginine", "Asparagine", "Aspartic", "Cysteine",
    "Glutamine", "Glutamic", "Glycine", "Histidine", "Isoleucine",
    "Leucine", "Lysine", "Methionine", "Phenylal", "Proline",
    "Serine", "Threonine", "Tryptophan", "Tyrosine", "Valine"
]
SUPPORT_STATIONS = ["Deblock", "Activator", "Capping", "LAKE_UTIL", "WASH"]
RESERVED_STATIONS = ["RES_1", "RES_2", "RES_3", "RES_4", "RES_5"]
STATION_NAMES = AMINO_ACIDS + SUPPORT_STATIONS + RESERVED_STATIONS

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

    def to_dict(self):
        return {
            "reagent_ms": self.reagent_ms.get(),
            "activator_ms": self.activator_ms.get(),
            "adv_release_ms": self.adv_release_ms.get(),
            "x": round(self.pos_x.get(), 1),
            "y": round(self.pos_y.get(), 1),
            "z_travel": round(self.pos_z_travel.get(), 1),
            "z_strike": round(self.pos_z_strike.get(), 1)
        }

class PeptideMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()
        print(f"Project: PEPTIDE_MARK_I_V115 | __FILE__: PeptidePrinter115.py")
        print(f"Compile Date: {datetime.now().strftime('%Y-%m-%d')} | Time: {datetime.now().strftime('%H:%M:%S')}")

        self.title("Lyttle reSearch Peptide Control - 30 STATION V115")
        self.geometry("1850x1150")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name) for name in STATION_NAMES}
        
        self.active_profile_name = ctk.StringVar(value="ronProfile")
        self.active_print_file = ctk.StringVar(value="NO_SEQUENCE_LOADED")
        self.total_req_time = ctk.StringVar(value="00:00:00")
        self.time_remaining = ctk.StringVar(value="00:00:00")
        
        self.val_x = ctk.DoubleVar(value=-999.9); self.val_y = ctk.DoubleVar(value=-999.9); self.val_z = ctk.DoubleVar(value=-999.9)
        self.cur_x = ctk.StringVar(value="-999.9"); self.cur_y = ctk.StringVar(value="-999.9"); self.cur_z = ctk.StringVar(value="-999.9")
        self.val_x.trace_add("write", lambda *args: self.cur_x.set(f"{self.val_x.get():.1f}"))
        self.val_y.trace_add("write", lambda *args: self.cur_y.set(f"{self.val_y.get():.1f}"))
        self.val_z.trace_add("write", lambda *args: self.cur_z.set(f"{self.val_z.get():.1f}"))
        
        self.active_station = ctk.StringVar(value="")
        self.jog_step = ctk.StringVar(value="1.0")
        self.speed_x = ctk.IntVar(value=2000); self.speed_y = ctk.IntVar(value=2000); self.speed_z = ctk.IntVar(value=1000)
        self.argon_psi = ctk.StringVar(value="5.00")

        self.setup_ui()

    def setup_ui(self):
        # --- HEADER PANEL ---
        self.top_panel = ctk.CTkFrame(self, height=160, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x"); self.top_panel.pack_propagate(False)
        h_wrap = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        h_wrap.place(relx=0.5, rely=0.5, anchor="center")

        p_box = ctk.CTkFrame(h_wrap, fg_color="transparent")
        p_box.pack(side="left", padx=20)
        ctk.CTkEntry(p_box, textvariable=self.active_profile_name, width=180, font=("Arial", 14, "bold")).pack()
        p_btns = ctk.CTkFrame(p_box, fg_color="transparent"); p_btns.pack(pady=5)
        ctk.CTkButton(p_btns, text="LOAD", width=85, fg_color="#62B6CB", text_color="black").pack(side="left", padx=2)
        ctk.CTkButton(p_btns, text="SAVE PROFILE", width=120, fg_color="#62B6CB", text_color="black", command=self.save_global_profile).pack(side="left", padx=2)

        j_box = ctk.CTkFrame(h_wrap, fg_color="transparent")
        j_box.pack(side="left", padx=20)
        ctk.CTkEntry(j_box, textvariable=self.active_print_file, width=400, height=40, font=("Courier", 16), text_color="#E63946").pack()
        f_btns = ctk.CTkFrame(j_box, fg_color="transparent"); f_btns.pack(pady=5)
        ctk.CTkButton(f_btns, text="LOAD FASTA", fg_color="#5FA8D3", text_color="black", width=110).pack(side="left", padx=2)
        ctk.CTkButton(f_btns, text="GENERATE G-CODE", fg_color="#5FA8D3", text_color="black", width=140).pack(side="left", padx=2)
        ctk.CTkButton(f_btns, text="LOAD G-CODE", fg_color="#5FA8D3", text_color="black", width=120).pack(side="left", padx=2)

        ctk.CTkButton(h_wrap, text="START", fg_color="#2D6A4F", width=120, height=100, font=("Arial", 20, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(h_wrap, text="STOP", fg_color="#E63946", width=120, height=100, font=("Arial", 20, "bold")).pack(side="left", padx=10)

        # --- MONITORING ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0, height=100) 
        self.monitor_frame.pack(fill="x"); self.monitor_frame.pack_propagate(False)
        m_inner = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        m_inner.place(relx=0.5, rely=0.5, anchor="center")
        
        t1_box = ctk.CTkFrame(m_inner, fg_color="transparent"); t1_box.pack(side="left", padx=40)
        ctk.CTkLabel(t1_box, text="TOTAL TIME", font=("Arial", 11, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t1_box, textvariable=self.total_req_time, font=("Courier", 34, "bold"), text_color="#1B4965").pack()
        
        dro_bg = ctk.CTkFrame(m_inner, fg_color="#1B4965", corner_radius=10, width=700, height=80)
        dro_bg.pack(side="left"); dro_bg.pack_propagate(False)
        dg = ctk.CTkFrame(dro_bg, fg_color="transparent")
        dg.place(relx=0.5, rely=0.5, anchor="center")
        for i, (ax, var) in enumerate([("X-AXIS", self.cur_x), ("Y-AXIS", self.cur_y), ("Z-AXIS", self.cur_z)]):
            f = ctk.CTkFrame(dg, fg_color="transparent", width=230)
            f.grid(row=0, column=i)
            ctk.CTkLabel(f, text=ax, font=("Arial", 10, "bold"), text_color="#62B6CB").pack()
            ctk.CTkLabel(f, textvariable=var, font=("Courier", 24, "bold"), text_color="white").pack()

        t2_box = ctk.CTkFrame(m_inner, fg_color="transparent"); t2_box.pack(side="left", padx=40)
        ctk.CTkLabel(t2_box, text="REMAINING", font=("Arial", 11, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t2_box, textvariable=self.time_remaining, font=("Courier", 34, "bold"), text_color="#E63946").pack()

        # --- COMMAND ROW ---
        self.cmd_row = ctk.CTkFrame(self, fg_color="#CAE9FF", height=200)
        self.cmd_row.pack(fill="x")
        c_inner = ctk.CTkFrame(self.cmd_row, fg_color="transparent")
        c_inner.place(relx=0.5, rely=0.5, anchor="center")

        jog_box = ctk.CTkFrame(c_inner, fg_color="white", border_width=1, border_color="#1B4965")
        jog_box.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(jog_box, text="JOG CONTROL", font=("Arial", 11, "bold")).pack(pady=2)
        s_row = ctk.CTkFrame(jog_box, fg_color="transparent"); s_row.pack()
        for s in ["0.1", "1.0", "10.0"]:
            ctk.CTkRadioButton(s_row, text=s, variable=self.jog_step, value=s, font=("Arial", 9)).pack(side="left", padx=5)
        g = ctk.CTkFrame(jog_box, fg_color="transparent"); g.pack(padx=10, pady=5)
        for i, (ax, var) in enumerate([("X", self.val_x), ("Y", self.val_y), ("Z", self.val_z)]):
            ctk.CTkButton(g, text=f"{ax}-", width=45, height=30, command=lambda v=var: v.set(v.get()-float(self.jog_step.get()))).grid(row=i, column=0, pady=2, padx=2)
            ctk.CTkButton(g, text=f"{ax}+", width=45, height=30, command=lambda v=var: v.set(v.get()+float(self.jog_step.get()))).grid(row=i, column=1, pady=2, padx=2)
            ctk.CTkButton(g, text="HOME", fg_color="#1B4965", width=70, height=30, font=("Arial", 9, "bold")).grid(row=i, column=2, padx=2)

        av_box = ctk.CTkFrame(c_inner, fg_color="white", border_width=1, border_color="#1B4965")
        av_box.pack(side="left", padx=10, pady=10, fill="y")
        ctk.CTkLabel(av_box, text="AXIS VELOCITY", font=("Arial", 11, "bold")).pack(pady=2)
        self.add_speed_control(av_box, "X-AXIS", self.speed_x)
        self.add_speed_control(av_box, "Y-AXIS", self.speed_y)
        self.add_speed_control(av_box, "Z-AXIS", self.speed_z)

        ss_box = ctk.CTkFrame(c_inner, fg_color="white", border_width=1, border_color="#1B4965")
        ss_box.pack(side="left", padx=10, pady=10, fill="y")
        ctk.CTkLabel(ss_box, text="STATION SNAP", font=("Arial", 11, "bold")).pack(pady=2)
        ss_grid = ctk.CTkFrame(ss_box, fg_color="transparent")
        ss_grid.pack(padx=15, pady=5)
        for i, name in enumerate(STATION_NAMES):
            ctk.CTkRadioButton(ss_grid, text=name.upper()[:4], variable=self.active_station, value=name, font=("Arial", 8)).grid(row=i//5, column=i%5, padx=2)

        ar_box = ctk.CTkFrame(c_inner, fg_color="white", border_width=1, border_color="#1B4965")
        ar_box.pack(side="left", padx=10, pady=10, fill="y")
        ctk.CTkLabel(ar_box, text="ARGON", font=("Arial", 11, "bold")).pack(pady=2)
        p_disp = ctk.CTkFrame(ar_box, fg_color="#1B4965"); p_disp.pack(padx=10, pady=5)
        ctk.CTkLabel(p_disp, textvariable=self.argon_psi, text_color="white", font=("Arial", 16, "bold")).pack(padx=10)
        ctk.CTkButton(ar_box, text="LAKE FILL", height=30, font=("Arial", 10)).pack(pady=2)
        ctk.CTkLabel(ar_box, text="●", font=("Arial", 40), text_color="#2D6A4F").pack()

        # --- GRID ---
        self.grid_container = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.grid_container.pack(fill="both", expand=True, padx=10, pady=10)
        for i, name in enumerate(STATION_NAMES):
            p = ctk.CTkFrame(self.grid_container, border_width=1, border_color="#62B6CB", fg_color="white")
            p.grid(row=i//5, column=i%5, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(p, text=name.upper(), font=("Arial", 14, "bold"), text_color="#1B4965").pack(pady=(25, 10))
            ctk.CTkButton(p, text="⚙", width=50, height=50, font=("Arial", 30), fg_color="transparent", 
                        text_color="#1B4965", hover_color="#BEE9E8", command=lambda n=name: self.open_settings(n)).pack()

        for c in range(5): self.grid_container.grid_columnconfigure(c, weight=1)
        for r in range(6): self.grid_container.grid_rowconfigure(r, weight=1)

    def add_speed_control(self, master, txt, var):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(f, text=txt, font=("Arial", 9, "bold")).pack(side="left")
        ctk.CTkLabel(f, textvariable=var, font=("Arial", 9), text_color="#1B4965").pack(side="right")
        ctk.CTkSlider(master, from_=100, to=5000, variable=var, width=150, height=14).pack(padx=10, pady=(0, 5))

    def open_settings(self, name):
        master_data = self.storage[name]
        pop = ctk.CTkToplevel(self); pop.title(f"Live Tuning: {name}"); pop.geometry("550x700"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text=f"STATION: {name.upper()}", font=("Arial", 18, "bold"), text_color="#1B4965").pack(pady=20)
        
        c_f = ctk.CTkFrame(pop, fg_color="#F0F5F9", corner_radius=10); c_f.pack(fill="x", padx=30, pady=10)
        self.create_direct_input(c_f, "X Position (mm):", master_data.pos_x)
        self.create_direct_input(c_f, "Y Position (mm):", master_data.pos_y)
        self.create_direct_input(c_f, "Z-Travel (Safe):", master_data.pos_z_travel)
        self.create_direct_input(c_f, "Z-Strike (Plunge):", master_data.pos_z_strike)

        t_f = ctk.CTkFrame(pop, fg_color="transparent"); t_f.pack(fill="x", pady=10)
        r_row = ctk.CTkFrame(t_f, fg_color="transparent"); r_row.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(r_row, text="REAGENT (ms):").pack(side="left")
        ctk.CTkEntry(r_row, textvariable=master_data.reagent_ms, width=80).pack(side="left", padx=10)
        ctk.CTkButton(r_row, text="PURGE REAGENT", fg_color="#E63946", width=130, font=("Arial", 10, "bold")).pack(side="right")

        if name in AMINO_ACIDS or "RES" in name:
            a_row = ctk.CTkFrame(t_f, fg_color="transparent"); a_row.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(a_row, text="ACTIVATOR (ms):").pack(side="left")
            ctk.CTkEntry(a_row, textvariable=master_data.activator_ms, width=80).pack(side="left", padx=10)
            ctk.CTkButton(a_row, text="PURGE ACTIV", fg_color="#E63946", width=130, font=("Arial", 10, "bold")).pack(side="right")
            self.create_direct_input(t_f, "Adv Release (ms):", master_data.adv_release_ms)

        ctk.CTkLabel(pop, text="Values apply instantly. Use SAVE PROFILE to make permanent.", font=("Arial", 10, "italic")).pack(pady=10)
        ctk.CTkButton(pop, text="CLOSE TUNING", command=pop.destroy, fg_color="#1B4965", height=45, width=200).pack(pady=20)

    def create_direct_input(self, master, label, var):
        row = ctk.CTkFrame(master, fg_color="transparent"); row.pack(fill="x", padx=30, pady=6)
        ctk.CTkLabel(row, text=label).pack(side="left")
        ctk.CTkEntry(row, textvariable=var, width=100, justify="center").pack(side="right")

    def save_global_profile(self):
        config = {n: d.to_dict() for n, d in self.storage.items()}
        filename = f"{self.active_profile_name.get()}.json"
        with open(filename, "w") as f:
            json.dump(config, f, indent=4)
        print(f"GLOBAL PROFILE '{filename}' SAVED.")

if __name__ == "__main__":
    PeptideMarkI().mainloop()
