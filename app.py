import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import struct
import math
import json
import os
import requests
import re
from PIL import Image
import datetime

# -----------------------------------------------------------------------------
# 1. ページ基本設定 (ノートPC表示最適化)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CIRCUIT ANALYZE ver1.0",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. 多言語辞書 (日本語 ⇔ English 完全対応)
# -----------------------------------------------------------------------------
LANG_DICT = {
    "日本語": {
        "title_sub": "高精度テレメトリー ＆ ダイナミクス比較解析システム",
        "theme_select": "システムUIテーマ選択",
        "config_assets": "設定 ＆ アセット読み込み",
        "saved_config": "保存済み設定ファイル (.json)",
        "config_loaded": "設定ファイルを読み込みました",
        "config_failed": "設定ファイルのパースに失敗しました",
        "telemetry_file": "走行データ (複数選択可: .bnx4 / .dtb / .csv)",
        "circuit_pth": "🏁 コース形状データ (.pth)",
        "circuit_bg": "サーキット背景画像 (.png / .jpg)",
        "geojson_file": "国土地理院/GeoJSON コース幅データ",
        "render_style": "描画背景タイプ",
        "track_width": "想定コース幅 (ピクセル)",
        "track_opacity": "想定コース透明度",
        "track_shift_x": "コース位置 X (東西シフト)",
        "track_shift_y": "コース位置 Y (南北シフト)",
        "north_rotation": "北基準回転角度 (°)",
        "bg_shift": "コース図面画像の位置・比率調整 (整数単位)",
        "offset_x": "位置 X (東西)",
        "offset_y": "位置 Y (南北)",
        "scale_x": "横幅倍率 (Scale X)",
        "scale_y": "縦幅倍率 (Scale Y)",
        "opacity": "透明度",
        "min_pts": "1周の最低データ点数",
        "auto_gps": "🎯 コース全体基準 GPS高精度ズレ補正",
        "select_session": "解析対象の走行グループを選択:",
        "visual_start": "スタート位置を目視で調整する",
        "start_slider": "コース上のサンプルポイント位置",
        "filter_laps": "🗑️ 不要なLAPを選択して除外（削除）:",
        "compare_laps": "📊 比較ラップ選択 (最大10周まで選択可能)",
        "export_btn": "💾 現在のコース・名前設定をファイルに保存する",
        "braking_points": "🔴🟢 強調ブレーキ/アクセルON ポイント表示",
        "trace_axis": "グラフ比較軸:",
        "replay_speed": "同期再生速度:",
        "main_analysis": "🏁 メイン走行ライン解析",
        "start_time": "開始時刻",
        "hud_title": "選択ラップ HUD & 傾きインジケーター",
        "sub_compare": "📺 併設比較周",
        "bank_angle": "🏍️ バイク傾き (bike.png バンク角)",
        "seek_time": "再生シーン連動 (各ラップバンク角同期)",
        "speed_traces": "📈 車速 ＆ アクセル/ブレーキ状態トレース",
        "drop_info": "左側のサイドバーから .bnx4 / .dtb / .csv ログファイルをドロップしてください。",
        "dist_m": "走行距離 (m)",
        "time_s": "経過時間 (秒)",
        "speed_kmh": "車速 (km/h)",
        "lean_deg": "バンク角"
    },
    "English": {
        "title_sub": "HIGH-PRECISION TELEMETRY & DYNAMICS ANALYZER",
        "theme_select": "SYSTEM THEME SELECT",
        "config_assets": "CONFIG & ASSETS",
        "saved_config": "Saved Config (.json)",
        "config_loaded": "Config Loaded Successfully",
        "config_failed": "Failed to Parse Config File",
        "telemetry_file": "Telemetry Data (Multiple: .bnx4/.dtb/.csv)",
        "circuit_pth": "🏁 Circuit Path Data (.pth)",
        "circuit_bg": "Circuit Track Image (.png / .jpg)",
        "geojson_file": "GeoJSON Track Width File",
        "render_style": "Track Render Style",
        "track_width": "Track Width (px)",
        "track_opacity": "Track Opacity",
        "track_shift_x": "Track Shift X (East-West)",
        "track_shift_y": "Track Shift Y (North-South)",
        "north_rotation": "North Align Rotation (°)",
        "bg_shift": "Image Offset & Scale Adjust (Integer)",
        "offset_x": "Offset X (East-West)",
        "offset_y": "Offset Y (North-South)",
        "scale_x": "Scale X",
        "scale_y": "Scale Y",
        "opacity": "Opacity",
        "min_pts": "Min Lap Points",
        "auto_gps": "Whole Track Global Alignment",
        "select_session": "Select Session:",
        "visual_start": "Visual Start Line Adjust",
        "start_slider": "Start Line Sample Point",
        "filter_laps": "🗑️ Select Unwanted Laps to Exclude (Remove):",
        "compare_laps": "SELECT LAPS TO COMPARE (MAX 10 LAPS)",
        "export_btn": "EXPORT CONFIG FILE (.JSON)",
        "braking_points": "Enhanced Braking Points (🔴)",
        "trace_axis": "Trace Axis:",
        "replay_speed": "Replay Speed:",
        "main_analysis": "MAIN LAP TRACE ANALYSIS",
        "start_time": "Start Time",
        "hud_title": "SELECT LAPS HUD & LEAN SENSOR",
        "sub_compare": "SUB COMPARE",
        "bank_angle": "DYNAMICS (BANK ANGLE)",
        "seek_time": "SEEK TIME (LEAN SENSOR)",
        "speed_traces": "TELEMETRY SPEED TRACES",
        "drop_info": "DROP .BNX4, .DTB, OR .CSV TELEMETRY FILES FROM SIDEBAR.",
        "dist_m": "Distance (m)",
        "time_s": "Time (s)",
        "speed_kmh": "Speed (km/h)",
        "lean_deg": "Lean"
    }
}

THEMES = {
    "Cyber Matrix 2.0": {
        "bg_app": "#040806", "bg_panel": "#09120e", "bg_card": "#0d1a14",
        "border": "#1b3a2b", "text": "#e2e8f0", "accent": "#00ff66", "best": "#00ff66",
        "plot_bg": "#06110b", "grid": "#13281c",
        "colors": ["#00f2fe", "#ff2a5f", "#00ff88", "#ffb703", "#a855f7", "#00ff66", "#f43f5e", "#06b6d4", "#eab308", "#ec4899"]
    },
    "F1 Telemetry Carbon": {
        "bg_app": "#08080a", "bg_panel": "#101014", "bg_card": "#16161c",
        "border": "#232332", "text": "#f1f5f9", "accent": "#00f2fe", "best": "#00ff88",
        "plot_bg": "#0a0a0f", "grid": "#1a1a28",
        "colors": ["#00f2fe", "#ff2a5f", "#00ff88", "#ffb703", "#e0e6ed", "#a855f7", "#f43f5e", "#38bdf8", "#facc15", "#c084fc"]
    }
}

def ceil_2(val):
    if pd.isna(val) or val is None: return 0.0
    return math.ceil(val * 100.0) / 100.0

def parse_pth_course_file(file_bytes):
    """コース形状定義ファイル (.pth) 専用パースエンジン"""
    paths = []
    try:
        content = file_bytes.decode('utf-8', errors='ignore')
        path_blocks = re.findall(r'<path>(.*?)</path>', content, re.DOTALL)
        if path_blocks:
            for block in path_blocks:
                pts = []
                for line in block.strip().splitlines():
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        try:
                            lon, lat = float(parts[0]), float(parts[1])
                            pts.append({'lat': lat, 'lon': lon})
                        except: pass
                if pts:
                    paths.append(pd.DataFrame(pts))
        else:
            # タグがないプレーンテキストの場合
            pts = []
            for line in content.strip().splitlines():
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    try:
                        lon, lat = float(parts[0]), float(parts[1])
                        pts.append({'lat': lat, 'lon': lon})
                    except: pass
            if pts:
                paths.append(pd.DataFrame(pts))
    except:
        pass
    return paths

def decode_extended_float(chunk_10b):
    try:
        mantissa = struct.unpack('<Q', chunk_10b[:8])[0]
        exp_sign = struct.unpack('<H', chunk_10b[8:10])[0]
        if (exp_sign & 0x7FFF) == 0: return 0.0
        sign = -1 if (exp_sign & 0x8000) else 1
        exp = (exp_sign & 0x7FFF) - 16383
        return sign * (mantissa / (2**63)) * (2 ** exp)
    except:
        return 0.0

def parse_bnx4_binary(data_bytes, end_hour=16, end_minute=35):
    records = []
    i = 0
    length = len(data_bytes)
    while i <= length - 36:
        try:
            lat = struct.unpack('<d', data_bytes[i:i+8])[0]
            lon = struct.unpack('<d', data_bytes[i+8:i+16])[0]
            if 10.0 < lat < 70.0 and -180.0 < lon < 180.0:
                elevation = struct.unpack('<f', data_bytes[i+16:i+20])[0]
                speed = struct.unpack('<f', data_bytes[i+20:i+24])[0]
                records.append({
                    'orig_idx': i, 'lat': lat, 'lon': lon,
                    'elevation_m': float(elevation),
                    'speed_kmh': max(0.0, float(speed))
                })
                i += 36
            else: i += 1
        except: i += 1
    
    df_res = pd.DataFrame(records)
    if not df_res.empty:
        total_pts = len(df_res)
        end_time_obj = datetime.datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        start_time_obj = end_time_obj - datetime.timedelta(seconds=total_pts * 0.05)
        df_res['time_str'] = [(start_time_obj + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(total_pts)]
    return df_res

def parse_dtb_binary(data_bytes, lap_idx=1, total_files=1, end_hour=16, end_minute=35):
    records = []
    length = len(data_bytes)
    stride = 128
    i = 0
    while i <= length - stride:
        chunk = data_bytes[i:i+stride]
        lat, lon, ele, speed = 0.0, 0.0, 0.0, 0.0
        lat_ext = decode_extended_float(chunk[32:42])
        lon_ext = decode_extended_float(chunk[48:58])
        if 10.0 < abs(lat_ext) < 180.0 and 10.0 < abs(lon_ext) < 180.0:
            lat, lon = lat_ext, lon_ext
            ele = decode_extended_float(chunk[64:74])
            speed = decode_extended_float(chunk[80:90])
        else:
            try:
                d32 = struct.unpack('<d', chunk[32:40])[0]
                d48 = struct.unpack('<d', chunk[48:56])[0]
                if 10.0 < abs(d32) < 180.0 and 10.0 < abs(d48) < 180.0:
                    lat, lon = d32, d48
                    f4 = struct.unpack('<f', chunk[4:8])[0]
                    speed = abs(f4) if 0.0 <= abs(f4) <= 250.0 else 0.0
            except:
                pass
        if lat != 0.0 and lon != 0.0:
            records.append({
                'orig_idx': i, 'lat': lat, 'lon': lon,
                'elevation_m': ele,
                'speed_kmh': abs(speed) if 0.0 <= abs(speed) <= 350.0 else 0.0
            })
        i += stride
    df_res = pd.DataFrame(records)
    if not df_res.empty:
        if df_res['speed_kmh'].max() < 5.0 or df_res['speed_kmh'].max() > 350.0:
            d_lat = np.radians(np.gradient(df_res['lat']))
            d_lon = np.radians(np.gradient(df_res['lon']))
            a = np.sin(d_lat/2)**2 + np.cos(np.radians(df_res['lat'])) * np.sin(d_lon/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            dist_m = 6371000.0 * c
            df_res['speed_kmh'] = np.clip(dist_m / 0.05 * 3.6, 0.0, 350.0)
        total_pts = len(df_res)
        end_time_obj = datetime.datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        offset_sec = (total_files - lap_idx) * 90
        start_time_obj = end_time_obj - datetime.timedelta(seconds=offset_sec + total_pts * 0.05)
        df_res['time_str'] = [(start_time_obj + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(total_pts)]
    return df_res

def split_time_sessions(df, gap_seconds=600):
    if df is None or df.empty: return [df]
    idx_diff = np.diff(df.index)
    session_cuts = np.where(idx_diff > (gap_seconds * 20))[0]
    sessions = []
    start_idx = 0
    for cut in session_cuts:
        sessions.append(df.iloc[start_idx:cut+1].copy())
        start_idx = cut + 1
    sessions.append(df.iloc[start_idx:].copy())
    return sessions

def parse_csv_data(data_bytes):
    try:
        try:
            df = pd.read_csv(pd.io.common.BytesIO(data_bytes))
            if len(df.columns) < 2:
                df = pd.read_csv(pd.io.common.BytesIO(data_bytes), sep=r'\s+')
        except:
            df = pd.read_csv(pd.io.common.BytesIO(data_bytes), sep=r'\s+')
            
        column_mapping = {
            '秒': 'sec', '時間': 'time', '緯度': 'lat', '経度': 'lon',
            '距離(km)': 'dist_km', '速度(km/h)': 'speed_kmh', '加減速G': 'accel_g',
            'コーナリングG': 'cornering_g', '時刻': 'time_str'
        }
        df = df.rename(columns=column_mapping)
        for col in df.columns:
            c_lower = str(col).lower().strip()
            if c_lower in ['latitude', 'lat.', 'lat']: df = df.rename(columns={col: 'lat'})
            if c_lower in ['longitude', 'lon.', 'lon', 'lng']: df = df.rename(columns={col: 'lon'})
            if c_lower in ['speed', 'speed_kmh', 'vel']: df = df.rename(columns={col: 'speed_kmh'})
            if c_lower in ['time', 'time_str', 'clock']: df = df.rename(columns={col: 'time_str'})
            
        if 'speed_kmh' not in df.columns and 'lat' in df.columns and 'lon' in df.columns:
            df['speed_kmh'] = 0.0
            
        if 'time_str' not in df.columns:
            start_t = datetime.datetime.now().replace(hour=10, minute=57, second=0)
            df['time_str'] = [(start_t + datetime.timedelta(seconds=idx*0.05)).strftime("%H:%M:%S") for idx in range(len(df))]
        return df
    except:
        return pd.DataFrame()

def fetch_osm_raceway_width(center_lat, center_lon, radius_m=1200):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (way["highway"="raceway"](around:{radius_m},{center_lat},{center_lon}););
    out body; >; out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=8)
        data = response.json()
        nodes = {node['id']: (node['lat'], node['lon']) for node in data['elements'] if node['type'] == 'node'}
        ways = []
        for element in data['elements']:
            if element['type'] == 'way':
                way_coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
                if way_coords: ways.append(way_coords)
        return ways
    except:
        return []

def process_lap_telemetry(df, min_pts=500, dist_thresh=0.00025, manual_start=None):
    if df is None or df.empty or 'lat' not in df.columns or len(df) < 5:
        if df is not None and not df.empty and 'lap' not in df.columns:
            df['lap'] = 1
        return df
    
    if 'speed_kmh' not in df.columns or df['speed_kmh'].max() < 5.0:
        d_lat = np.radians(np.gradient(df['lat']))
        d_lon = np.radians(np.gradient(df['lon']))
        a = np.sin(d_lat/2)**2 + np.cos(np.radians(df['lat'])) * np.sin(d_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        dist_m = 6371000.0 * c
        df['speed_kmh'] = np.clip(dist_m / 0.05 * 3.6, 0.0, 350.0)

    speed_ms = df['speed_kmh'] / 3.6
    dt = 0.05
    
    if 'accel_g' not in df.columns or df['accel_g'].isnull().all():
        accel_m_s2 = np.gradient(speed_ms, dt)
        df['accel_g'] = accel_m_s2 / 9.80665

    if 'cornering_g' not in df.columns or df['cornering_g'].isnull().all():
        d_lat = np.gradient(df['lat'])
        d_lon = np.gradient(df['lon'])
        heading = np.arctan2(d_lon, d_lat)
        d_heading = np.gradient(heading)
        omega = d_heading / dt
        a_lat = speed_ms * omega
        df['cornering_g'] = np.clip(a_lat / 9.80665, -1.5, 1.5)

    df['lean_angle_deg'] = np.degrees(np.arctan(df['cornering_g']))

    conditions = [(df['accel_g'] < -0.15), (df['accel_g'] > 0.12)]
    choices = ['Braking', 'Accel']
    df['pedal_status'] = np.select(conditions, choices, default='Coasting')

    if 'file_lap' in df.columns:
        return df

    if manual_start and manual_start[0] != 0.0:
        start_lat, start_lon = manual_start[0], manual_start[1]
    else:
        fast_pts = df[df['speed_kmh'] > 40.0]
        if not fast_pts.empty:
            hist, xedges, yedges = np.histogram2d(fast_pts['lat'], fast_pts['lon'], bins=40)
            max_bin = np.unravel_index(hist.argmax(), hist.shape)
            start_lat = (xedges[max_bin[0]] + xedges[max_bin[0]+1]) / 2.0
            start_lon = (yedges[max_bin[1]] + yedges[max_bin[1]+1]) / 2.0
        else:
            start_lat, start_lon = df['lat'].iloc[0], df['lon'].iloc[0]

    dist = np.sqrt((df['lat'] - start_lat)**2 + (df['lon'] - start_lon)**2)
    
    lap_num = 1
    laps = []
    counter = 0
    for i in range(len(df)):
        counter += 1
        if counter > min_pts and dist.iloc[i] < dist_thresh and df['speed_kmh'].iloc[i] > 20.0:
            lap_num += 1
            counter = 0
        laps.append(lap_num)
        
    df['lap'] = laps
    return df

def align_laps_entire_track(df):
    if df is None or df.empty or 'lap' not in df.columns: return df
    ref_lap = df['lap'].min()
    
    ref_df = df[df['lap'] == ref_lap]
    if len(ref_df) < 50: return df

    ref_center_lat = ref_df['lat'].mean()
    ref_center_lon = ref_df['lon'].mean()

    for lap_id in df['lap'].unique():
        if lap_id == ref_lap: continue
        lap_mask = df['lap'] == lap_id
        lap_df = df[lap_mask]
        if len(lap_df) < 50: continue
        
        lap_center_lat = lap_df['lat'].mean()
        lap_center_lon = lap_df['lon'].mean()

        offset_lat = ref_center_lat - lap_center_lat
        offset_lon = ref_center_lon - lap_center_lon

        df.loc[lap_mask, 'lat'] += offset_lat
        df.loc[lap_mask, 'lon'] += offset_lon

    return df

def rotate_coordinates(df, angle_deg, center_lat, center_lon):
    if angle_deg == 0.0: return df['lat'], df['lon']
    rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(rad), np.sin(rad)
    d_lat = df['lat'] - center_lat
    d_lon = (df['lon'] - center_lon) * np.cos(np.radians(center_lat))
    rot_lon = d_lon * cos_a - d_lat * sin_a
    rot_lat = d_lon * sin_a + d_lat * cos_a
    new_lat = center_lat + rot_lat
    new_lon = center_lon + rot_lon / np.cos(np.radians(center_lat))
    return new_lat, new_lon

def format_lap_time(seconds):
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

def render_rotated_bike_image(bike_pil_img, lean_deg):
    if bike_pil_img is None: return None
    return bike_pil_img.rotate(lean_deg, resample=Image.BICUBIC, expand=True)

# -----------------------------------------------------------------------------
# 5. サイドバーUI ＆ 言語切替
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🌐 LANGUAGE / 言語切替")
lang_choice = st.sidebar.radio("Language:", ["日本語", "English"], index=0, horizontal=True)
L = LANG_DICT[lang_choice]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {L['theme_select']}")
theme_name = st.sidebar.radio("Theme:", list(THEMES.keys()), index=0)
cur_theme = THEMES[theme_name]

st.markdown(f"""
<style>
    .stApp {{ background-color: {cur_theme['bg_app']}; color: {cur_theme['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {cur_theme['bg_panel']}; border-right: 1px solid {cur_theme['border']}; padding-top: 1rem; }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 1rem; padding-left: 1.5rem; padding-right: 1.5rem; }}
    .main-title {{
        font-size: 2.8rem; font-weight: 900; letter-spacing: -1px;
        background: linear-gradient(90deg, {cur_theme['accent']} 0%, #ffffff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}
    .sub-title {{ font-size: 0.85rem; color: #64748b; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px; }}
    .metric-card {{
        background: {cur_theme['bg_card']};
        border: 1px solid {cur_theme['border']}; border-radius: 8px; padding: 8px 12px; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .metric-title {{ color: {cur_theme['text']}; font-size: 0.75rem; font-weight: 700; opacity: 0.8; letter-spacing: 0.5px; }}
    .metric-value {{ font-size: 1.35rem; font-weight: 800; margin: 2px 0; }}
    .metric-unit {{ font-size: 0.75rem; color: {cur_theme['text']}; opacity: 0.6; }}
    .best-lap-card {{ border-color: {cur_theme['best']}; }}
    div[data-baseweb="select"] > div {{ background-color: {cur_theme['bg_card']} !important; border-color: {cur_theme['border']} !important; }}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"### {L['config_assets']}")
uploaded_setting_file = st.sidebar.file_uploader(L['saved_config'], type=["json"])

saved_settings = {}
if uploaded_setting_file is not None:
    try:
        saved_settings = json.load(uploaded_setting_file)
        st.sidebar.success(L['config_loaded'])
    except:
        st.sidebar.error(L['config_failed'])

uploaded_files = st.sidebar.file_uploader(L['telemetry_file'], type=["bnx4", "dtb", "csv"], accept_multiple_files=True)
uploaded_pth_file = st.sidebar.file_uploader(L['circuit_pth'], type=["pth"])
uploaded_bg_img = st.sidebar.file_uploader(L['circuit_bg'], type=["png", "jpg", "jpeg"])
uploaded_geojson_file = st.sidebar.file_uploader(L['geojson_file'], type=["geojson", "json"])

# bike.png はフォルダ内固定自動読込（UI要素なし）
bike_pil = None
if os.path.exists('bike.png'):
    bike_pil = Image.open('bike.png')
elif os.path.exists('input_file_2.png'):
    bike_pil = Image.open('input_file_2.png')

pth_paths = []
if uploaded_pth_file is not None:
    pth_paths = parse_pth_course_file(uploaded_pth_file.getvalue())

st.sidebar.markdown("⏱️ **最終走行時刻基準（JST）の設定**")
end_h = st.sidebar.number_input("最終周 終了時間(時)", min_value=0, max_value=23, value=16)
end_m = st.sidebar.number_input("最終周 終了時間(分)", min_value=0, max_value=59, value=35)

map_style = st.sidebar.selectbox(f"{L['render_style']}:", ["自動生成 想定コース幅（路面帯）", "OSM サーキットコース幅自動取得 (方法3)", "国土地理院/GeoJSON コース幅 (方法1)", "グラデーションカラー表示", "独自画像背景", "ESRI 衛星写真 (高画質)", "標準地図 (OSM)"])

auto_track_width = 18
auto_track_opacity = 0.25
auto_offset_x_int, auto_offset_y_int = 0, 0

if map_style == "自動生成 想定コース幅（路面帯）":
    auto_track_width = st.sidebar.slider(L['track_width'], 8, 40, int(saved_settings.get("auto_track_width", 18)), 1)
    auto_track_opacity = st.sidebar.slider(L['track_opacity'], 0.05, 0.80, float(saved_settings.get("auto_track_opacity", 0.25)), 0.05)
    st.sidebar.caption(f"📐 **{L['track_shift_x']} / Y**")
    auto_offset_x_int = st.sidebar.number_input(L['track_shift_x'], min_value=-100, max_value=100, value=int(saved_settings.get("auto_offset_x_int", 0)), step=1)
    auto_offset_y_int = st.sidebar.number_input(L['track_shift_y'], min_value=-100, max_value=100, value=int(saved_settings.get("auto_offset_y_int", 0)), step=1)

auto_offset_x = auto_offset_x_int * 0.00001
auto_offset_y = auto_offset_y_int * 0.00001

rotation_angle = st.sidebar.number_input(
    L['north_rotation'],
    min_value=-180.00, max_value=180.00,
    value=float(saved_settings.get("rotation_angle", 0.00)),
    step=0.01, format="%.2f"
)

bg_offset_x_int, bg_offset_y_int = 0, 0
bg_scale_x, bg_scale_y, bg_opacity = 1.0, 1.0, 0.6

if map_style == "独自画像背景" and uploaded_bg_img is not None:
    st.sidebar.caption(f"📐 **{L['bg_shift']}**")
    bg_offset_x_int = st.sidebar.number_input(L['offset_x'], min_value=-100, max_value=100, value=int(saved_settings.get("bg_offset_x_int", 0)), step=1)
    bg_offset_y_int = st.sidebar.number_input(L['offset_y'], min_value=-100, max_value=100, value=int(saved_settings.get("bg_offset_y_int", 0)), step=1)
    bg_scale_x = st.sidebar.number_input(L['scale_x'], value=float(saved_settings.get("bg_scale_x", 1.000)), min_value=0.100, max_value=5.000, step=0.010, format="%.3f")
    bg_scale_y = st.sidebar.number_input(L['scale_y'], value=float(saved_settings.get("bg_scale_y", 1.000)), min_value=0.100, max_value=5.000, step=0.010, format="%.3f")
    bg_opacity = st.sidebar.slider(L['opacity'], 0.10, 1.00, float(saved_settings.get("bg_opacity", 0.60)), 0.05)

bg_offset_x = bg_offset_x_int * 0.00001
bg_offset_y = bg_offset_y_int * 0.00001

split_pts = st.sidebar.number_input(L['min_pts'], min_value=10, max_value=2000, value=int(saved_settings.get("split_pts", 500)), step=50)
auto_align = st.sidebar.button(L['auto_gps'])

# -----------------------------------------------------------------------------
# 6. マルチファイルパース (.dtb / .bnx4 / .csv)
# -----------------------------------------------------------------------------
df = None
raw_df = pd.DataFrame()

if uploaded_files:
    dfs_list = []
    if len(uploaded_files) >= 1 and all(f.name.lower().endswith('.dtb') for f in uploaded_files):
        total_files = len(uploaded_files)
        for f_idx, u_f in enumerate(uploaded_files):
            f_bytes = u_f.getvalue()
            single_df = parse_dtb_binary(f_bytes, lap_idx=f_idx+1, total_files=total_files, end_hour=end_h, end_minute=end_m)
            if not single_df.empty:
                single_df['lap'] = f_idx + 1
                single_df['file_lap'] = True
                dfs_list.append(single_df)
        raw_df = pd.concat(dfs_list, ignore_index=True) if dfs_list else pd.DataFrame()
    else:
        u_f = uploaded_files[0]
        fname = u_f.name.lower()
        f_bytes = u_f.getvalue()
        if fname.endswith('.bnx4'):
            raw_df = parse_bnx4_binary(f_bytes, end_hour=end_h, end_minute=end_m)
        elif fname.endswith('.dtb'):
            raw_df = parse_dtb_binary(f_bytes, lap_idx=1, total_files=1, end_hour=end_h, end_minute=end_m)
            raw_df['file_lap'] = True
        else:
            raw_df = parse_csv_data(f_bytes)
        
    if not raw_df.empty and 'lat' in raw_df.columns:
        if 'file_lap' in raw_df.columns:
            sessions = [raw_df]
        else:
            sessions = split_time_sessions(raw_df, gap_seconds=600)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"🏁 **{L['select_session']}**")
        
        session_options = ["--- ALL DATA / 全走行データ (一括) ---"]
        for idx, s_df in enumerate(sessions):
            start_t = s_df['time_str'].iloc[0] if 'time_str' in s_df.columns else "00:00:00"
            end_t = s_df['time_str'].iloc[-1] if 'time_str' in s_df.columns else "00:00:00"
            dur_m = len(s_df) * 0.05 / 60.0
            session_options.append(f"Group {idx+1}: [{start_t} 〜 {end_t}] ({dur_m:.1f}m)")
        
        selected_session = st.sidebar.selectbox("Session:", session_options)
        
        if "ALL DATA" in selected_session:
            df = raw_df
        else:
            try:
                s_idx = int(selected_session.split(":")[0].replace("Group", "").strip()) - 1
                df = sessions[s_idx]
            except:
                df = raw_df

        use_visual_start = st.sidebar.checkbox(L['visual_start'], value=False)
        manual_start_tuple = None
        
        if use_visual_start and df is not None and not df.empty and len(df) > 1:
            max_idx = len(df) - 1
            start_idx = st.sidebar.slider(L['start_slider'], 0, max_idx, 0, min(10, max_idx))
            target_pt = df.iloc[start_idx]
            manual_start_tuple = (target_pt['lat'], target_pt['lon'])

        if df is not None and not df.empty:
            df = process_lap_telemetry(df, min_pts=split_pts, manual_start=manual_start_tuple)
            if auto_align:
                df = align_laps_entire_track(df)
                st.sidebar.success(L['auto_gps'])

# -----------------------------------------------------------------------------
# 7. メインアレイ描画
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">CIRCUIT ANALYZE <span style="font-size:1.5rem; font-weight:400; opacity:0.6;">ver1.0</span></div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{L["title_sub"]}</div>', unsafe_allow_html=True)

if df is not None and not df.empty and 'lat' in df.columns:
    if 'lap' not in df.columns:
        df['lap'] = 1
        
    lap_list = []
    for lap_no, group in df.groupby('lap'):
        if len(group) < 5: continue
        lap_sec = len(group) * 0.05
        max_sp = ceil_2(group['speed_kmh'].max())
        avg_sp = ceil_2(group['speed_kmh'].mean())
        if lap_sec > 400: continue
        
        start_time_str = group['time_str'].iloc[0] if 'time_str' in group.columns else "00:00:00"
        
        lap_list.append({
            'Lap': int(lap_no),
            'StartTime': start_time_str,
            'LapTime': format_lap_time(lap_sec),
            'RawSec': lap_sec,
            'MaxSpeed': max_sp,
            'AvgSpeed': avg_sp,
            'Points': len(group)
        })
    
    sum_df = pd.DataFrame(lap_list)
    
    if not sum_df.empty:
        best_row = sum_df.loc[sum_df['RawSec'].idxmin()]

        available_laps = sum_df['Lap'].tolist()
        
        default_selected = [int(best_row['Lap'])]
        if len(available_laps) > 1:
            second_best = sum_df.sort_values('RawSec').iloc[1]['Lap']
            default_selected.append(int(second_best))

        col_select_top, col_filter_top = st.columns([3, 1.5])
        
        with col_filter_top:
            excluded_laps = st.multiselect(
                L['filter_laps'],
                options=available_laps,
                default=[],
                format_func=lambda x: f"Lap {x} [{sum_df.loc[sum_df['Lap']==x, 'LapTime'].values[0]}]"
            )
        
        filtered_available_laps = [l for l in available_laps if l not in excluded_laps]
        filtered_default_selected = [l for l in default_selected if l not in excluded_laps]

        with col_select_top:
            selected_laps = st.multiselect(
                f"{L['compare_laps']}:",
                options=filtered_available_laps,
                default=filtered_default_selected[:10],
                format_func=lambda x: f"Lap {x} [{sum_df.loc[sum_df['Lap']==x, 'LapTime'].values[0]}]({sum_df.loc[sum_df['Lap']==x, 'StartTime'].values[0]}){sum_df.loc[sum_df['Lap']==x, 'MaxSpeed'].values[0]:.2f}km/h"
            )

        if len(selected_laps) > 10: selected_laps = selected_laps[:10]

        custom_names = {}
        if selected_laps:
            center_lat, center_lon = df['lat'].mean(), df['lon'].mean()
            df['rot_lat'], df['rot_lon'] = rotate_coordinates(df, rotation_angle, center_lat, center_lon)

            main_lap_id = selected_laps[0]
            sub_lap_id = selected_laps[1] if len(selected_laps) > 1 else None
            colors = cur_theme['colors']

            col_main_replay, col_side_laps = st.columns([2.7, 1.3])

            with col_main_replay:
                col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
                with col_c1: show_pedal_points = st.checkbox(L['braking_points'], value=True)
                with col_c2: x_axis_type = st.radio(L['trace_axis'], [L['dist_m'], L['time_s']], horizontal=True)
                with col_c3: speed_factor = st.radio(L['replay_speed'], ["0.5x", "1.0x", "2.0x", "4.0x"], index=1, horizontal=True)

                step_stride = {"0.5x": 1, "1.0x": 2, "2.0x": 4, "4.0x": 8}[speed_factor]

                fig_map = go.Figure()

                base_traces_count = 0

                # 1. .pth コースガイドライン（読み込まれている場合描画）
                if pth_paths:
                    for pth_df in pth_paths:
                        pth_df['rot_lat'], pth_df['rot_lon'] = rotate_coordinates(pth_df, rotation_angle, center_lat, center_lon)
                        fig_map.add_trace(go.Scatter(
                            x=pth_df['rot_lon'] + auto_offset_x,
                            y=pth_df['rot_lat'] + auto_offset_y,
                            mode='lines', name="PTH Circuit Boundary",
                            line=dict(width=auto_track_width, color=f"rgba(160, 180, 200, {auto_track_opacity})"),
                            hoverinfo='skip', showlegend=False
                        ))
                        base_traces_count += 1

                if map_style == "自動生成 想定コース幅（路面帯）" and not pth_paths:
                    best_lap_data = df[df['lap'] == int(best_row['Lap'])].reset_index(drop=True)
                    rgba_track = f"rgba(140, 160, 180, {auto_track_opacity})"
                    rgba_curb = f"rgba(255, 255, 255, {min(1.0, auto_track_opacity + 0.2)})"
                    
                    track_lon = best_lap_data['rot_lon'] + auto_offset_x
                    track_lat = best_lap_data['rot_lat'] + auto_offset_y

                    fig_map.add_trace(go.Scatter(
                        x=track_lon, y=track_lat,
                        mode='lines', name="Track Curb Edge",
                        line=dict(width=auto_track_width + 4, color=rgba_curb), hoverinfo='skip', showlegend=False
                    ))
                    fig_map.add_trace(go.Scatter(
                        x=track_lon, y=track_lat,
                        mode='lines', name="Track Width",
                        line=dict(width=auto_track_width, color=rgba_track), hoverinfo='skip', showlegend=False
                    ))
                    base_traces_count += 2

                elif map_style == "OSM サーキットコース幅自動取得 (方法3)":
                    osm_ways = fetch_osm_raceway_width(center_lat, center_lon)
                    for way_pts in osm_ways:
                        w_df = pd.DataFrame(way_pts, columns=['lat', 'lon'])
                        w_df['rot_lat'], w_df['rot_lon'] = rotate_coordinates(w_df, rotation_angle, center_lat, center_lon)
                        fig_map.add_trace(go.Scatter(
                            x=w_df['rot_lon'], y=w_df['rot_lat'],
                            mode='lines', name="OSM Raceway",
                            line=dict(width=20, color='rgba(120, 140, 160, 0.3)'), hoverinfo='skip', showlegend=False
                        ))
                        base_traces_count += 1

                elif map_style == "独自画像背景" and uploaded_bg_img is not None:
                    bg_img = Image.open(uploaded_bg_img)
                    min_x, max_x = df['rot_lon'].min(), df['rot_lon'].max()
                    min_y, max_y = df['rot_lat'].min(), df['rot_lat'].max()
                    mid_x = (min_x + max_x) / 2.0 + bg_offset_x
                    mid_y = (min_y + max_y) / 2.0 + bg_offset_y
                    span_x = (max_x - min_x) * bg_scale_x * 1.2
                    span_y = (max_y - min_y) * bg_scale_y * 1.2

                    fig_map.add_layout_image(dict(
                        source=bg_img, xref="x", yref="y",
                        x=mid_x - span_x / 2.0, y=mid_y + span_y / 2.0,
                        sizex=span_x, sizey=span_y,
                        sizing="stretch", opacity=bg_opacity, layer="below"
                    ))

                for idx, lap_id in enumerate(selected_laps):
                    lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                    color = colors[idx % len(colors)]
                    label_name = saved_settings.get("custom_names", {}).get(str(lap_id), f"Lap {lap_id}")
                    custom_names[lap_id] = label_name

                    fig_map.add_trace(go.Scatter(
                        x=lap_data['rot_lon'], y=lap_data['rot_lat'],
                        mode='lines', name=f"{label_name}",
                        line=dict(width=3.5, color=color)
                    ))
                    base_traces_count += 1

                    if show_pedal_points and 'pedal_status' in lap_data.columns:
                        brake_df = lap_data[lap_data['pedal_status'] == 'Braking']
                        fig_map.add_trace(go.Scatter(
                            x=brake_df['rot_lon'], y=brake_df['rot_lat'],
                            mode='markers', name=f"{label_name} Brake🔴",
                            marker=dict(size=8, color='#ff0055', symbol='circle', line=dict(width=2, color='#ffffff')),
                            showlegend=False, hoverinfo='text',
                            text=[f"{label_name} Brake | {ceil_2(sp):.2f} km/h" for sp in brake_df['speed_kmh']]
                        ))
                        base_traces_count += 1

                initial_animated_indices = []
                for idx, lap_id in enumerate(selected_laps):
                    ldf = df[df['lap'] == lap_id].reset_index(drop=True)
                    color = colors[idx % len(colors)]
                    label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                    curr_pt = ldf.iloc[0]
                    fig_map.add_trace(go.Scatter(
                        x=[curr_pt['rot_lon']], y=[curr_pt['rot_lat']],
                        mode='markers+text',
                        marker=dict(size=14, color=color, line=dict(width=2, color='#ffffff')),
                        text=[f" {label_name}: {ceil_2(curr_pt['speed_kmh']):.2f} km/h"],
                        textposition="top right", showlegend=False
                    ))
                    initial_animated_indices.append(base_traces_count + idx)

                max_len = max([len(df[df['lap'] == l_id]) for l_id in selected_laps])
                frames = []
                for f_idx in range(0, max_len, step_stride):
                    frame_data = []
                    for idx, lap_id in enumerate(selected_laps):
                        ldf = df[df['lap'] == lap_id].reset_index(drop=True)
                        color = colors[idx % len(colors)]
                        label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                        pos = min(f_idx, len(ldf) - 1)
                        curr_pt = ldf.iloc[pos]
                        frame_data.append(go.Scatter(
                            x=[curr_pt['rot_lon']], y=[curr_pt['rot_lat']],
                            mode='markers+text',
                            marker=dict(size=14, color=color, line=dict(width=2, color='#ffffff')),
                            text=[f" {label_name}: {ceil_2(curr_pt['speed_kmh']):.2f} km/h"],
                            textposition="top right"
                        ))
                    frames.append(go.Frame(data=frame_data, name=str(f_idx), traces=initial_animated_indices))

                fig_map.frames = frames

                fig_map.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                    font=dict(color=cur_theme['text']), height=680,
                    xaxis=dict(showgrid=True, gridcolor=cur_theme['grid'], scaleanchor="y", scaleratio=1),
                    yaxis=dict(showgrid=True, gridcolor=cur_theme['grid']),
                    margin=dict(l=5, r=5, t=5, b=5),
                    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
                    updatemenus=[dict(
                        type="buttons", showactive=False, x=0.01, y=0.99,
                        buttons=[
                            dict(label="PLAY (▶)", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]),
                            dict(label="PAUSE (❚❚)", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
                        ]
                    )]
                )

                st.plotly_chart(fig_map, use_container_width=True)

            with col_side_laps:
                st.markdown(f"##### {L['hud_title']}")
                
                main_df = df[df['lap'] == main_lap_id].reset_index(drop=True)
                replay_idx = st.slider(L['seek_time'], 0, len(main_df)-1, 0, 5)
                
                for idx, lap_id in enumerate(selected_laps):
                    row = sum_df[sum_df['Lap'] == lap_id].iloc[0]
                    color = colors[idx % len(colors)]
                    label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                    
                    lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                    pos = min(replay_idx, len(lap_data)-1)
                    sync_pt = lap_data.iloc[pos]
                    
                    c_col1, c_col2 = st.columns([2.2, 1])
                    with c_col1:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left: 5px solid {color}; margin-bottom: 6px;">
                            <div class="metric-title" style="color:{color};">{label_name} <span style="opacity:0.7;">({row['StartTime']})</span></div>
                            <div class="metric-value" style="color:{color};">[{row['LapTime']}]</div>
                            <div class="metric-unit">{ceil_2(sync_pt['speed_kmh']):.2f} km/h (傾き {sync_pt['lean_angle_deg']:.1f}°)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_col2:
                        if bike_pil:
                            rot_bike = render_rotated_bike_image(bike_pil, sync_pt['lean_angle_deg'])
                            st.image(rot_bike, width=70)

                st.markdown("<br>", unsafe_allow_html=True)

                if sub_lap_id:
                    sub_row = sum_df.loc[sum_df['Lap']==sub_lap_id].iloc[0]
                    sub_color = colors[1 % len(colors)]
                    st.markdown(f"##### {L['sub_compare']}: <span style='color:{sub_color};'>{custom_names.get(sub_lap_id, f'Lap {sub_lap_id}')} [{sub_row['LapTime']}]({sub_row['StartTime']}){sub_row['MaxSpeed']:.2f}km/h</span>", unsafe_allow_html=True)
                    sub_df = df[df['lap'] == sub_lap_id].reset_index(drop=True)
                    
                    fig_sub = go.Figure()
                    fig_sub.add_trace(go.Scatter(
                        x=sub_df['rot_lon'], y=sub_df['rot_lat'],
                        mode='lines', line=dict(width=2.5, color=sub_color)
                    ))
                    
                    fig_sub.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                        font=dict(color=cur_theme['text']), height=180,
                        xaxis=dict(showgrid=False, visible=False, scaleanchor="y", scaleratio=1),
                        yaxis=dict(showgrid=False, visible=False),
                        margin=dict(l=2, r=2, t=2, b=2), showlegend=False
                    )
                    st.plotly_chart(fig_sub, use_container_width=True)

            st.markdown(f"### {L['speed_traces']}")
            fig_speed = go.Figure()
            
            for idx, lap_id in enumerate(selected_laps):
                lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                row = sum_df.loc[sum_df['Lap']==lap_id].iloc[0]
                color = colors[idx % len(colors)]
                label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                
                if x_axis_type in ["Distance (m)", "走行距離 (m)"]:
                    x_vals = np.cumsum(lap_data['speed_kmh'] / 3.6 * 0.05)
                    x_title = L['dist_m']
                else:
                    x_vals = np.arange(len(lap_data)) * 0.05
                    x_title = L['time_s']

                lap_data['speed_ceil'] = lap_data['speed_kmh'].apply(ceil_2)
                
                fig_speed.add_trace(go.Scatter(
                    x=x_vals, y=lap_data['speed_ceil'],
                    mode='lines', name=f"{label_name} [{row['LapTime']}]({row['StartTime']}){row['MaxSpeed']:.2f}km/h",
                    line=dict(width=2.2, color=color),
                    hovertemplate="%{x:.1f} | SPEED: %{y:.2f} km/h<extra></extra>"
                ))

            fig_speed.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                font=dict(color=cur_theme['text']), height=320,
                xaxis=dict(title=x_title, showgrid=True, gridcolor=cur_theme['grid']),
                yaxis=dict(title=L['speed_kmh'], showgrid=True, gridcolor=cur_theme['grid']),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_speed, use_container_width=True)

            current_settings = {
                "rotation_angle": rotation_angle,
                "bg_offset_x_int": bg_offset_x_int,
                "bg_offset_y_int": bg_offset_y_int,
                "bg_scale_x": bg_scale_x,
                "bg_scale_y": bg_scale_y,
                "bg_opacity": bg_opacity,
                "auto_track_width": auto_track_width,
                "auto_track_opacity": auto_track_opacity,
                "auto_offset_x_int": auto_offset_x_int,
                "auto_offset_y_int": auto_offset_y_int,
                "split_pts": split_pts,
                "custom_names": {str(k): v for k, v in custom_names.items()}
            }
            json_string = json.dumps(current_settings, indent=2, ensure_ascii=False)
            st.download_button(
                label=L['export_btn'],
                file_name="racelog_settings.json",
                mime="application/json",
                data=json_string
            )

else:
    st.info(L['drop_info'])