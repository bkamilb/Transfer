import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

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

role_map = {
    "Kaleci": {"bench": "GK", "weights": {"Poss Won/90": 1.0, "Ps A/90": 0.8}},
    "Stoper": {"bench": "DEF", "weights": {"Tck A/90": 1.0, "Int/90": 1.0, "Aer A/90": 0.9}},
    "Bek": {"bench": "DEF", "weights": {"xA/90": 1.0, "Tck A/90": 1.0, "Drb/90": 0.9}},
    "DM": {"bench": "MID", "weights": {"Poss Won/90": 1.0, "Int/90": 1.0, "Ps A/90": 0.9}},
    "AM": {"bench": "MID", "weights": {"KP/90": 1.0, "xA/90": 1.0, "Pr passes/90": 0.9}},
    "Kanat": {"bench": "MID", "weights": {"Drb/90": 1.0, "xA/90": 1.0, "KP/90": 0.9}},
    "Forvet": {"bench": "FWD", "weights": {"xG/90": 1.0, "Shot/90": 1.0, "xA/90": 0.6}}
}

# --- 2. FONKSİYONLAR ---
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

    if not matched_key: return "background-color: #1a1a1a; color: #555;"
    
    thresh = mustermann[bench_key][matched_key]
    if "lost" in matched_key.lower():
        if v <= thresh[3]: return "background-color: #6a0dad; color: white;" 
        if v <= thresh[2]: return "background-color: #2e7d32; color: white;" 
        if v <= thresh[1]: return "background-color: #fbc02d; color: black;" 
        return "background-color: #c62828; color: white;" 
    
    if v >= thresh[3]: return "background-color: #6a0dad; color: white;" 
    if v >= thresh[2]: return "background-color: #2e7d32; color: white;" 
    if v >= thresh[1]: return "background-color: #fbc02d; color: black;" 
    return "background-color: #c62828; color: white;" 

def parse_price(v):
    if pd.isna(v) or v == "" or v == "-": return 0.0
    v = str(v).replace('€','').replace(' ','').strip()
    if '-' in v: v = v.split('-')[-1].strip()
    mult = 1.0
    if 'M' in v: mult = 1000000.0; v = v.replace('M', '')
    elif 'K' in v: mult = 1000.0; v = v.replace('K', '')
    try:
        return float(re.sub(r'[^\d.]', '', v.replace(',', '.'))) * mult
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

# --- 3. STREAMLIT UI & KOZMETİK ---
st.set_page_config(layout="wide", page_title="Moneyball Pro v11.1")
st.markdown("""
<style>
    .main { background-color: #0E1117; color: white; }
    .stProgress > div > div > div > div { background-color: #00f2ff; }
</style>
""", unsafe_allow_html=True)

st.title("💰 FM26 Moneyball: Ultimate Scout")

file = st.file_uploader("FM Export CSV'sini Yükle", type="csv")

if file:
    df = pd.read_csv(file, sep=";")
    df['Minutes'] = df['Minutes'].apply(lambda x: x if x > 0 else 1)
    df['Role'] = df['Position'].apply(get_role)
    df['Price_Num'] = df['Transfer Value'].apply(parse_price)
    
    if 'Tck A' in df.columns: df['Tck A/90'] = (df['Tck A'].apply(to_num) * 90) / df['Minutes']

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Strateji & Bütçe")
    strategy = st.sidebar.radio("Strateji", ["Kâr Odaklı (Geliştir-Sat)", "Performans (Glory)"])
    min_v, max_v = int(df['Price_Num'].min()), int(df['Price_Num'].max())
    budget = st.sidebar.slider("Bonservis Aralığı", min_value=min_v, max_value=max_v, value=(min_v, max_v), step=100000)

    # --- SCORING & VFM ---
    def calculate_score(row):
        config = role_map[row['Role']]
        bench = mustermann.get(config['bench'], {})
        scores = []
        for s, w in config['weights'].items():
            if s in row:
                clean_s = clean_key(s)
                target_key = next((k for k in bench.keys() if clean_key(k) == clean_s), None)
                if target_key: scores.append((to_num(row[s]) / bench[target_key][3]) * 100 * w)
        base = np.mean(scores) if scores else 0
        return base + (max(0, (23 - row['Age']) * 5) if strategy == "Kâr Odaklı (Geliştir-Sat)" else 0)

    df['Scout_Score'] = df.apply(calculate_score, axis=1)
    df['VFM_Skoru'] = (df['Scout_Score'] / ((df['Price_Num'] / 1000000) + 1)).round(1) 
    
    f_df = df[(df['Price_Num'] >= budget[0]) & (df['Price_Num'] <= budget[1])].sort_values('Scout_Score', ascending=False)

    col_m, col_s = st.columns([2, 1])
    
    with col_m:
        st.subheader("📋 Scouting Listesi")
        selected = st.selectbox("Oyuncu Seç (Tabloda Parlayacak):", f_df['Player'].tolist())
        
        # GÖRÜNTÜLENECEK TABLOYU HAZIRLA (Fiyat artık sayısal olarak tutulup arayüzde formatlanıyor)
        show_top_df = f_df[['Player', 'Age', 'Role', 'Scout_Score', 'VFM_Skoru', 'Price_Num']].copy()
        show_top_df.rename(columns={'Price_Num': 'Bonservis (€)'}, inplace=True)
        
        def highlight_top(row):
            if row['Player'] == selected:
                return ['background-color: #1a2a3a; border-left: 3px solid #00f2ff; color: #00f2ff; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        st.dataframe(
            show_top_df.style
            .apply(highlight_top, axis=1)
            .format({'Bonservis (€)': lambda x: f"{int(x):,}".replace(",", ".") + " €"}), # Sıralamayı bozmadan görselliği ekledik
            use_container_width=True, 
            height=400
        )

    with col_s:
        st.subheader("🎯 Seçili Analiz")
        p = f_df[f_df['Player'] == selected].iloc[0]
        
        # INFO BUTONLARI EKLENDİ (Tooltip özelliği)
        c1, c2 = st.columns(2)
        c1.metric(
            "Final Puanı", 
            f"{round(p['Scout_Score'], 1)}", 
            help="Oyuncunun mevkisine özel Mustermann katsayılarına göre hesaplanan 100 üzerinden saf yetenek ve verimlilik puanı."
        )
        c2.metric(
            "Fiyat/Performans (VFM)", 
            f"{p['VFM_Skoru']}", 
            help="Final Puanı / Milyon Euro. Ödediğiniz her 1 Milyon € başına satın aldığınız yetenek miktarını gösterir. Yüksek olması maliyet etkinliğini kanıtlar."
        )

        # Radar Metrikleri
        role = p['Role']
        bench = mustermann[role_map[role]['bench']]
        if role == "Stoper":
            r_data = {"Savunma": (to_num(p.get('Int/90',0))/bench['Int/90'][3])*100, "Hava": (to_num(p.get('Aer A/90',0))/bench['Aer A/90'][3])*100, "Pas": (to_num(p.get('Ps A/90',0))/bench['Ps A/90'][3])*100, "Sertlik": (to_num(p.get('Tck A/90',0))/bench['Tck A/90'][3])*100}
        elif role == "Forvet":
            r_data = {"Bitiricilik": (to_num(p.get('xG/90',0))/bench['xG/90'][3])*100, "Şut": (to_num(p.get('Shot/90',0))/bench['Shot/90'][3])*100, "Üretim": (to_num(p.get('xA/90',0))/bench['xA/90'][3])*100, "Çalım": (to_num(p.get('Drb/90',0))/bench['Drb/90'][3])*100}
        else:
            r_data = {"Defans": (to_num(p.get('Int/90',0))/bench['Int/90'][3])*100, "Yaratıcılık": (to_num(p.get('xA/90',0))/bench['xA/90'][3])*100, "Top Taşıma": (to_num(p.get('Drb/90',0))/bench['Drb/90'][3])*100, "Pas Trafiği": (to_num(p.get('Ps A/90',0))/bench['Ps A/90'][3])*100}

        # Radar Grafiği
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
        fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#161A24')
        labels = list(r_data.keys()); values = [min(100, v) for v in r_data.values()]
        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]; angles += angles[:1]
        ax.fill(angles, values, color='#00f2ff', alpha=0.3)
        ax.plot(angles, values, color='#00f2ff', linewidth=2, marker='o', markersize=5, markerfacecolor='white')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=9, color='#00f2ff', fontweight='bold')
        ax.set_ylim(0, 100); ax.grid(True, color='#333', linestyle='--')
        st.pyplot(fig)
        
        st.write("---")
        for key, val in r_data.items():
            st.markdown(f"<div style='font-size:12px; margin-bottom:-10px;'>{key}: <b>{int(min(100, val))}</b>/100</div>", unsafe_allow_html=True)
            st.progress(int(min(100, val)))

    # --- GENİŞ ALT PANEL ---
    st.divider()
    st.subheader(f"📊 Karşılaştırmalı Veri Havuzu (Tam Renkli)")
    
    num_cols = [c for c in df.columns if any(x in c for x in ['/90', '%', 'Scout_Score'])]
    deep_cols = ['Player', 'Role'] + num_cols
    
    def apply_final_styling(row):
        styles = []
        for col in row.index:
            if col == 'Player' and row['Player'] == selected:
                styles.append('background-color: #1a2a3a; border: 2.5px solid #00f2ff; color: #00f2ff; font-weight: bold;')
            else:
                styles.append(get_mustermann_color(row[col], col, row['Role']))
        return styles

    st.dataframe(f_df[deep_cols].style.apply(apply_final_styling, axis=1), use_container_width=True)
    
    st.markdown("""
    <div style="display: flex; gap: 15px; justify-content: center; margin-top: 15px; font-weight: bold;">
        <div style="background-color: #6a0dad; padding: 7px 15px; border-radius: 4px; color: white;">🟣 ELITE</div>
        <div style="background-color: #2e7d32; padding: 7px 15px; border-radius: 4px; color: white;">🟢 GOOD</div>
        <div style="background-color: #fbc02d; padding: 7px 15px; border-radius: 4px; color: black;">🟡 AVG</div>
        <div style="background-color: #c62828; padding: 7px 15px; border-radius: 4px; color: white;">🔴 POOR</div>
    </div>
    """, unsafe_allow_html=True)
