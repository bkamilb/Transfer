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

# --- 2. DİNAMİK PROFİLLER ---
rol_isimleri = {
    "⚖️ Dengeli": "Dengeli",
    "⚔️ IP (Hücum)": "IP (Hücum)",
    "🛡️ OOP (Svn)": "OOP (Savunma)"
}

role_map = {
    "Kaleci": {
        "bench": "GK",
        "weights": {
            "Dengeli": {"Poss Won/90": 1.0, "Ps A/90": 0.8},
            "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.2},
            "OOP (Savunma)": {"Poss Won/90": 1.5, "Ps A/90": 0.5}
        }
    },
    "Stoper": {
        "bench": "DEF",
        "weights": {
            "Dengeli": {"Tck A/90": 1.0, "Int/90": 1.0, "Aer A/90": 0.9, "Ps A/90": 0.5},
            "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.2, "Int/90": 0.8, "Tck A/90": 0.5},
            "OOP (Savunma)": {"Tck A/90": 1.5, "Int/90": 1.5, "Aer A/90": 1.2, "Blk/90": 1.0, "Clr/90": 0.8}
        }
    },
    "Bek": {
        "bench": "DEF",
        "weights": {
            "Dengeli": {"xA/90": 1.0, "Tck A/90": 1.0, "Drb/90": 0.9, "Int/90": 0.8},
            "IP (Hücum)": {"xA/90": 1.5, "Drb/90": 1.5, "KP/90": 1.2, "Pr passes/90": 1.0},
            "OOP (Savunma)": {"Tck A/90": 1.5, "Int/90": 1.5, "Poss Won/90": 1.0, "Aer A/90": 0.8}
        }
    },
    "DM": {
        "bench": "MID",
        "weights": {
            "Dengeli": {"Poss Won/90": 1.0, "Int/90": 1.0, "Ps A/90": 0.9, "Tck A/90": 0.8},
            "IP (Hücum)": {"Ps A/90": 1.5, "Pr passes/90": 1.5, "KP/90": 1.0, "Poss Won/90": 0.5},
            "OOP (Savunma)": {"Poss Won/90": 1.5, "Int/90": 1.5, "Tck A/90": 1.2, "Ps A/90": 0.5}
        }
    },
    "AM": {
        "bench": "MID",
        "weights": {
            "Dengeli": {"KP/90": 1.0, "xA/90": 1.0, "Pr passes/90": 0.9, "Shot/90": 0.6},
            "IP (Hücum)": {"KP/90": 1.5, "xA/90": 1.5, "Drb/90": 1.2, "Shot/90": 1.0},
            "OOP (Savunma)": {"Poss Won/90": 1.5, "Int/90": 1.2, "Tck A/90": 1.0, "KP/90": 0.6}
        }
    },
    "Kanat": {
        "bench": "MID",
        "weights": {
            "Dengeli": {"Drb/90": 1.0, "xA/90": 1.0, "KP/90": 0.9, "xG/90": 0.8},
            "IP (Hücum)": {"xG/90": 1.5, "xA/90": 1.5, "Drb/90": 1.2, "Shot/90": 1.2},
            "OOP (Savunma)": {"Poss Won/90": 1.5, "Tck A/90": 1.2, "Drb/90": 0.8, "xA/90": 0.5}
        }
    },
    "Forvet": {
        "bench": "FWD",
        "weights": {
            "Dengeli": {"xG/90": 1.0, "Shot/90": 1.0, "xA/90": 0.6},
            "IP (Hücum)": {"xA/90": 1.5, "KP/90": 1.5, "xG/90": 0.8, "Ps A/90": 1.0},
            "OOP (Savunma)": {"xG/90": 1.5, "Aer A/90": 1.5, "Poss Won/90": 1.2, "Shot/90": 1.2}
        }
    }
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
    bench_key = role_map.get(role, {}).get('bench')
    if not bench_key: return "background-color: #1a1a1a;"

    clean_target = clean_key(stat_name)
    matched_key = next((k for k in mustermann[bench_key].keys() if clean_key(k) == clean_target), None)

    if not matched_key: return "background-color: #1a1a1a; color: #555555;"
    thresh = mustermann[bench_key][matched_key]
    
    if "lost" in matched_key.lower():
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

def get_role(pos):
    pos = str(pos)
    if "GK" in pos: return "Kaleci"
    if any(k in pos for k in ["ST", "S (C)"]): return "Forvet"
    if any(k in pos for k in ["AM (R)", "AM (L)", "M (R)", "M (L)"]): return "Kanat"
    if "AM (C)" in pos: return "AM"
    if "DM" in pos: return "DM"
    if "D (C)" in pos: return "Stoper"
    return "Bek"

# RENK PALETİ (Dengeli / IP / OOP / Kıyas)
RADAR_COLORS = ['#00f2ff', '#ff0055', '#00ff66', '#ffaa00']

# --- 4. STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="Moneyball Ultimate")
st.markdown("""
<style>
    .main { background-color: #0E1117; color: white; }
    .stProgress > div > div > div > div { background-color: #00f2ff; }
    div.row-widget.stRadio > div { flex-direction: row; gap: 15px; justify-content: center; }
</style>
""", unsafe_allow_html=True)

st.title("💰 FM26 Moneyball: Ultimate Decision Maker")

file = st.file_uploader("FM Export CSV'sini Yükle", type="csv")

if file:
    df = pd.read_csv(file, sep=";")
    df['Minutes'] = df['Minutes'].apply(lambda x: x if x > 0 else 1)
    df['Role'] = df['Position'].apply(get_role)
    df['Price_Num'] = df['Transfer Value'].apply(parse_price)
    if 'Tck A' in df.columns: df['Tck A/90'] = (df['Tck A'].apply(to_num) * 90) / df['Minutes']

    if 'player_roles' not in st.session_state:
        st.session_state.player_roles = {}
    df['Rol_Secimi'] = df['Player'].apply(lambda x: st.session_state.player_roles.get(x, "⚖️ Dengeli"))

    st.sidebar.header("🎯 Strateji & Bütçe")
    strategy = st.sidebar.radio("Strateji", ["Kâr Odaklı (Geliştir-Sat)", "Performans (Glory)"])
    min_v, max_v = int(df['Price_Num'].min()), int(df['Price_Num'].max())
    budget = st.sidebar.slider("Bonservis Aralığı", min_value=min_v, max_value=max_v, value=(min_v, max_v), step=100000)

    # --- HESAPLAMA MOTORU ---
    def calc_scores(row):
        config = role_map[row['Role']]
        bench = mustermann.get(config['bench'], {})
        results = {}
        for dict_key, prof_name in [("Dengeli", "Dengeli_Ham"), ("IP (Hücum)", "IP_Ham"), ("OOP (Savunma)", "OOP_Ham")]:
            scores = []
            active_weights = config['weights'].get(dict_key, config['weights']["Dengeli"])
            for s, w in active_weights.items():
                if s in row:
                    clean_s = clean_key(s)
                    target_key = next((k for k in bench.keys() if clean_key(k) == clean_s), None)
                    if target_key: scores.append((to_num(row[s]) / bench[target_key][3]) * 100 * w)
            results[prof_name] = np.mean(scores) if scores else 0
            
        bonus = max(0, (23 - row['Age']) * 5) if strategy == "Kâr Odaklı (Geliştir-Sat)" else 0
        results["IP_Score"] = results["IP_Ham"] + bonus
        results["OOP_Score"] = results["OOP_Ham"] + bonus
        
        secili_rol_key = rol_isimleri[row['Rol_Secimi']]
        if secili_rol_key == "Dengeli": aktif_ham_puan = results["Dengeli_Ham"]
        elif secili_rol_key == "IP (Hücum)": aktif_ham_puan = results["IP_Ham"]
        else: aktif_ham_puan = results["OOP_Ham"]

        results["Scout_Puanı"] = aktif_ham_puan + bonus
        return pd.Series([results["Scout_Puanı"], results["IP_Score"], results["OOP_Score"]])

    df[['Scout_Puanı', 'IP_Score', 'OOP_Score']] = df.apply(calc_scores, axis=1)
    df['VFM_Skoru'] = (df['Scout_Puanı'] / ((df['Price_Num'] / 1000000) + 1)).round(1) 
    f_df = df[(df['Price_Num'] >= budget[0]) & (df['Price_Num'] <= budget[1])].sort_values('Scout_Puanı', ascending=False)

    col_m, col_s = st.columns([2, 1])
    
    with col_s:
        st.subheader("🎯 Scout Kartı & Kıyaslama")
        selected = st.selectbox("Ana Oyuncu:", f_df['Player'].tolist())
        
        avail_compare = [p for p in f_df['Player'].tolist() if p != selected]
        compare_players = st.multiselect("Kıyaslanacak Diğer Oyuncular (Maks 3):", avail_compare, max_selections=3)
        
        selected_all = [selected] + compare_players
        
        p = f_df[f_df['Player'] == selected].iloc[0]
        aktif_rol_str = rol_isimleri[p['Rol_Secimi']]
        
        # Rozetler
        badges = []
        if p['VFM_Skoru'] >= 25.0: badges.append("💎 Kelepir")
        if p['OOP_Score'] >= 80.0: badges.append("🧱 Duvar")
        if p['IP_Score'] >= 80.0: badges.append("🪄 Maestro")
        if p['Scout_Puanı'] >= 85.0: badges.append("⭐ Elit Sınıf")
        if badges:
            st.markdown(f"<div style='margin-bottom: 10px; font-size: 14px;'><b>Rozetler:</b> {' | '.join(badges)}</div>", unsafe_allow_html=True)
        
        # --- ŞIK VE ORTALANMIŞ PUAN & LEJANT ALANI ---
        legend_html = ""
        for i, p_name in enumerate(selected_all):
            legend_html += f"<div style='color: {RADAR_COLORS[i]}; font-weight: bold; margin-top: 3px;'>■ {p_name}</div>"

        # Kıyas Listesi Başlığı
        if len(selected_all) > 1:
            kiyas_baslik = "<div style='color: #aaaaaa; margin-bottom: 5px; border-bottom: 1px solid #333333; padding-bottom: 3px; font-size: 10px; text-transform: uppercase;'>Kıyas Listesi</div>"
        else:
            kiyas_baslik = ""

        metrics_html = f"""<div style='display: flex; background-color:#161a24; padding:15px; border-radius:8px; margin-bottom:15px; border:1px solid #333333; justify-content: space-between; align-items: center;'>
<div style='display: flex; gap: 30px;'>
<div style='text-align: center;'>
<div style='font-size:12px; color:#aaaaaa; margin-bottom: 5px;'>Puan ({aktif_rol_str})</div>
<div style='font-size:28px; font-weight:bold; color:#00f2ff;'>{round(p['Scout_Puanı'], 1)}</div>
</div>
<div style='text-align: center;'>
<div style='font-size:12px; color:#aaaaaa; margin-bottom: 5px;'>VFM Skoru</div>
<div style='font-size:28px; font-weight:bold; color:#ff0055;'>{p['VFM_Skoru']}</div>
</div>
</div>
<div style='text-align: left; font-size: 12px; background-color: #0e1117; padding: 10px; border-radius: 5px; border: 1px solid #222222; min-width: 140px;'>
{kiyas_baslik}
{legend_html}
</div>
</div>"""
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Radar Ayarları
        role = p['Role']
        bench = mustermann[role_map[role]['bench']]
        
        st.markdown("<div style='text-align: center; color: #aaaaaa; font-size: 14px; margin-bottom: 5px;'>Radar Görünümü</div>", unsafe_allow_html=True)
        g_profili = st.radio("Radar Görünümü", ["⚖️ Dengeli", "⚔️ IP (Hücum)", "🛡️ OOP (Svn)"], horizontal=True, label_visibility="collapsed", index=list(rol_isimleri.values()).index(aktif_rol_str))
        grafik_aktif_rol = rol_isimleri[g_profili]

        if grafik_aktif_rol == "Dengeli":
            ip_k = list(role_map[role]['weights']["IP (Hücum)"].keys())
            oop_k = list(role_map[role]['weights']["OOP (Savunma)"].keys())
            radar_stats = list(set(ip_k + oop_k))
        else:
            radar_stats = list(role_map[role]['weights'][grafik_aktif_rol].keys())

        # Çoklu Radar Çizimi
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
        fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#161A24')
        
        for i, p_name in enumerate(selected_all):
            p_row = f_df[f_df['Player'] == p_name].iloc[0]
            r_data = {}
            for stat in radar_stats:
                clean_s = clean_key(stat)
                target_key = next((k for k in bench.keys() if clean_key(k) == clean_s), None)
                if target_key:
                    r_data[stat.replace("/90", "").replace(" %", "")] = (to_num(p_row.get(stat, 0)) / bench[target_key][3]) * 100
            
            labels = list(r_data.keys())
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]
            vals = [min(100, v) for v in r_data.values()] + [min(100, list(r_data.values())[0])]
            
            alpha_val = 0.3 if i == 0 else 0.2
            marker_style = 'o' if i == 0 else 'X'
            
            ax.fill(angles, vals, color=RADAR_COLORS[i], alpha=alpha_val)
            ax.plot(angles, vals, color=RADAR_COLORS[i], linewidth=2, marker=marker_style, markersize=5)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=9, color='white', fontweight='bold')
        
        # RADAR YAZILARI İÇİN ÇÖZÜM: Yazıları grafikten uzaklaştırdık
        ax.tick_params(axis='x', pad=15) 
        
        ax.set_ylim(0, 100); ax.grid(True, color='#333333', linestyle='--')
        
        # Grafik kenarlarını biraz genişletelim ki itilen yazılar kesilmesin
        plt.tight_layout(pad=2.0)
        
        st.pyplot(fig)

    with col_m:
        st.markdown("### 📋 Oyuncu Analiz Masası")
        
        show_df = f_df[['Player', 'Age', 'Role', 'IP_Score', 'OOP_Score', 'Rol_Secimi', 'Scout_Puanı', 'VFM_Skoru', 'Price_Num']].copy()
        show_df.rename(columns={'Price_Num': 'Bonservis (€)'}, inplace=True)
        
        edited_df = st.data_editor(
            show_df,
            column_config={
                "IP_Score": st.column_config.ProgressColumn("⚔️ IP", format="%.1f", min_value=0, max_value=100),
                "OOP_Score": st.column_config.ProgressColumn("🛡️ OOP", format="%.1f", min_value=0, max_value=100),
                "Rol_Secimi": st.column_config.SelectboxColumn("🔄 Tercih", options=list(rol_isimleri.keys()), required=True, width="medium"),
                "Scout_Puanı": st.column_config.ProgressColumn("⭐ Puan", format="%.1f", min_value=0, max_value=100),
                "VFM_Skoru": st.column_config.NumberColumn("VFM", format="%.1f"),
                "Bonservis (€)": st.column_config.NumberColumn(format="%d €"),
            },
            disabled=["Player", "Age", "Role", "IP_Score", "OOP_Score", "Scout_Puanı", "VFM_Skoru", "Bonservis (€)"],
            use_container_width=True, hide_index=True, height=450
        )

        changes = False
        for idx, row in edited_df.iterrows():
            player_name = row['Player']
            new_role = row['Rol_Secimi']
            if st.session_state.player_roles.get(player_name, "⚖️ Dengeli") != new_role:
                st.session_state.player_roles[player_name] = new_role
                changes = True
        if changes:
            st.rerun()

        # --- OYUN İÇİ PAZAR MATRİSİ (PUAN vs VFM) ---
        st.markdown("---")
        st.markdown("### 🌌 Oyuncu Pazar Matrisi (Puan & VFM)")
        st.markdown("<span style='color:#aaaaaa; font-size:13px;'>Sağ üst bölge elit ve kelepir oyuncuları (Yüksek Puan, Yüksek VFM) temsil eder. Renkli kutularla isimler eşleştirilmiştir.</span>", unsafe_allow_html=True)
        
        fig_scatter = go.Figure()
        
        diger_df = f_df[~f_df['Player'].isin(selected_all)]
        fig_scatter.add_trace(go.Scatter(
            x=diger_df['Scout_Puanı'], y=diger_df['VFM_Skoru'],
            mode='markers',
            marker=dict(color='white', size=7, opacity=0.3),
            text=diger_df['Player'],
            hovertemplate="<b>%{text}</b><br>Puan: %{x:.1f}<br>VFM: %{y:.1f}<extra></extra>",
            name='Diğer'
        ))
        
        for i, p_name in enumerate(selected_all):
            p_df = f_df[f_df['Player'] == p_name]
            if not p_df.empty:
                fig_scatter.add_trace(go.Scatter(
                    x=p_df['Scout_Puanı'], y=p_df['VFM_Skoru'],
                    mode='markers',
                    marker=dict(color=RADAR_COLORS[i], size=16, symbol='diamond', line=dict(color='#ffffff', width=1.5)),
                    text=p_df['Player'],
                    hovertemplate="<b>%{text}</b><br>Puan: %{x:.1f}<br>VFM: %{y:.1f}<extra></extra>",
                    name=p_name
                ))
                
        x_mid = f_df['Scout_Puanı'].mean()
        y_mid = f_df['VFM_Skoru'].mean()
        fig_scatter.add_vline(x=x_mid, line_dash="dash", line_color="rgba(255, 255, 255, 0.4)", line_width=2)
        fig_scatter.add_hline(y=y_mid, line_dash="dash", line_color="rgba(255, 255, 255, 0.4)", line_width=2)
        
        fig_scatter.add_annotation(x=1, y=1, xref="paper", yref="paper", text="Elit & Kelepir", showarrow=False, font=dict(color="#00ff66", size=11), xanchor="right", yanchor="bottom")
        fig_scatter.add_annotation(x=0, y=0, xref="paper", yref="paper", text="Zayıf & Pahalı", showarrow=False, font=dict(color="#ff0055", size=11), xanchor="left", yanchor="top")
        
        fig_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Scout Puanı",
            yaxis_title="VFM Skoru",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- ALT TABLO (SEÇİLİLER EN ÜSTTE VE RENKLİ) ---
    st.divider()
    st.subheader(f"📊 Karşılaştırmalı Veri Havuzu (Tam Detay)")
    
    top_dfs = [f_df[f_df['Player'] == p_name] for p_name in selected_all]
    rest_df = f_df[~f_df['Player'].isin(selected_all)].sort_values('Scout_Puanı', ascending=False)
    
    # BULUT SUNUCUSU İÇİN KESİN ÇÖZÜM: İndeksler sıfırlandı
    final_bottom_df = pd.concat(top_dfs + [rest_df]).reset_index(drop=True)
    
    num_cols = [c for c in df.columns if any(x in c for x in ['/90', '%'])]
    deep_cols = ['Player', 'Role', 'Rol_Secimi'] + num_cols
    
    def apply_final_styling(row):
        styles = []
        for col in row.index:
            if col == 'Player':
                if row['Player'] in selected_all:
                    idx = selected_all.index(row['Player'])
                    c = RADAR_COLORS[idx]
                    # Streamlit Cloud uyumu: Sadece background-color ve color bırakıldı
                    styles.append(f'background-color: #1a2a3a; color: {c};')
                else:
                    styles.append('background-color: #161a24; color: #ffffff;')
            elif col in ['Role', 'Rol_Secimi']:
                styles.append('background-color: #161a24; color: #aaaaaa;')
            else:
                styles.append(get_mustermann_color(row[col], col, row['Role']))
        return styles

    # BULUT SUNUCUSU İÇİN KESİN ÇÖZÜM 2: hide_index=True eklendi
    st.dataframe(final_bottom_df[deep_cols].style.apply(apply_final_styling, axis=1), use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div style="display: flex; gap: 15px; justify-content: center; margin-top: 15px; font-weight: bold;">
        <div style="background-color: #6a0dad; padding: 7px 15px; border-radius: 4px; color: white;">🟣 ELITE</div>
        <div style="background-color: #2e7d32; padding: 7px 15px; border-radius: 4px; color: white;">🟢 GOOD</div>
        <div style="background-color: #fbc02d; padding: 7px 15px; border-radius: 4px; color: black;">🟡 AVG</div>
        <div style="background-color: #c62828; padding: 7px 15px; border-radius: 4px; color: white;">🔴 POOR</div>
    </div>
    """, unsafe_allow_html=True)
