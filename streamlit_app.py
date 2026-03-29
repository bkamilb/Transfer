import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import plotly.express as px
import plotly.graph_objects as go

# --- 1. MUSTERMANN TAM EŞİKLER ---
mustermann = {
    "GK": {
        "Poss Won/90": [7.25, 7.62, 8.17, 8.53], "Ps A/90": [21.58, 23.26, 24.38, 26.06],
        "Pr passes/90": [0.37, 0.58, 0.74, 0.98], "Poss Lost/90": [8.21, 6.04, 3.67, 2.35]
    },
    "DEF": {
        "Poss Won/90": [8.33, 9.09, 9.77, 10.54], "Hdr %": [52.4, 60.8, 65.6, 70.7],
        "Aer A/90": [3.15, 3.82, 4.57, 5.35], "Tck R": [72.4, 74.7, 76.7, 79.0],
        "Tck A/90": [0.87, 1.07, 2.25, 3.48], "Int/90": [2.38, 2.65, 2.88, 3.12],
        "Clr/90": [0.90, 1.03, 1.13, 1.28], "Blk/90": [0.56, 0.62, 0.68, 0.75],
        "xG/90": [0.01, 0.02, 0.03, 0.04], "Shot/90": [0.25, 0.34, 0.48, 0.68],
        "xA/90": [0.02, 0.03, 0.06, 0.13], "KP/90": [0.20, 0.29, 0.77, 1.39],
        "Drb/90": [0.04, 0.08, 0.55, 1.75], "Poss Lost/90": [12.01, 8.18, 4.90, 4.05],
        "Pr passes/90": [3.19, 4.44, 6.18, 7.95], "Ps A/90": [50.96, 56.45, 62.33, 69.88]
    },
    "MID": {
        "Poss Won/90": [5.63, 6.92, 7.82, 8.53], "KP/90": [0.87, 1.2, 1.6, 2.08],
        "xA/90": [0.06, 0.09, 0.13, 0.19], "Ps A/90": [48.62, 54.66, 60.74, 68.83],
        "Pr passes/90": [3.69, 5.02, 5.82, 6.91], "Int/90": [1.96, 2.32, 2.52, 2.86],
        "Poss Lost/90": [10.21, 8.44, 7.15, 6.04], "Aer A/90": [1.67, 2.16, 2.64, 3.45], "Hdr %": [27.0, 36.1, 44.8, 54.4],
        "Tck R": [67.3, 69.8, 72.4, 74.7], "Tck A/90": [1.49, 1.98, 2.34, 2.72],
        "Clr/90": [0.49, 0.70, 0.84, 1.01], "Blk/90": [0.27, 0.40, 0.51, 0.61],
        "xG/90": [0.04, 0.06, 0.11, 0.22], "Shot/90": [0.88, 1.17, 1.57, 2.02], "Drb/90": [0.22, 0.37, 0.72, 1.56]
    },
    "FWD": {
        "xG/90": [0.21, 0.26, 0.32, 0.40], "Shot/90": [1.96, 2.22, 2.47, 2.81],
        "Drb/90": [0.84, 1.63, 3.43, 5.62], "xA/90": [0.12, 0.16, 0.21, 0.26],
        "KP/90": [1.18, 1.53, 1.95, 2.31], "Poss Lost/90": [14.95, 12.36, 8.53, 6.12],
        "Poss Won/90": [2.47, 4.16, 6.52, 7.52], "Hdr %": [19.5, 26.9, 33.5, 40.3],
        "Aer A/90": [2.92, 3.60, 4.94, 6.86], "Tck R": [65.3, 70.7, 74.0, 76.6],
        "Tck A/90": [0.48, 1.24, 2.34, 2.94], "Int/90": [0.90, 1.37, 1.97, 2.34],
        "Clr/90": [0.17, 0.31, 0.49, 0.64], "Blk/90": [0.10, 0.16, 0.24, 0.32],
        "Pr passes/90": [0.98, 2.10, 3.55, 4.75], "Ps A/90": [28.63, 35.10, 43.27, 50.29]
    }
}

# --- LİG KATSAYILARI ---
LEAGUE_RANKING_MULTIPLIERS = {
    "Premier League": 1.00, "First Division": 1.00,
    "Spanish First Division": 0.95, "German Bundesliga": 0.95, "Italian Serie A": 0.95, "Serie A": 0.95,
    "Ligue 1 McDonald's": 0.95, "Portuguese Premier League": 0.90, "Eredivisie": 0.90,
    "Sky Bet Championship": 0.88, "Belgian Jupiler Pro League": 0.88,
    "Turkish Super League": 0.85, "Brazilian National First Division": 0.85,
    "Austrian Premier Division": 0.82, "Scottish William Hill Premiership": 0.82, "MLS": 0.80,
    "Polish Ekstraklasa": 0.78, "Turkish 1. League": 0.75, "Second Division": 0.75,
    "Intermedia": 0.70, "I League": 0.70, "Metropolitan Zone B": 0.65,
    "DEFAULT": 0.70
}

# --- KARAKTER & KİŞİLİK KATSOYILARI ---
CHARACTER_MULTIPLIERS = {
    "Model Citizen": 1.10, "Model Professional": 1.10, "Professional": 1.08, "Perfectionist": 1.06,
    "Driven": 1.05, "Determined": 1.04, "Unflappable": 1.05, "Evasive": 1.04, "Reserved": 1.03, 
    "Level-headed": 1.03, "Media-friendly": 1.01, "Balanced": 1.00, "Normal": 1.00, "Quiet": 1.00,
    "Volatile": 0.94, "Outspoken": 0.95, "Confrontational": 0.93, "Short-fused": 0.92,
    "Casual": 0.92, "Slack": 0.90, "Temperamental": 0.90
}

# --- YARDIM SÖZLÜĞÜ ---
stat_yardim = {
    "IP_Score": "Hücum Skoru (Top takımdaysa).",
    "OOP_Score": "Savunma Skoru (Top rakipteyse).",
    "Scout_Puanı": "Nihai Scout Kalite Skoru.",
    "VFM_Skoru": "Value For Money: Maliyet/Verim oranı."
}

# --- 2. DİNAMİK PROFİLLER ---
rol_isimleri = {"⚖️ Dengeli": "Dengeli", "⚔️ IP (Hücum)": "IP (Hücum)", "🛡️ OOP (Svn)": "OOP (Savunma)"}
ana_mevki_listesi = ["Kaleci", "Stoper", "Bek", "DM", "AM", "Kanat", "Forvet"]

role_map = {
    "Kaleci": {"bench": "GK", "weights": {"Dengeli": {"Poss Won/90": 1.0, "Ps A/90": 0.8}, "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.2}, "OOP (Savunma)": {"Poss Won/90": 1.5, "Ps A/90": 0.5}}},
    "Stoper": {"bench": "DEF", "weights": {"Dengeli": {"Tck A/90": 1.0, "Int/90": 1.0, "Aer A/90": 0.9, "Ps A/90": 0.5}, "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.2, "Int/90": 0.8, "Tck A/90": 0.5}, "OOP (Savunma)": {"Tck A/90": 1.5, "Int/90": 1.5, "Aer A/90": 1.2, "Blk/90": 1.0, "Clr/90": 0.8}}},
    "Bek": {"bench": "DEF", "weights": {"Dengeli": {"xA/90": 1.0, "Tck A/90": 1.0, "Drb/90": 0.9, "Int/90": 0.8}, "IP (Hücum)": {"xA/90": 1.5, "Drb/90": 1.5, "KP/90": 1.2, "Pr passes/90": 1.0}, "OOP (Savunma)": {"Tck A/90": 1.5, "Int/90": 1.5, "Poss Won/90": 1.0, "Aer A/90": 0.8}}},
    "DM": {"bench": "MID", "weights": {"Dengeli": {"Poss Won/90": 1.0, "Int/90": 1.0, "Ps A/90": 0.9, "Tck A/90": 0.8}, "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.5, "KP/90": 1.0, "Poss Won/90": 0.5}, "OOP (Savunma)": {"Poss Won/90": 1.5, "Int/90": 1.5, "Tck A/90": 1.2, "Ps A/90": 0.5}}},
    "AM": {"bench": "MID", "weights": {"Dengeli": {"KP/90": 1.0, "xA/90": 1.0, "Pr passes/90": 0.9, "Shot/90": 0.6}, "IP (Hücum)": {"KP/90": 1.5, "xA/90": 1.5, "Drb/90": 1.2, "Shot/90": 1.0}, "OOP (Savunma)": {"Poss Won/90": 1.5, "Int/90": 1.2, "Tck A/90": 1.0, "KP/90": 0.6}}},
    "Kanat": {"bench": "MID", "weights": {"Dengeli": {"Drb/90": 1.0, "xA/90": 1.0, "KP/90": 0.9, "xG/90": 0.8}, "IP (Hücum)": {"xG/90": 1.5, "xA/90": 1.5, "Drb/90": 1.2, "Shot/90": 1.2}, "OOP (Savunma)": {"Poss Won/90": 1.5, "Tck A/90": 1.2, "Drb/90": 0.8, "xA/90": 0.5}}},
    "Forvet": {"bench": "FWD", "weights": {"Dengeli": {"xG/90": 1.0, "Shot/90": 1.0, "xA/90": 0.6}, "IP (Hücum)": {"xA/90": 1.5, "KP/90": 1.5, "xG/90": 0.8, "Ps A/90": 1.0}, "OOP (Savunma)": {"xG/90": 1.5, "Aer A/90": 1.5, "Poss Won/90": 1.2, "Shot/90": 1.2}}}
}

# --- 3. FONKSİYONLAR ---
def clean_key(text): return re.sub(r'[^a-zA-Z]', '', str(text)).lower()

def to_num(val):
    if pd.isna(val): return 0.0
    try:
        if isinstance(val, str): val = val.replace('%','').replace(',','.').strip()
        return float(val)
    except: return 0.0

def get_mustermann_color(val, stat_name, role):
    v = to_num(val)
    role_config = role_map.get(role)
    if not role_config: return "background-color: #1a1a1a;"
    bench_key = role_config.get('bench')
    if not bench_key or bench_key not in mustermann: return "background-color: #1a1a1a;"
    clean_target = clean_key(stat_name)
    target_key = next((k for k in mustermann[bench_key].keys() if clean_key(k) == clean_target), None)
    if not target_key: return "background-color: #1a1a1a; color: #555555;"
    thresh = mustermann[bench_key][target_key]
    if "lost" in target_key.lower():
        if v <= thresh[3]: return "background-color: #6a0dad; color: #ffffff;" 
        if v <= thresh[2]: return "background-color: #2e7d32; color: #ffffff;" 
        if v <= thresh[1]: return "background-color: #fbc02d; color: #000000;" 
        return "background-color: #c62828; color: #ffffff;" 
    if v >= thresh[3]: return "background-color: #6a0dad; color: #ffffff;" 
    if v >= thresh[2]: return "background-color: #2e7d32; color: #ffffff;" 
    if v >= thresh[1]: return "background-color: #fbc02d; color: #000000;" 
    return "background-color: #c62828; color: #ffffff;" 

def parse_price(v):
    if pd.isna(v) or v == "" or v == "-": return 0.0
    v = str(v).replace('€','').replace(' ','').strip()
    if '-' in v: v = v.split('-')[-1].strip()
    mult = 1.0
    if 'M' in v: mult = 1000000.0; v = v.replace('M', '')
    elif 'K' in v: mult = 1000.0; v = v.replace('K', '')
    try: return float(re.sub(r'[^\d.]', '', v.replace(',', '.'))) * mult
    except: return 0.0

def get_role(pos, sec_pos=""):
    combined = (str(pos) + " " + str(sec_pos)).upper()
    
    # 1. Temel Bölge Tespitleri
    # AM (RLC) veya M (RLC) gibi durumlarda dize içindeki harfleri hassas yakalamak için:
    has_am_zone = "AM " in combined or "AM/" in combined or "AMR" in combined or "AML" in combined or "AMC" in combined
    has_m_zone = "M " in combined or "M/" in combined or "MR" in combined or "ML" in combined or "MC" in combined
    
    # 2. Yön Tespitleri (AMRLC gibi hibritlerde R, L ve C var mı?)
    # AM (RLC) yazımında AM ve parantez içindeki harfleri kontrol ediyoruz.
    # Örnek: "AM (RLC)" -> AM zone içinde R, L ve C var.
    has_r_direction = any(x in combined for x in ["(R", "R)", "R,", "RC", "RL", "AMR", "MR"])
    has_l_direction = any(x in combined for x in ["(L", "L)", "L,", "LC", "RL", "AML", "ML"])
    has_c_direction = any(x in combined for x in ["(C", "C)", "C,", "RC", "LC", "AMC", "MC", "S (C", "ST (C", "D (C"])

    # 3. Kategori Bayrakları
    has_kanat_mevki = (has_am_zone or has_m_zone) and (has_r_direction or has_l_direction)
    has_amc = has_am_zone and has_c_direction
    has_fwd = any(k in combined for k in ["ST", "S (C)", "ST (C)"])
    has_side_def = any(x in combined for x in ["D (R", "D (L", "D (RL"])
    has_stoper = "D (C)" in combined
    has_wb = "WB (" in combined
    has_dm = "DM" in combined
    has_gk = "GK" in combined

    # --- HİYERARŞİ VE TWEAK KURALLARI ---

    # KURAL: AMC de varsa (örneğin AMRLC) Kanat hiyerarşisi her zaman önceliklidir (Bek/WB olsa bile)
    if has_kanat_mevki:
        # AMC varsa doğrudan Kanat
        if has_amc: return "Kanat"
        # AMC yoksa ama Forvet veya Bek kombinasyonu varsa yine Kanat (Winger-Forward hibriti)
        if has_fwd or has_side_def: return "Kanat"
        # Saf kanat (AMR, ML vb.)
        return "Kanat"
    
    # KURAL: Bek + Kanat Bek + Kanat (AMC YOKSA) -> Bek
    # Not: Yukarıdaki if kanat mevkisi varsa çalışacağı için, 
    # AMRLC gibi AMC'li oyuncular zaten yukarıda "Kanat" olarak elenecek.
    if has_side_def and has_wb and has_kanat_mevki and not has_amc: 
        return "Bek"

    # --- GENEL ÖNCELİK SIRALAMASI (Ne varsa ona göre) ---
    if has_fwd: return "Forvet"
    if has_amc: return "AM"
    if has_dm: return "DM"
    if has_stoper: return "Stoper"
    if has_gk: return "Kaleci"
    if has_side_def: return "Bek"
    
    return "Bek" # Varsayılan

RADAR_COLORS = ['#00f2ff', '#ff0055', '#00ff66', '#ffaa00']

# --- 4. STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="Moneyball Ultimate")
st.markdown("""<style>.main { background-color: #0E1117; color: white; } .stProgress > div > div > div > div { background-color: #00f2ff; } div.row-widget.stRadio > div { flex-direction: row; gap: 15px; justify-content: center; }</style>""", unsafe_allow_html=True)
st.title("💰 FM26 Moneyball: Ultimate Decision Maker")
file = st.file_uploader("FM Export CSV'sini Yükle", type="csv")

if file:
    df = pd.read_csv(file, sep=";")
    df['Minutes'] = df['Minutes'].apply(lambda x: x if x > 0 else 1)
    df['Price_Num'] = df['Transfer Value'].apply(parse_price)
    if 'Tck A' in df.columns: df['Tck A/90'] = (df['Tck A'].apply(to_num) * 90) / df['Minutes']
    
    # Session State
    if 'player_preferences' not in st.session_state: st.session_state.player_preferences = {}
    if 'player_base_roles' not in st.session_state: st.session_state.player_base_roles = {}
    
    # Varsayılanları ata
    for idx, row in df.iterrows():
        p_name = row['Player']
        if p_name not in st.session_state.player_base_roles:
            sec_pos_val = row.get('Sec. Position', "")
            st.session_state.player_base_roles[p_name] = get_role(row['Position'], sec_pos_val)
        if p_name not in st.session_state.player_preferences:
            st.session_state.player_preferences[p_name] = "⚖️ Dengeli"

    df['Role'] = df['Player'].apply(lambda x: st.session_state.player_base_roles.get(x, "Bek"))
    df['Rol_Secimi'] = df['Player'].apply(lambda x: st.session_state.player_preferences.get(x, "⚖️ Dengeli"))

    st.sidebar.header("🎯 Strateji & Bütçe")
    strategy = st.sidebar.radio("Strateji", ["Kâr Odaklı (Geliştir-Sat)", "Performans (Glory)"])
    min_v, max_v = int(df['Price_Num'].min()), int(df['Price_Num'].max())
    budget = st.sidebar.slider("Bonservis Aralığı", min_value=min_v, max_value=max_v, value=(min_v, max_v), step=100000)

    # --- HESAPLAMA MOTORU ---
    def calc_scores(row):
        player_role = str(row.get('Role', "Bek"))
        if player_role not in role_map: player_role = "Bek"
        
        config = role_map[player_role]
        bench = mustermann.get(config['bench'], {})
        results = {}
        for dict_key, prof_name in [("Dengeli", "Dengeli_Ham"), ("IP (Hücum)", "IP_Ham"), ("OOP (Savunma)", "OOP_Ham")]:
            scores = []
            active_weights = config['weights'].get(dict_key, config['weights']["Dengeli"])
            for s, w in active_weights.items():
                if s in row:
                    target_key = next((k for k in bench.keys() if clean_key(k) == clean_key(s)), None)
                    if target_key: scores.append((to_num(row[s]) / bench[target_key][3]) * 100 * w)
            results[prof_name] = np.mean(scores) if scores else 0
        
        league_name = row.get('Division', 'Unknown')
        multiplier = LEAGUE_RANKING_MULTIPLIERS.get(league_name, LEAGUE_RANKING_MULTIPLIERS["DEFAULT"])
        raw_char = str(row.get('Personality', row.get('Media Handling', 'Balanced')))
        char_mults = [CHARACTER_MULTIPLIERS.get(t.strip(), 1.0) for t in raw_char.split(',') if t.strip() in CHARACTER_MULTIPLIERS]
        char_multiplier = np.mean(char_mults) if char_mults else 1.0
        
        secili_rol = str(row.get('Rol_Secimi', "⚖️ Dengeli"))
        if secili_rol not in rol_isimleri: secili_rol = "⚖️ Dengeli"
        
        if secili_rol == "⚖️ Dengeli": final_raw = results["Dengeli_Ham"]
        elif secili_rol == "⚔️ IP (Hücum)": final_raw = (results["Dengeli_Ham"] * 0.7) + (results["IP_Ham"] * 0.3)
        else: final_raw = (results["Dengeli_Ham"] * 0.7) + (results["OOP_Ham"] * 0.3)
        
        total_mult = multiplier * char_multiplier
        bonus = max(0, (23 - row['Age']) * 5) if strategy == "Kâr Odaklı (Geliştir-Sat)" else 0
        
        return pd.Series([final_raw * total_mult + bonus, results["IP_Ham"] * total_mult + bonus, results["OOP_Ham"] * total_mult + bonus])

    df[['Scout_Puanı', 'IP_Score', 'OOP_Score']] = df.apply(calc_scores, axis=1)
    df['VFM_Skoru'] = (df['Scout_Puanı'] / ((df['Price_Num'] / 1000000) + 1)).round(1) 
    f_df = df[(df['Price_Num'] >= budget[0]) & (df['Price_Num'] <= budget[1])].sort_values('Scout_Puanı', ascending=False)

    col_m, col_s = st.columns([2, 1])
    with col_s:
        st.subheader("🎯 Scout Kartı & Kıyaslama")
        selected = st.selectbox("Ana Oyuncu:", f_df['Player'].tolist())
        selected_all = [selected] + st.multiselect("Kıyaslanacaklar:", [p for p in f_df['Player'].tolist() if p != selected], max_selections=3)
        p = f_df[f_df['Player'] == selected].iloc[0]
        
        p_pref = str(p['Rol_Secimi'])
        if p_pref not in rol_isimleri: p_pref = "⚖️ Dengeli"
        aktif_rol_str = rol_isimleri[p_pref]
        
        legend_html = "".join([f"<div style='color: {RADAR_COLORS[i]}; font-weight: bold; margin-top: 3px;'>■ {p_name}</div>" for i, p_name in enumerate(selected_all)])
        st.markdown(f"""<div style='display: flex; background-color:#161a24; padding:15px; border-radius:8px; margin-bottom:15px; border:1px solid #333333; justify-content: space-between; align-items: center;'><div style='display: flex; gap: 30px;'><div style='text-align: center;'><div style='font-size:12px; color:#aaaaaa;'>Puan ({aktif_rol_str})</div><div style='font-size:28px; font-weight:bold; color:#00f2ff;'>{round(p['Scout_Puanı'], 1)}</div></div><div style='text-align: center;'><div style='font-size:12px; color:#aaaaaa;'>VFM Skoru</div><div style='font-size:28px; font-weight:bold; color:#ff0055;'>{p['VFM_Skoru']}</div></div></div><div style='text-align: left; font-size: 12px; background-color: #0e1117; padding: 10px; border-radius: 5px; border: 1px solid #222222; min-width: 140px;'>{legend_html}</div></div>""", unsafe_allow_html=True)

        role = p['Role']
        if role_map[role]['bench'] in mustermann:
            bench = mustermann[role_map[role]['bench']]
            try: current_idx = list(rol_isimleri.values()).index(aktif_rol_str)
            except: current_idx = 0
                
            g_profili = st.radio("Radar Görünümü", ["⚖️ Dengeli", "⚔️ IP (Hücum)", "🛡️ OOP (Svn)"], horizontal=True, label_visibility="collapsed", index=current_idx)
            grafik_rol = rol_isimleri[g_profili]
            radar_stats = list(set(list(role_map[role]['weights']["IP (Hücum)"].keys()) + list(role_map[role]['weights']["OOP (Savunma)"].keys()))) if grafik_rol == "Dengeli" else list(role_map[role]['weights'][grafik_rol].keys())
            fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
            fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#161A24')
            for i, p_name in enumerate(selected_all):
                p_row = f_df[f_df['Player'] == p_name].iloc[0]
                r_data = {}
                for stat in radar_stats:
                    t_key = next((k for k in bench.keys() if clean_key(k) == clean_key(stat)), None)
                    if t_key: r_data[stat.replace("/90", "")] = (to_num(p_row.get(stat, 0)) / bench[t_key][3]) * 100
                labels = list(r_data.keys()); angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist() + [0]
                vals = [min(100, v) for v in r_data.values()] + [min(100, list(r_data.values())[0])]
                ax.fill(angles, vals, color=RADAR_COLORS[i], alpha=0.3); ax.plot(angles, vals, color=RADAR_COLORS[i], linewidth=2, marker='o', markersize=5)
            ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=9, color='white', fontweight='bold')
            ax.tick_params(axis='x', pad=15); ax.set_yticks([20, 40, 60, 80, 100]); ax.set_ylim(0, 120); ax.grid(True, color='#333333', linestyle='--')
            plt.tight_layout(pad=2.0); st.pyplot(fig)

    with col_m:
        st.markdown("### 📋 Oyuncu Analiz Masası")
        show_df = f_df[['Player', 'Age', 'Role', 'Rol_Secimi', 'IP_Score', 'OOP_Score', 'Scout_Puanı', 'VFM_Skoru', 'Price_Num']].copy()
        show_df.insert(0, ' Seç', False)
        
        valid_roles = [str(r) for r in ana_mevki_listesi]
        valid_prefs = [str(k) for k in rol_isimleri.keys()]
        
        edited_df = st.data_editor(show_df, column_config={
            " Seç": st.column_config.CheckboxColumn("Seç"),
            "Role": st.column_config.SelectboxColumn("Mevki", options=valid_roles, required=True),
            "Rol_Secimi": st.column_config.SelectboxColumn("🔄 Tercih", options=valid_prefs, required=True),
            "IP_Score": st.column_config.ProgressColumn("⚔️ IP", format="%.1f", min_value=0, max_value=200),
            "OOP_Score": st.column_config.ProgressColumn("🛡️ OOP", format="%.1f", min_value=0, max_value=200),
            "Scout_Puanı": st.column_config.ProgressColumn("⭐ Puan", format="%.1f", min_value=0, max_value=200),
            "VFM_Skoru": st.column_config.NumberColumn("VFM"),
            "Price_Num": st.column_config.NumberColumn("Bonservis (€)", format="%d")
        }, disabled=["Player", "Age", "IP_Score", "OOP_Score", "Scout_Puanı", "VFM_Skoru"], use_container_width=True, hide_index=True, height=450)
        
        selected_for_batch = edited_df[edited_df[' Seç'] == True]['Player'].tolist()
        if selected_for_batch:
            st.info(f"⚡ {len(selected_for_batch)} oyuncu seçildi.")
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
            new_role = col_b1.selectbox("Yeni Mevki:", valid_roles, key="batch_role")
            new_pref = col_b2.selectbox("Yeni Tercih:", valid_prefs, key="batch_pref")
            if col_b3.button("Seçililere Uygula", use_container_width=True):
                for p_name in selected_for_batch:
                    if new_role: st.session_state.player_base_roles[p_name] = new_role
                    if new_pref: st.session_state.player_preferences[p_name] = new_pref
                st.rerun()
        else:
            for idx, row in edited_df.iterrows():
                p_name = row['Player']
                changed = False
                if row['Role'] and row['Role'] in valid_roles:
                    if st.session_state.player_base_roles.get(p_name) != row['Role']:
                        st.session_state.player_base_roles[p_name] = row['Role']; changed = True
                if row['Rol_Secimi'] and row['Rol_Secimi'] in valid_prefs:
                    if st.session_state.player_preferences.get(p_name) != row['Rol_Secimi']:
                        st.session_state.player_preferences[p_name] = row['Rol_Secimi']; changed = True
                if changed: st.rerun()

    st.divider(); st.subheader(f"📊 Karşılaştırmalı Veri Havuzu (Tam Detay)")
    top_dfs = [f_df[f_df['Player'] == p_name] for p_name in selected_all]
    rest_df = f_df[~f_df['Player'].isin(selected_all)].sort_values('Scout_Puanı', ascending=False)
    final_bottom_df = pd.concat(top_dfs + [rest_df]).reset_index(drop=True)
    num_cols = [c for c in df.columns if any(x in c for x in ['/90', '%']) and c != 'NP-xG/90']
    
    pool_config = {s: st.column_config.NumberColumn(s) for s in num_cols}
    pool_config["Player"] = st.column_config.TextColumn("Player", width="large")

    def style_dataframe(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        for i in data.index:
            row = data.loc[i]; p_idx = selected_all.index(row['Player']) if row['Player'] in selected_all else -1
            for col in data.columns:
                if col == 'Player': styles.at[i, col] = f'background-color: #1a2a3a; color: {RADAR_COLORS[p_idx]}; font-weight: bold;' if p_idx != -1 else 'background-color: #161a24; color: #ffffff;'
                elif col in ['Role', 'Rol_Secimi']: styles.at[i, col] = 'background-color: #161a24; color: #aaaaaa;'
                else: styles.at[i, col] = get_mustermann_color(row[col], col, row['Role'])
        return styles

    st.dataframe(final_bottom_df[['Player', 'Role', 'Rol_Secimi'] + num_cols].style.apply(style_dataframe, axis=None), column_config=pool_config, use_container_width=True, hide_index=True)
    st.markdown("<div style='display:flex;gap:15px;justify-content:center;font-weight:bold;margin-top:10px;'><div style='background:#6a0dad;padding:7px 15px;border-radius:4px;color:white;'>🟣 ELITE</div><div style='background:#2e7d32;padding:7px 15px;border-radius:4px;color:white;'>🟢 GOOD</div><div style='background:#fbc02d;padding:7px 15px;border-radius:4px;color:black;'>🟡 AVG</div><div style='background:#c62828;padding:7px 15px;border-radius:4px;color:white;'>🔴 POOR</div></div>", unsafe_allow_html=True)
