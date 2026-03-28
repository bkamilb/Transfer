import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# --- 1. MUSTERMANN ELITE BARAJLAR (PDF BAZLI) ---
mustermann = {
    "GK": {"Poss Won/90": 8.53, "Ps A/90": 26.06, "Pr passes/90": 0.98, "Poss Lost/90": 2.35},
    "DEF": {"Tck A/90": 3.48, "Int/90": 3.12, "Aer A/90": 5.35, "Hdr %": 70.7, "Blk/90": 0.75, "Pr passes/90": 7.95, "Ps A/90": 69.88},
    "MID": {"Poss Won/90": 8.53, "KP/90": 2.08, "xA/90": 0.19, "Ps A/90": 68.83, "Pr passes/90": 6.91, "Int/90": 2.86},
    "FWD": {"xG/90": 0.40, "Shot/90": 2.81, "Drb/90": 5.62, "xA/90": 0.26, "KP/90": 2.31}
}

# --- 2. 7 MEVKİ KATSAYILARI ---
role_map = {
    "Kaleci": {"bench": "GK", "weights": {"Poss Won/90": 1.0, "Ps A/90": 0.8, "Pr passes/90": 0.8}},
    "Stoper": {"bench": "DEF", "weights": {"Tck A/90": 1.0, "Int/90": 1.0, "Aer A/90": 0.9, "Hdr %": 0.8, "Blk/90": 0.7}},
    "Bek": {"bench": "DEF", "weights": {"xA/90": 1.0, "Tck A/90": 1.0, "Drb/90": 0.9, "Pr passes/90": 0.8}},
    "DM": {"bench": "MID", "weights": {"Poss Won/90": 1.0, "Int/90": 1.0, "Ps A/90": 0.9, "Pr passes/90": 0.8}},
    "AM": {"bench": "MID", "weights": {"KP/90": 1.0, "xA/90": 1.0, "Pr passes/90": 0.9}},
    "Kanat": {"bench": "MID", "weights": {"Drb/90": 1.0, "xA/90": 1.0, "KP/90": 0.9}},
    "Forvet": {"bench": "FWD", "weights": {"xG/90": 1.0, "Shot/90": 1.0, "xA/90": 0.6}}
}

# --- 3. YARDIMCI FONKSİYONLAR ---
def parse_price(v):
    if pd.isna(v) or v == "" or v == "-": return 0.0
    v = str(v).replace('€', '').replace(' ', '').strip()
    if '-' in v: v = v.split('-')[-1].strip() # Maksimum fiyatı al
    mult = 1.0
    if 'M' in v: mult = 1000000.0; v = v.replace('M', '')
    elif 'K' in v: mult = 1000.0; v = v.replace('K', '')
    try:
        v = v.replace(',', '.'); v = re.sub(r'[^\d.]', '', v)
        return float(v) * mult
    except: return 0.0

def format_curr(val):
    return f"{int(val):,}".replace(",", ".") + " €"

def to_num(val):
    try:
        if isinstance(val, str): val = val.replace('%', '').replace(',', '.').strip()
        v = pd.to_numeric(val, errors='coerce')
        return float(v) if not np.isnan(v) else 0.0
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

def get_mustermann_color(val, stat, role):
    bench_key = role_map[role]['bench']
    if bench_key not in mustermann or stat not in mustermann[bench_key]: return ""
    elite = mustermann[bench_key][stat]
    ratio = (val / elite) if elite > 0 else 0
    if ratio >= 1.0: return "background-color: #6a0dad; color: white;" 
    if ratio >= 0.75: return "background-color: #2e7d32; color: white;" 
    if ratio >= 0.5: return "background-color: #fbc02d; color: black;" 
    return "background-color: #c62828; color: white;" 

# --- 4. STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="Moneyball Pro Final")
st.markdown("<style>.main { background-color: #0E1117; color: white; }</style>", unsafe_allow_html=True)

st.title("💰 FM26 Moneyball: Final Decision Tool")

file = st.file_uploader("FM Export CSV'sini Yükle", type="csv")

if file:
    df = pd.read_csv(file, sep=";")
    df['Minutes'] = df['Minutes'].apply(lambda x: x if x > 0 else 1)
    df['Role'] = df['Position'].apply(get_role)
    df['Numeric_Value'] = df['Transfer Value'].apply(parse_price)
    df['Fiyat_Okunaklı'] = df['Numeric_Value'].apply(format_curr)
    if 'Tck A' in df.columns: df['Tck A/90'] = (df['Tck A'].apply(to_num) * 90) / df['Minutes']

    # --- SIDEBAR FİLTRELER ---
    st.sidebar.header("🎯 Strateji & Bütçe")
    strategy = st.sidebar.radio("Transfer Amacı", ["Kâr Odaklı (Geliştir-Sat)", "Performans (Glory)"])
    
    min_v = int(df['Numeric_Value'].min())
    max_v = int(df['Numeric_Value'].max())
    
    budget_range = st.sidebar.slider(
        "Bonservis Aralığı (Maks. Fiyat Bazlı)",
        min_value=min_v, max_value=max_v,
        value=(min_v, max_v), step=100000
    )
    st.sidebar.info(f"Filtre: {format_curr(budget_range[0])} - {format_curr(budget_range[1])}")

    # --- SCORING ENGINE ---
    def calculate_score(row):
        config = role_map[row['Role']]
        bench_vals = mustermann[config['bench']]
        scores = [(to_num(row[s]) / bench_vals.get(s, 1.0)) * 100 * w for s, w in config['weights'].items() if s in row]
        base = np.mean(scores) if scores else 0
        if strategy == "Kâr Odaklı (Geliştir-Sat)":
            return base + max(0, (23 - row['Age']) * 5)
        return base

    df['Scout_Score'] = df.apply(calculate_score, axis=1)
    filtered_df = df[(df['Numeric_Value'] >= budget_range[0]) & (df['Numeric_Value'] <= budget_range[1])].sort_values('Scout_Score', ascending=False)

    col_main, col_radar = st.columns([2, 1])

    with col_main:
        st.subheader("📋 Scouting Listesi")
        st.dataframe(filtered_df[['Player', 'Age', 'Role', 'Scout_Score', 'Fiyat_Okunaklı']], use_container_width=True, height=450)

    with col_radar:
        st.subheader("🎯 Mevki Analizi")
        selected_player = st.selectbox("Oyuncu Seç:", filtered_df['Player'].tolist())
        p = filtered_df[filtered_df['Player'] == selected_player].iloc[0]
        
        # Radar Grafik (Dark Neon)
        role = p['Role']
        if role == "Stoper":
            radar_data = {"Savunma": (to_num(p.get('Int/90',0))/3.12 + to_num(p.get('Tck A/90',0))/3.48)*50, "Hava": (to_num(p.get('Aer A/90',0))/5.35 + to_num(p.get('Hdr %',0))/70.7)*50, "Pas": (to_num(p.get('Ps A/90',0))/69.8)*100, "Sertlik": (to_num(p.get('Tck A/90',0))/3.48)*100}
        elif role == "Forvet":
            radar_data = {"Bitiricilik": (to_num(p.get('xG/90',0))/0.40)*100, "Şut": (to_num(p.get('Shot/90',0))/2.81)*100, "Üretim": (to_num(p.get('xA/90',0))/0.26)*100, "Çalım": (to_num(p.get('Drb/90',0))/5.62)*100}
        else:
            radar_data = {"Defans": (to_num(p.get('Int/90',0))/2.86 + to_num(p.get('Poss Won/90',0))/8.53)*50, "Yaratıcılık": (to_num(p.get('xA/90',0))/0.19 + to_num(p.get('KP/90',0))/2.08)*50, "Dribbling": (to_num(p.get('Drb/90',0))/1.56)*100, "Pas": (to_num(p.get('Ps A/90',0))/68.8)*100}

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#161A24')
        labels = list(radar_data.keys()); values = [min(100, v) for v in radar_data.values()]
        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]; angles += angles[:1]
        ax.fill(angles, values, color='#00f2ff', alpha=0.3)
        ax.plot(angles, values, color='#00f2ff', linewidth=3, marker='o', markersize=7, markerfacecolor='white')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=10, color='#00f2ff', fontweight='bold')
        ax.set_ylim(0, 100); ax.grid(True, color='#333', linestyle='--')
        st.pyplot(fig)
        st.write(f"**Değer (Maks):** {p['Fiyat_Okunaklı']}")

    # --- GENİŞ ALT PANEL ---
    st.divider()
    st.subheader(f"📊 Veritabanı (Mustermann Renkleri & Tam Liste)")
    deep_cols = ['Player', 'Role', 'Fiyat_Okunaklı'] + [c for c in df.columns if any(x in c for x in ['/90', '%'])]
    
    def highlight_and_color_final(row):
        style = [get_mustermann_color(row[c], c, row['Role']) if c in mustermann.get(role_map[row['Role']]['bench'], {}) else '' for c in row.index]
        if row['Player'] == selected_player:
            return ['background-color: #1a2a3a; border: 2px solid #00f2ff; color: #00f2ff; font-weight: bold;' for _ in row]
        return style

    # Height kaldırıldı, liste tam görünecek
    st.dataframe(filtered_df[deep_cols].style.apply(highlight_and_color_final, axis=1), use_container_width=True)

    st.markdown("""
    <div style="display: flex; gap: 15px; justify-content: center; margin-top: 15px; font-weight: bold;">
        <div style="background-color: #6a0dad; padding: 7px 15px; border-radius: 4px; color: white;">🟣 ELITE</div>
        <div style="background-color: #2e7d32; padding: 7px 15px; border-radius: 4px; color: white;">🟢 GOOD</div>
        <div style="background-color: #fbc02d; padding: 7px 15px; border-radius: 4px; color: black;">🟡 AVG</div>
        <div style="background-color: #c62828; padding: 7px 15px; border-radius: 4px; color: white;">🔴 POOR</div>
    </div>
    <p style="text-align: center; color: #00f2ff; margin-top: 5px;">Neon Mavi Çerçeve: Seçili Oyuncu</p>
    """, unsafe_allow_html=True)
