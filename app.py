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
import datetime

# -----------------------------------------------------------------------------
# 1. ページ基本設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CIRCUIT ANALYZE ver1.0",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. 多言語辞書
# -----------------------------------------------------------------------------
LANG_DICT = {
    "日本語": {
        "title_sub": "高精度テレメトリー ＆ ダイナミクス比較解析システム",
        "theme_select": "画面表示UIテーマ",
        "config_assets": "設定 ＆ アセット読み込み",
        "saved_config": "保存済み設定ファイル (.json - 任意)",
        "config_loaded": "設定ファイルを読み込みました",
        "config_failed": "設定ファイルのパースに失敗しました",
        "telemetry_file": "走行データ (複数選択可: .bnx / .bnx4 / .dtb / .csv / .nma)",
        "circuit_pth": "コース形状データ (.pth - 任意)",
        "control_line_cln": "コントロールラインデータ (.cln - 任意)",
        "circuit_bg": "サーキット背景画像 (.png / .jpg)",
        "render_style": "描画背景タイプ",
        "track_width": "想定コース幅 (ピクセル)",
        "track_opacity": "想定コース透明度",
        "track_shift_x": "全体コース位置 X (東西シフト)",
        "track_shift_y": "全体コース位置 Y (南北シフト)",
        "north_rotation": "北基準回転角度 (°)",
        "bg_shift": "コース図面画像の位置・比率調整 (整数単位)",
        "offset_x": "位置 X (東西)",
        "offset_y": "位置 Y (南北)",
        "scale_x": "横幅倍率 (Scale X)",
        "scale_y": "縦幅倍率 (Scale Y)",
        "opacity": "透明度",
        "min_pts": "1周の最低データ点数 (誤分割防止ガード)",
        "map_height_label": "コースマップ描画高さ (px)",
        "auto_gps": "GPS軌跡・コース重心自動フィット補正",
        "reset_gps": "GPS補正をリセット",
        "select_session": "解析対象の走行グループを選択 (複数可):",
        "saved_laps_select": "保存済みキープLAPから読み込み・比較:",
        "visual_start": "スタート位置の微調整",
        "start_candidate_label": "1. スタートラインの候補地を選択:",
        "start_offset_label": "2. 前後微調整 (メートル):",
        "marker_text_size": "走行マシン表示テキストサイズ (px)",
        "filter_laps": "不要なLAPを選択して除外（削除）:",
        "compare_laps": "比較ラップ選択 (速い順にソート表示):",
        "export_btn": "現在のコース・名前設定をファイルに保存する",
        "braking_points": "ブレーキ強調",
        "toggle_hud": "HUD非表示",
        "line_color_mode": "描画カラー:",
        "view_mode": "表示モード:",
        "zoom_sub": "追従ズーム・サブウィンドウ表示",
        "trace_axis": "グラフ比較軸:",
        "replay_speed": "再生速度:",
        "main_analysis": "メイン走行ライン解析",
        "hud_title": "HUD & バンク角分析",
        "sub_compare": "併設比較周",
        "bank_angle": "バイク傾き (リアルタイム バンク角)",
        "speed_traces": "車速 ＆ アクセル/ブレーキ状態トレース",
        "delta_traces": "デルタタイム (ベストラップとのタイム差: 秒)",
        "gg_diagram": "G-G Diagram (縦G vs 横G 摩擦サークル解析)",
        "sector_analysis": "セクター分割 ＆ テレメトリー詳細分析 (S1 / S2 / S3 / ペダル率 / V-max)",
        "drop_info": "左側のサイドバーから .bnx / .bnx4 / .dtb / .csv / .nma / .cln ファイルをドロップしてください。",
        "dist_m": "走行距離 (m)",
        "time_s": "経過時間 (秒)",
        "speed_kmh": "車速 (km/h)",
        "lean_deg": "バンク角",
        "report_export": "全テレメトリー比較レポート (CSV) をダウンロード"
    },
    "English": {
        "title_sub": "HIGH-PRECISION TELEMETRY & DYNAMICS ANALYZER",
        "theme_select": "SYSTEM UI THEME",
        "config_assets": "CONFIG & ASSETS",
        "saved_config": "Saved Config (.json - Optional)",
        "config_loaded": "Config Loaded Successfully",
        "config_failed": "Failed to Parse Config File",
        "telemetry_file": "Telemetry Data (Multiple: .bnx/.bnx4/.dtb/.csv/.nma)",
        "circuit_pth": "Circuit Path Data (.pth - Optional)",
        "control_line_cln": "Control Line Data (.cln - Optional)",
        "circuit_bg": "Circuit Track Image (.png / .jpg)",
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
        "min_pts": "Min Lap Points Guard",
        "map_height_label": "Map Render Height (px)",
        "auto_gps": "Auto Centroid Course Alignment",
        "reset_gps": "Reset GPS Alignment",
        "select_session": "Select Session Groups (Multiple):",
        "saved_laps_select": "Load & Compare Saved Kept Laps:",
        "visual_start": "Start Line Candidate & Meter Offset Adjust",
        "start_candidate_label": "1. Select Start Candidate Location:",
        "start_offset_label": "2. Fine-tune Position (Meters):",
        "marker_text_size": "Bike Marker Text Size (px)",
        "filter_laps": "Select Unwanted Laps to Exclude (Remove):",
        "compare_laps": "SELECT LAPS TO COMPARE:",
        "export_btn": "EXPORT CONFIG FILE (.JSON)",
        "braking_points": "Enhanced Braking Points",
        "toggle_hud": "Hide HUD Panel",
        "line_color_mode": "Trace Color Mode:",
        "view_mode": "View Mode:",
        "zoom_sub": "Follow Zoom Sub-Window",
        "trace_axis": "Trace Axis:",
        "replay_speed": "Replay Speed:",
        "main_analysis": "MAIN LAP TRACE ANALYSIS",
        "hud_title": "HUD & LEAN ANALYZER",
        "sub_compare": "SUB COMPARE",
        "bank_angle": "DYNAMICS (BANK ANGLE)",
        "speed_traces": "TELEMETRY SPEED TRACES",
        "delta_traces": "DELTA TIME (vs Best Lap: Sec)",
        "gg_diagram": "G-G DIAGRAM (G-Circle Analysis)",
        "sector_analysis": "SECTOR ANALYSIS & TELEMETRY REPORT",
        "drop_info": "DROP TELEMETRY (.BNX/.DTB/.CSV/.NMA) OR .CLN FILES FROM SIDEBAR.",
        "dist_m": "Distance (m)",
        "time_s": "Time (s)",
        "speed_kmh": "Speed (km/h)",
        "lean_deg": "Lean",
        "report_export": "Export Full Telemetry Report (CSV)"
    }
}

THEMES = {
    "Dark (夜間解析用)": {
        "bg_app": "#040806", "bg_panel": "#09120e", "bg_card": "#0d1a14",
        "border": "#1b3a2b", "text": "#ffffff", "subtext": "#94a3b8", "accent": "#00ff66", "pth_line": "rgba(160, 180, 200, 0.5)",
        "plot_bg": "#06110b", "grid": "#13281c",
        "drop_bg": "#14231b", "drop_border": "#27543d",
        "dropdown_bg": "#0d1a14", "dropdown_text": "#ffffff", "dropdown_hover": "#1b3a2b",
        "modebar_color": "#00ff66", "modebar_active": "#ffffff",
        "colors": ["#00f2fe", "#ff2a5f", "#00ff88", "#ffb703", "#a855f7", "#00ff66", "#f43f5e", "#06b6d4", "#eab308", "#ec4899"]
    },
    "High Contrast (日中日陰用)": {
        "bg_app": "#ffffff", "bg_panel": "#f1f5f9", "bg_card": "#e2e8f0",
        "border": "#94a3b8", "text": "#000000", "subtext": "#334155", "accent": "#1d4ed8", "pth_line": "rgba(15, 23, 42, 0.9)",
        "plot_bg": "#f8fafc", "grid": "#cbd5e1",
        "drop_bg": "#e2e8f0", "drop_border": "#64748b",
        "dropdown_bg": "#ffffff", "dropdown_text": "#000000", "dropdown_hover": "#e2e8f0",
        "modebar_color": "#1d4ed8", "modebar_active": "#000000",
        "colors": ["#1d4ed8", "#dc2626", "#15803d", "#c2410c", "#7e22ce", "#0369a1", "#a16207", "#be123c", "#3730a3", "#047857"]
    }
}

TEXT_POSITIONS = ["top right", "top left", "bottom right", "bottom left", "top center", "bottom center", "middle right", "middle left"]

COMMON_PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "toImageButtonOptions": {"format": "png", "filename": "circuit_telemetry", "height": 800, "width": 1200, "scale": 2}
}

def ceil_2(val):
    if pd.isna(val) or val is None: return 0.0
    return math.ceil(val * 100.0) / 100.0

def parse_pth_course_text(content_text):
    paths = []
    try:
        path_blocks = re.findall(r'<path>(.*?)</path>', content_text, re.DOTALL | re.IGNORECASE)
        if not path_blocks:
            path_blocks = [content_text]

        for block in path_blocks:
            pts = []
            for line in block.strip().splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith('<'): continue
                parts = line_str.split(',')
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0].strip())
                        lat = float(parts[1].strip())
                        if -180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0:
                            pts.append({'lat': lat, 'lon': lon})
                    except: pass
            if len(pts) >= 2:
                paths.append(pd.DataFrame(pts))
    except Exception as e:
        pass
    return paths

def parse_cln_file(content_text):
    pts = []
    try:
        lines = content_text.strip().splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith('#') or line_str.startswith('<'): continue
            parts = re.split(r'[,\s\t]+', line_str)
            if len(parts) >= 2:
                try:
                    p1 = float(parts[0])
                    p2 = float(parts[1])
                    if 120.0 <= abs(p1) <= 150.0 and 20.0 <= abs(p2) <= 50.0:
                        pts.append({'lat': p2, 'lon': p1})
                    elif 20.0 <= abs(p1) <= 50.0 and 120.0 <= abs(p2) <= 150.0:
                        pts.append({'lat': p1, 'lon': p2})
                except: pass
    except Exception as e:
        pass
    return pd.DataFrame(pts) if pts else None

def nmea_coord_to_decimal(raw_val, direction):
    try:
        raw_float = float(raw_val)
        deg = int(raw_float / 100)
        minutes = raw_float - (deg * 100)
        dec = deg + (minutes / 60.0)
        if direction in ['S', 'W']:
            dec = -dec
        return dec
    except:
        return None

@st.cache_data
def parse_nma_data(data_bytes):
    records = []
    try:
        text = data_bytes.decode('ascii', errors='ignore')
    except:
        text = str(data_bytes)
    
    current_time_str = "00:00:00"
    pending_speed = None
    
    for line in text.splitlines():
        line = line.strip()
        if not line or '$' not in line:
            continue
        
        nmea_part = line[line.find('$'):]
        if '*' in nmea_part:
            nmea_part = nmea_part.split('*')[0]
        tokens = nmea_part.split(',')
        if len(tokens) < 3:
            continue
        
        tag = tokens[0]
        
        if tag in ['$GNVTG', '$GPVTG']:
            if len(tokens) >= 8 and tokens[7] != '':
                try:
                    pending_speed = max(0.0, float(tokens[7]))
                except: pass
            elif len(tokens) >= 6 and tokens[5] != '':
                try:
                    pending_speed = max(0.0, float(tokens[5]) * 1.852)
                except: pass

        elif tag in ['$GNRMC', '$GPRMC']:
            if len(tokens) >= 7 and tokens[2] == 'A':
                time_token = tokens[1]
                lat_raw, lat_dir = tokens[3], tokens[4]
                lon_raw, lon_dir = tokens[5], tokens[6]
                
                lat = nmea_coord_to_decimal(lat_raw, lat_dir)
                lon = nmea_coord_to_decimal(lon_raw, lon_dir)
                
                sp_kmh = pending_speed
                if sp_kmh is None and len(tokens) >= 8 and tokens[7] != '':
                    try:
                        sp_kmh = max(0.0, float(tokens[7]) * 1.852)
                    except: pass
                
                if len(time_token) >= 6:
                    try:
                        hh = (int(time_token[0:2]) + 9) % 24
                        mm = int(time_token[2:4])
                        ss = int(time_token[4:6])
                        current_time_str = f"{hh:02d}:{mm:02d}:{ss:02d}"
                    except: pass
                    
                if lat is not None and lon is not None:
                    records.append({
                        'lat': lat,
                        'lon': lon,
                        'speed_kmh': sp_kmh if sp_kmh is not None else 0.0,
                        'time_str': current_time_str
                    })
                    pending_speed = None

        elif tag in ['$GNGGA', '$GPGGA']:
            if len(tokens) >= 6 and tokens[2] != '' and tokens[4] != '':
                time_token = tokens[1]
                lat_raw, lat_dir = tokens[2], tokens[3]
                lon_raw, lon_dir = tokens[4], tokens[5]
                lat = nmea_coord_to_decimal(lat_raw, lat_dir)
                lon = nmea_coord_to_decimal(lon_raw, lon_dir)
                
                if len(time_token) >= 6:
                    try:
                        hh = (int(time_token[0:2]) + 9) % 24
                        mm = int(time_token[2:4])
                        ss = int(time_token[4:6])
                        current_time_str = f"{hh:02d}:{mm:02d}:{ss:02d}"
                    except: pass

                if lat is not None and lon is not None:
                    records.append({
                        'lat': lat,
                        'lon': lon,
                        'speed_kmh': pending_speed if pending_speed is not None else 0.0,
                        'time_str': current_time_str
                    })
                    pending_speed = None

    df_res = pd.DataFrame(records)
    if not df_res.empty:
        df_res = df_res.reset_index(drop=True)
        if df_res['speed_kmh'].max() < 3.0:
            d_lat = np.radians(np.gradient(df_res['lat']))
            d_lon = np.radians(np.gradient(df_res['lon']))
            a = np.sin(d_lat/2)**2 + np.cos(np.radians(df_res['lat'])) * np.sin(d_lon/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            dist_m = 6371000.0 * c
            df_res['speed_kmh'] = np.clip(dist_m / 0.1 * 3.6, 0.0, 350.0)
    return df_res

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

@st.cache_data
def parse_bnx4_binary_cached(data_bytes):
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
        df_res['time_str'] = [(datetime.datetime.now() + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(total_pts)]
    return df_res

@st.cache_data
def parse_dtb_binary_cached(data_bytes, lap_idx=1, total_files=1):
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
        df_res['time_str'] = [(datetime.datetime.now() + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(total_pts)]
    return df_res

def split_time_sessions(df, gap_seconds=300):
    if df is None or df.empty: return [df]
    idx_diff = np.diff(df.index)
    session_cuts = np.where(idx_diff > (gap_seconds * 20))[0]
    
    sessions = []
    start_idx = 0
    for cut in session_cuts:
        sess = df.iloc[start_idx:cut+1].copy()
        if len(sess) >= 10:
            sessions.append(sess)
        start_idx = cut + 1
    last_sess = df.iloc[start_idx:].copy()
    if len(last_sess) >= 10:
        sessions.append(last_sess)
        
    return sessions if sessions else [df]

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

def process_lap_telemetry(df, min_pts=300, dist_thresh=0.00015, manual_start=None):
    if df is None or df.empty or 'lat' not in df.columns or len(df) < 5:
        if df is not None and not df.empty and 'lap' not in df.columns:
            df['lap'] = 1
        return df
    
    if 'speed_kmh' not in df.columns or df['speed_kmh'].max() < 3.0:
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

    if manual_start and manual_start[0] != 0.0:
        start_lat, start_lon = manual_start[0], manual_start[1]
    else:
        fast_pts = df[df['speed_kmh'] > 15.0]
        if not fast_pts.empty:
            hist, xedges, yedges = np.histogram2d(fast_pts['lat'], fast_pts['lon'], bins=40)
            max_bin = np.unravel_index(hist.argmax(), hist.shape)
            start_lat = (xedges[max_bin[0]] + xedges[max_bin[0]+1]) / 2.0
            start_lon = (yedges[max_bin[1]] + yedges[max_bin[1]+1]) / 2.0
        else:
            start_lat, start_lon = df['lat'].iloc[0], df['lon'].iloc[0]

    dist = np.sqrt((df['lat'] - start_lat)**2 + (df['lon'] - start_lon)**2)
    
    if 'file_lap' in df.columns and not manual_start:
        return df

    lap_num = 1
    laps = []
    counter = 0
    for i in range(len(df)):
        counter += 1
        if counter > min_pts and dist.iloc[i] < dist_thresh:
            lap_num += 1
            counter = 0
        laps.append(lap_num)
        
    df['lap'] = laps
    return df.reset_index(drop=True)

def align_laps_entire_track(df, pth_paths=None):
    if df is None or df.empty or 'lat' not in df.columns: return df
    
    fast_pts = df[df['speed_kmh'] > 10.0]
    if fast_pts.empty: fast_pts = df
    
    data_center_lat = fast_pts['lat'].mean()
    data_center_lon = fast_pts['lon'].mean()

    if pth_paths and len(pth_paths) > 0:
        all_pth_pts = pd.concat(pth_paths, ignore_index=True)
        pth_center_lat = all_pth_pts['lat'].mean()
        pth_center_lon = all_pth_pts['lon'].mean()
        
        offset_lat = pth_center_lat - data_center_lat
        offset_lon = pth_center_lon - data_center_lon
        
        df['lat'] += offset_lat
        df['lon'] += offset_lon

    return df

def auto_align_laps_to_ref(df, ref_lap_id):
    if df is None or df.empty or 'lap' not in df.columns: return df
    ref_df = df[df['lap'] == ref_lap_id].reset_index(drop=True)
    if ref_df.empty: return df
    
    ref_coords = ref_df[['lat', 'lon']].values
    
    for lap_id in df['lap'].unique():
        if lap_id == ref_lap_id: continue
        lap_mask = df['lap'] == lap_id
        lap_df = df[lap_mask].reset_index(drop=True)
        if len(lap_df) < 50: continue
        
        lap_coords = lap_df[['lat', 'lon']].values
        dists = np.linalg.norm(lap_coords[:, None, :] - ref_coords[None, :, :], axis=2)
        closest_indices = np.argmin(dists, axis=1)
        matched_ref_coords = ref_coords[closest_indices]
        
        offset = np.mean(matched_ref_coords - lap_coords, axis=0)
        
        offset[0] = np.clip(offset[0], -0.00015, 0.00015)
        offset[1] = np.clip(offset[1], -0.00015, 0.00015)
        
        df.loc[lap_mask, 'lat'] += offset[0]
        df.loc[lap_mask, 'lon'] += offset[1]
        
    return df

# -----------------------------------------------------------------------------
# 【修正】歪み（アスペクト比の狂い）を完全に排除するメートル直交座標回転
# -----------------------------------------------------------------------------
def rotate_coordinates(df, angle_deg, center_lat, center_lon):
    if df is None or df.empty or 'lat' not in df.columns or 'lon' not in df.columns:
        return df.get('lat', pd.Series()), df.get('lon', pd.Series())
    
    # 緯度・経度のメートル換算係数
    lat_rad = np.radians(center_lat)
    m_per_deg_lat = 111132.954 - 559.822 * np.cos(2 * lat_rad) + 1.175 * np.cos(4 * lat_rad)
    m_per_deg_lon = (math.pi / 180.0) * 6378137.0 * np.cos(lat_rad)
    
    # メートル単位の直交座標（X: 東西, Y: 南北）に変換
    x_m = (df['lon'] - center_lon) * m_per_deg_lon
    y_m = (df['lat'] - center_lat) * m_per_deg_lat
    
    if angle_deg != 0.0:
        rad = np.radians(angle_deg)
        cos_a = np.cos(rad)
        sin_a = np.sin(rad)
        # ユークリッド空間で真の等長回転
        rot_x_m = x_m * cos_a - y_m * sin_a
        rot_y_m = x_m * sin_a + y_m * cos_a
    else:
        rot_x_m = x_m
        rot_y_m = y_m

    # 等長比率を保ったまま度数法表示へ逆写像
    rot_lon = center_lon + (rot_x_m / m_per_deg_lon)
    rot_lat = center_lat + (rot_y_m / m_per_deg_lat)
    
    return rot_lat, rot_lon

def format_lap_time(seconds):
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# -----------------------------------------------------------------------------
# 5. UIテーマ ＆ プルダウン視認性改善CSS
# -----------------------------------------------------------------------------
st.sidebar.markdown("### LANGUAGE / 言語切替")
lang_choice = st.sidebar.radio("Language:", ["日本語", "English"], index=0, horizontal=True)
L = LANG_DICT[lang_choice]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {L['theme_select']}")
theme_name = st.sidebar.radio("Theme Mode:", list(THEMES.keys()), index=0)
cur_theme = THEMES[theme_name]

st.markdown(f"""
<style>
    .stApp {{ background-color: {cur_theme['bg_app']}; color: {cur_theme['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {cur_theme['bg_panel']}; border-right: 1px solid {cur_theme['border']}; padding-top: 1rem; }}
    
    h1, h2, h3, h4, h5, h6, label, .stMarkdown, p, span, div {{
        color: {cur_theme['text']} !important;
    }}
    
    .main-title {{
        font-size: 4.5rem; font-weight: 200; letter-spacing: 4px; line-height: 1.1;
        background: linear-gradient(90deg, {cur_theme['accent']} 0%, {cur_theme['text']} 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 0.5rem; margin-bottom: 0.2rem; padding-top: 0.5rem;
    }}
    .sub-title {{ font-size: 0.90rem; font-weight: 300; color: {cur_theme['subtext']} !important; margin-bottom: 1.2rem; letter-spacing: 2px; }}
    
    .toolbar-box {{
        background: {cur_theme['bg_card']};
        border: 1px solid {cur_theme['border']};
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 12px;
    }}
    .toolbar-title {{
        font-size: 0.75rem;
        font-weight: 700;
        color: {cur_theme['accent']} !important;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }}
    
    .metric-card-slim {{
        background: {cur_theme['bg_card']};
        border: 1px solid {cur_theme['border']};
        border-radius: 6px;
        padding: 6px 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }}
    .metric-title-slim {{
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1.2;
    }}
    .metric-value-slim {{
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        line-height: 1.1;
        margin: 3px 0px;
        color: {cur_theme['text']} !important;
        text-shadow: 0 0 6px rgba(0,255,102,0.2);
    }}
    .metric-unit-slim {{
        font-size: 0.65rem;
        opacity: 0.85;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {cur_theme['dropdown_bg']} !important;
        border-color: {cur_theme['border']} !important;
        color: {cur_theme['dropdown_text']} !important;
    }}
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {{
        color: {cur_theme['dropdown_text']} !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
    ul[data-testid="stSelectboxVirtualDropdown"],
    ul[role="listbox"] {{
        background-color: {cur_theme['dropdown_bg']} !important;
        border: 1px solid {cur_theme['border']} !important;
    }}

    ul[role="listbox"] li,
    ul[data-testid="stSelectboxVirtualDropdown"] li,
    li[role="option"] {{
        background-color: {cur_theme['dropdown_bg']} !important;
        color: {cur_theme['dropdown_text']} !important;
    }}
    
    ul[role="listbox"] li span,
    ul[data-testid="stSelectboxVirtualDropdown"] li span,
    li[role="option"] span,
    li[role="option"] div {{
        color: {cur_theme['dropdown_text']} !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }}

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: {cur_theme['dropdown_hover']} !important;
    }}
    li[role="option"]:hover span,
    li[role="option"][aria-selected="true"] span {{
        color: {cur_theme['accent']} !important;
    }}

    .modebar-container {{
        opacity: 0.95 !important;
        background-color: transparent !important;
    }}
    .modebar-btn {{
        background-color: {cur_theme['bg_card']} !important;
        border-radius: 4px !important;
        margin: 1px !important;
        padding: 2px !important;
    }}
    .modebar-btn svg path {{
        fill: {cur_theme['modebar_color']} !important;
    }}
    .modebar-btn.active svg path, .modebar-btn:hover svg path {{
        fill: {cur_theme['modebar_active']} !important;
    }}

    div[data-testid="stFileUploader"] section {{
        background-color: {cur_theme['drop_bg']} !important;
        border: 2px dashed {cur_theme['drop_border']} !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }}
    div[data-testid="stFileUploader"] section:hover {{
        border-color: {cur_theme['accent']} !important;
    }}

    button[kind="secondary"], button[kind="primary"] {{
        background-color: {cur_theme['bg_card']} !important;
        color: {cur_theme['text']} !important;
        border: 1px solid {cur_theme['border']} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"### {L['config_assets']}")
uploaded_setting_file = st.sidebar.file_uploader(L['saved_config'], type=["json"])

saved_settings = {}
if uploaded_setting_file is not None:
    try:
        saved_settings = json.load(uploaded_setting_file)
        if "custom_names" in saved_settings and isinstance(saved_settings["custom_names"], dict):
            saved_settings["custom_names"] = {
                int(k) if str(k).isdigit() else k: str(v)
                for k, v in saved_settings["custom_names"].items()
            }
        st.sidebar.success(L['config_loaded'])
    except Exception as e:
        st.sidebar.error(f"{L['config_failed']}: {e}")

uploaded_files = st.sidebar.file_uploader(L['telemetry_file'], type=["bnx", "bnx4", "dtb", "csv", "nma", "nmea"], accept_multiple_files=True)
uploaded_pth_file = st.sidebar.file_uploader(L['circuit_pth'], type=["pth"])
uploaded_cln_file = st.sidebar.file_uploader(L['control_line_cln'], type=["cln"])
uploaded_bg_img = st.sidebar.file_uploader(L['circuit_bg'], type=["png", "jpg", "jpeg"])

pth_paths = []
if uploaded_pth_file is not None:
    pth_paths = parse_pth_course_text(uploaded_pth_file.getvalue().decode('utf-8', errors='ignore'))

cln_df = None
cln_start_tuple = None
if uploaded_cln_file is not None:
    cln_df = parse_cln_file(uploaded_cln_file.getvalue().decode('utf-8', errors='ignore'))
    if cln_df is not None and not cln_df.empty:
        cln_start_tuple = (cln_df.iloc[0]['lat'], cln_df.iloc[0]['lon'])

map_style = st.sidebar.selectbox(f"{L['render_style']}:", ["自動生成 想定コース幅（路面帯）", "OSM サーキットコース幅自動取得 (方法3)", "グラデーションカラー表示", "独自画像背景", "ESRI 衛星写真 (高画質)", "標準地図 (OSM)"])

auto_track_width = 9
auto_track_opacity = 0.25
auto_offset_x_int, auto_offset_y_int = 0, 0

if map_style == "自動生成 想定コース幅（路面帯）":
    auto_track_width = st.sidebar.slider(L['track_width'], 4, 30, int(saved_settings.get("auto_track_width", 9)), 1)
    auto_track_opacity = st.sidebar.slider(L['track_opacity'], 0.05, 0.80, float(saved_settings.get("auto_track_opacity", 0.25)), 0.05)
    st.sidebar.caption(f"全体コース位置 X / Y")
    auto_offset_x_int = st.sidebar.number_input(L['track_shift_x'], min_value=-200, max_value=200, value=int(saved_settings.get("auto_offset_x_int", 0)), step=1)
    auto_offset_y_int = st.sidebar.number_input(L['track_shift_y'], min_value=-200, max_value=200, value=int(saved_settings.get("auto_offset_y_int", 0)), step=1)

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
    st.sidebar.caption(f"コース図面調整")
    bg_offset_x_int = st.sidebar.number_input(L['offset_x'], min_value=-100, max_value=100, value=int(saved_settings.get("bg_offset_x_int", 0)), step=1)
    bg_offset_y_int = st.sidebar.number_input(L['offset_y'], min_value=-100, max_value=100, value=int(saved_settings.get("bg_offset_y_int", 0)), step=1)
    bg_scale_x = st.sidebar.number_input(L['scale_x'], value=float(saved_settings.get("bg_scale_x", 1.000)), min_value=0.100, max_value=5.000, step=0.010, format="%.3f")
    bg_scale_y = st.sidebar.number_input(L['scale_y'], value=float(saved_settings.get("bg_scale_y", 1.000)), min_value=0.100, max_value=5.000, step=0.010, format="%.3f")
    bg_opacity = st.sidebar.slider(L['opacity'], 0.10, 1.00, float(saved_settings.get("bg_opacity", 0.60)), 0.05)

default_split_pts = int(saved_settings.get("split_pts", 300))
split_pts = st.sidebar.number_input(L['min_pts'], min_value=50, max_value=2000, value=default_split_pts, step=50)

map_height_px = st.sidebar.slider(L['map_height_label'], 400, 1200, 680, 20)
marker_font_size = st.sidebar.slider(L['marker_text_size'], 10, 30, 14, 1)

col_gps_btn1, col_gps_btn2 = st.sidebar.columns(2)
with col_gps_btn1:
    auto_align = st.button(L['auto_gps'])
with col_gps_btn2:
    reset_gps_btn = st.button(L['reset_gps'])

# -----------------------------------------------------------------------------
# 6. マルチファイルパース ＆ 保存ラップの保持
# -----------------------------------------------------------------------------
if 'saved_kept_laps' not in st.session_state:
    st.session_state['saved_kept_laps'] = {}

if 'individual_lap_offsets' not in st.session_state:
    st.session_state['individual_lap_offsets'] = {}

files_sig = "|".join(sorted([f"{f.name}_{f.size}" for f in uploaded_files])) if uploaded_files else ""

if 'last_files_sig' not in st.session_state or st.session_state['last_files_sig'] != files_sig:
    st.session_state['last_files_sig'] = files_sig
    st.session_state['cached_raw_df'] = pd.DataFrame()

if uploaded_files and st.session_state['cached_raw_df'].empty:
    dfs_list = []
    if len(uploaded_files) >= 1 and all(f.name.lower().endswith('.dtb') for f in uploaded_files):
        total_files = len(uploaded_files)
        for f_idx, u_f in enumerate(uploaded_files):
            f_bytes = u_f.getvalue()
            single_df = parse_dtb_binary_cached(f_bytes, lap_idx=f_idx+1, total_files=total_files)
            if not single_df.empty:
                single_df['lap'] = f_idx + 1
                single_df['file_lap'] = True
                dfs_list.append(single_df)
        st.session_state['cached_raw_df'] = pd.concat(dfs_list, ignore_index=True) if dfs_list else pd.DataFrame()
    else:
        u_f = uploaded_files[0]
        fname = u_f.name.lower()
        f_bytes = u_f.getvalue()
        if fname.endswith('.bnx') or fname.endswith('.bnx4'):
            st.session_state['cached_raw_df'] = parse_bnx4_binary_cached(f_bytes)
        elif fname.endswith('.dtb'):
            raw_temp = parse_dtb_binary_cached(f_bytes, lap_idx=1, total_files=1)
            raw_temp['file_lap'] = True
            st.session_state['cached_raw_df'] = raw_temp
        elif fname.endswith('.nma') or fname.endswith('.nmea'):
            st.session_state['cached_raw_df'] = parse_nma_data(f_bytes)
        else:
            st.session_state['cached_raw_df'] = parse_csv_data(f_bytes)

raw_df = st.session_state['cached_raw_df']
df = None

if 'gps_aligned_flag' not in st.session_state:
    st.session_state['gps_aligned_flag'] = False

if reset_gps_btn:
    st.session_state['gps_aligned_flag'] = False
    st.session_state['cached_raw_df'] = pd.DataFrame()
    st.session_state['individual_lap_offsets'] = {}
    st.sidebar.info("GPS位置座標および個別オフセットを初期状態へリセットしました。")

if auto_align:
    st.session_state['gps_aligned_flag'] = True

if not raw_df.empty and 'lat' in raw_df.columns:
    if 'file_lap' in raw_df.columns:
        sessions = [raw_df]
    else:
        sessions = split_time_sessions(raw_df, gap_seconds=300)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{L['select_session']}**")
    
    session_options = []
    for idx, s_df in enumerate(sessions):
        start_t = s_df['time_str'].iloc[0] if 'time_str' in s_df.columns else "00:00:00"
        end_t = s_df['time_str'].iloc[-1] if 'time_str' in s_df.columns else "00:00:00"
        dur_m = len(s_df) * 0.05 / 60.0
        session_options.append(f"Group {idx+1}: [{start_t} 〜 {end_t}] ({dur_m:.1f}分走行)")
    
    selected_sessions = st.sidebar.multiselect("Sessions:", session_options, default=[session_options[0]] if session_options else [])
    
    if selected_sessions:
        selected_dfs = []
        for s_opt in selected_sessions:
            try:
                s_idx = int(s_opt.split(":")[0].replace("Group", "").strip()) - 1
                selected_dfs.append(sessions[s_idx])
            except: pass
        df = pd.concat(selected_dfs, ignore_index=True) if selected_dfs else raw_df.copy()
    else:
        df = raw_df.copy()

    st.sidebar.markdown("---")
    use_visual_start = st.sidebar.checkbox(L['visual_start'], value=(cln_start_tuple is not None))
    manual_start_tuple = cln_start_tuple
    
    if use_visual_start and not cln_start_tuple and df is not None and not df.empty and len(df) > 30:
        fast_df = df[df['speed_kmh'] > 10.0].reset_index(drop=True)
        if fast_df.empty: fast_df = df.reset_index(drop=True)
        
        max_sp_idx = fast_df['speed_kmh'].idxmax()
        
        hist, xedges, yedges = np.histogram2d(fast_df['lat'], fast_df['lon'], bins=40)
        max_bin = np.unravel_index(hist.argmax(), hist.shape)
        c_lat = (xedges[max_bin[0]] + xedges[max_bin[0]+1]) / 2.0
        c_lon = (yedges[max_bin[1]] + yedges[max_bin[1]+1]) / 2.0
        dists = np.sqrt((fast_df['lat'] - c_lat)**2 + (fast_df['lon'] - c_lon)**2)
        auto_c_idx = dists.idxmin()
        
        candidate_labels = [
            "候補 A: コントロールライン自動推定地点",
            "候補 B: 最高速メインストレート地点"
        ]
        selected_candidate = st.sidebar.selectbox(L['start_candidate_label'], candidate_labels)
        
        base_idx = auto_c_idx if "候補 A" in selected_candidate else max_sp_idx
        meter_offset = st.sidebar.slider(L['start_offset_label'], -100, 100, 0, 2)
        
        point_offset = int(meter_offset * 1.5)
        final_idx = (base_idx + point_offset) % len(fast_df)
        
        target_pt = fast_df.iloc[final_idx]
        manual_start_tuple = (target_pt['lat'], target_pt['lon'])

    if df is not None and not df.empty:
        df = process_lap_telemetry(df, min_pts=split_pts, manual_start=manual_start_tuple)
        if st.session_state.get('gps_aligned_flag', False):
            df = align_laps_entire_track(df, pth_paths=pth_paths)

# -----------------------------------------------------------------------------
# 7. メイン解析領域
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">CIRCUIT ANALYZE <span style="font-size:1.6rem; font-weight:200; opacity:0.6;">ver1.0</span></div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{L["title_sub"]}</div>', unsafe_allow_html=True)

if st.session_state['saved_kept_laps']:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{L['saved_laps_select']}**")
    selected_kept_keys = st.sidebar.multiselect("Kept Laps:", list(st.session_state['saved_kept_laps'].keys()))
    if selected_kept_keys and df is not None:
        kept_dfs = [st.session_state['saved_kept_laps'][k] for k in selected_kept_keys]
        max_existing_lap = df['lap'].max() if 'lap' in df.columns else 0
        for k_idx, k_df in enumerate(kept_dfs):
            k_df_copy = k_df.copy()
            k_df_copy['lap'] = max_existing_lap + k_idx + 1
            df = pd.concat([df, k_df_copy], ignore_index=True)

if df is not None and not df.empty and 'lat' in df.columns:
    if 'lap' not in df.columns:
        df['lap'] = 1
        
    lap_list = []
    for lap_no, group in df.groupby('lap'):
        if len(group) < 5: continue
        lap_sec = len(group) * 0.05
        max_sp = ceil_2(group['speed_kmh'].max())
        avg_sp = ceil_2(group['speed_kmh'].mean())
        
        if lap_sec < 5.0 or lap_sec > 600.0: continue
        
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
    
    if sum_df.empty:
        lap_sec = len(df) * 0.05
        sum_df = pd.DataFrame([{
            'Lap': 1,
            'StartTime': df['time_str'].iloc[0] if 'time_str' in df.columns else "00:00:00",
            'LapTime': format_lap_time(lap_sec),
            'RawSec': lap_sec,
            'MaxSpeed': ceil_2(df['speed_kmh'].max()),
            'AvgSpeed': ceil_2(df['speed_kmh'].mean()),
            'Points': len(df)
        }])
        df['lap'] = 1
    
    if not sum_df.empty:
        sum_df_sorted = sum_df.sort_values('RawSec').reset_index(drop=True)
        best_row = sum_df_sorted.iloc[0]
        best_lap_id = int(best_row['Lap'])

        available_laps = sum_df_sorted['Lap'].tolist()

        # 比較ラップ選択パネル
        st.markdown('<div class="toolbar-box">', unsafe_allow_html=True)
        st.markdown('<div class="toolbar-title">比較周回の選択 ＆ プリセット切り替え</div>', unsafe_allow_html=True)
        
        p_col1, p_col2, p_col3, p_col4 = st.columns([1, 1, 1, 3.5])
        
        if 'preset_select_mode' not in st.session_state:
            st.session_state['preset_select_mode'] = 'top10'

        with p_col1:
            if st.button("Fastest Top 5"):
                st.session_state['preset_select_mode'] = 'top5'
        with p_col2:
            if st.button("Fastest Top 10"):
                st.session_state['preset_select_mode'] = 'top10'
        with p_col3:
            if st.button("全選択解除"):
                st.session_state['preset_select_mode'] = 'clear'

        if st.session_state['preset_select_mode'] == 'top5':
            default_selection = available_laps[:5]
        elif st.session_state['preset_select_mode'] == 'clear':
            default_selection = []
        else:
            default_selection = available_laps[:10]

        selected_laps = st.multiselect(
            L['compare_laps'],
            options=available_laps,
            default=default_selection,
            format_func=lambda x: f"Lap {x} [{sum_df.loc[sum_df['Lap']==x, 'LapTime'].values[0]}] (時刻 {sum_df.loc[sum_df['Lap']==x, 'StartTime'].values[0]}) - 最高速 {sum_df.loc[sum_df['Lap']==x, 'MaxSpeed'].values[0]:.1f}km/h"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if len(selected_laps) > 10: selected_laps = selected_laps[:10]

        st.sidebar.markdown("---")
        st.sidebar.markdown("✏️ **LAP任意名 / ライダー名設定**")
        custom_names = {}
        loaded_custom_names = saved_settings.get("custom_names", {})
        
        for lap_id in selected_laps:
            default_val = loaded_custom_names.get(lap_id, loaded_custom_names.get(str(lap_id), f"Lap {lap_id}"))
            input_name = st.sidebar.text_input(f"Lap {lap_id} の名前:", value=default_val, key=f"custom_name_input_{lap_id}")
            custom_names[lap_id] = input_name if input_name.strip() else f"Lap {lap_id}"

        st.sidebar.markdown("---")
        st.sidebar.markdown("🎯 **LAP個別GPS位置微調整 (X/Y)**")
        
        if selected_laps:
            target_adjust_lap = st.sidebar.selectbox("調整対象のLAPを選択:", selected_laps, format_func=lambda x: f"Lap {x}")
            cur_offsets = st.session_state['individual_lap_offsets'].get(target_adjust_lap, (0.0, 0.0))
            
            adj_x = st.sidebar.slider(f"Lap {target_adjust_lap} 東西シフト (m)", -15.0, 15.0, float(cur_offsets[0] * 100000.0), 0.1)
            adj_y = st.sidebar.slider(f"Lap {target_adjust_lap} 南北シフト (m)", -15.0, 15.0, float(cur_offsets[1] * 100000.0), 0.1)
            
            st.session_state['individual_lap_offsets'][target_adjust_lap] = (adj_x / 100000.0, adj_y / 100000.0)

            if st.sidebar.button("🎯 選択LAPを基準ラインへ自動フィッティング"):
                df = auto_align_laps_to_ref(df, ref_lap_id=selected_laps[0])
                st.sidebar.success("全LAPの走行軌跡をベストラップラインへ自動フィッティング完了！")

        if selected_laps:
            center_lat, center_lon = df['lat'].mean(), df['lon'].mean()
            # 歪みを解消した回転処理
            df['rot_lat'], df['rot_lon'] = rotate_coordinates(df, rotation_angle, center_lat, center_lon)

            main_lap_id = selected_laps[0]
            sub_lap_id = selected_laps[1] if len(selected_laps) > 1 else None
            colors = cur_theme['colors']

            main_df = df[df['lap'] == main_lap_id].reset_index(drop=True)
            if main_df.empty:
                main_df = df.reset_index(drop=True)

            st.markdown('<div class="toolbar-box">', unsafe_allow_html=True)
            col_b1, col_b2, col_b3, col_b4 = st.columns([1.2, 1.2, 1.1, 1.1])
            
            with col_b1:
                st.markdown('<div class="toolbar-title">描画オプション</div>', unsafe_allow_html=True)
                show_pedal_points = st.checkbox(L['braking_points'], value=True)
                line_color_mode = st.selectbox(L['line_color_mode'], ["ラップ単色", "車速グラデーション", "ブレーキGグラデーション"])
                
            with col_b2:
                st.markdown('<div class="toolbar-title">表示モード</div>', unsafe_allow_html=True)
                hide_hud_panel = st.checkbox(L['toggle_hud'], value=False)
                view_mode = st.radio(L['view_mode'], ["全域表示", "ズーム追従"], index=0, horizontal=True)
                
            with col_b3:
                st.markdown('<div class="toolbar-title">比較軸設定</div>', unsafe_allow_html=True)
                x_axis_type = st.radio(L['trace_axis'], [L['dist_m'], L['time_s']], horizontal=True)
                
            with col_b4:
                st.markdown('<div class="toolbar-title">再生速度</div>', unsafe_allow_html=True)
                speed_factor = st.radio(L['replay_speed'], ["0.5x", "1.0x", "2.0x", "4.0x"], index=1, horizontal=True)

            st.markdown('</div>', unsafe_allow_html=True)

            base_stride = {"0.5x": 2, "1.0x": 4, "2.0x": 8, "4.0x": 16}[speed_factor]

            if not hide_hud_panel:
                col_map_half, col_trace_half = st.columns([4.5, 1.0])
            else:
                col_map_half = st.container()
                col_trace_half = None

            with col_map_half:
                cached_lap_data = {}
                max_lap_len = 0
                for idx, lap_id in enumerate(selected_laps):
                    l_df = df[df['lap'] == lap_id].reset_index(drop=True)
                    ind_off = st.session_state['individual_lap_offsets'].get(lap_id, (0.0, 0.0))
                    l_df['plot_x'] = l_df['rot_lon'] + auto_offset_x + ind_off[0]
                    l_df['plot_y'] = l_df['rot_lat'] + auto_offset_y + ind_off[1]
                    cached_lap_data[lap_id] = {
                        'df': l_df,
                        'color': colors[idx % len(colors)],
                        'name': custom_names.get(lap_id, f"Lap {lap_id}"),
                        'pos_str': TEXT_POSITIONS[idx % len(TEXT_POSITIONS)]
                    }
                    if len(l_df) > max_lap_len:
                        max_lap_len = len(l_df)

                def build_map_figure(is_zoomed=False, target_center=None, clicked_point=None):
                    fig = go.Figure()
                    base_count = 0

                    pth_width = max(1.5, auto_track_width / 2.0)

                    if pth_paths:
                        for pth_df in pth_paths:
                            pth_df['rot_lat'], pth_df['rot_lon'] = rotate_coordinates(pth_df, rotation_angle, center_lat, center_lon)
                            fig.add_trace(go.Scatter(
                                x=pth_df['rot_lon'] + auto_offset_x,
                                y=pth_df['rot_lat'] + auto_offset_y,
                                mode='lines', name="PTH Circuit Boundary",
                                line=dict(width=pth_width, color=cur_theme['pth_line']),
                                hoverinfo='skip', showlegend=False
                            ))
                            base_count += 1

                    if map_style == "自動生成 想定コース幅（路面帯）" and pth_paths:
                        best_lap_data = df[df['lap'] == int(best_row['Lap'])].reset_index(drop=True)
                        rgba_track = f"rgba(140, 160, 180, {auto_track_opacity})"
                        rgba_curb = f"rgba(255, 255, 255, {min(1.0, auto_track_opacity + 0.2)})"
                        
                        track_lon = best_lap_data['rot_lon'] + auto_offset_x
                        track_lat = best_lap_data['rot_lat'] + auto_offset_y

                        fig.add_trace(go.Scatter(
                            x=track_lon, y=track_lat,
                            mode='lines', name="Track Curb Edge",
                            line=dict(width=auto_track_width + 2, color=rgba_curb), hoverinfo='skip', showlegend=False
                        ))
                        fig.add_trace(go.Scatter(
                            x=track_lon, y=track_lat,
                            mode='lines', name="Track Width",
                            line=dict(width=auto_track_width, color=rgba_track), hoverinfo='skip', showlegend=False
                        ))
                        base_count += 2

                    for lap_id in selected_laps:
                        c_info = cached_lap_data[lap_id]
                        lap_data = c_info['df']
                        color = c_info['color']
                        label_name = c_info['name']

                        disp_lon = lap_data['plot_x']
                        disp_lat = lap_data['plot_y']

                        # 走行ライン
                        fig.add_trace(go.Scatter(
                            x=disp_lon, y=disp_lat,
                            mode='lines', name=f"{label_name}",
                            line=dict(width=4.0, color=color),
                            customdata=np.stack((lap_data.index, lap_data['speed_kmh'], lap_data['lean_angle_deg']), axis=-1),
                            hovertemplate="%{data.name}<br>速: %{customdata[1]:.1f}km/h | 傾: %{customdata[2]:.1f}°<extra></extra>"
                        ))
                        base_count += 1

                        if line_color_mode == "車速グラデーション":
                            fig.add_trace(go.Scatter(
                                x=disp_lon, y=disp_lat,
                                mode='markers', name=f"{label_name} (車速)",
                                marker=dict(size=5, color=lap_data['speed_kmh'], colorscale='Jet', showscale=False),
                                hoverinfo='skip', showlegend=False
                            ))
                            base_count += 1
                        elif line_color_mode == "ブレーキGグラデーション":
                            fig.add_trace(go.Scatter(
                                x=disp_lon, y=disp_lat,
                                mode='markers', name=f"{label_name} (減速G)",
                                marker=dict(size=5, color=np.abs(lap_data['accel_g']), colorscale='Reds', showscale=False),
                                hoverinfo='skip', showlegend=False
                            ))
                            base_count += 1

                        vmin_idx = lap_data['speed_kmh'].idxmin()
                        fig.add_trace(go.Scatter(
                            x=[disp_lon.iloc[vmin_idx]], y=[disp_lat.iloc[vmin_idx]],
                            mode='markers', marker=dict(size=7, color='#00ffff', symbol='diamond'),
                            name=f"{label_name} V-min", hoverinfo='text',
                            text=[f"{label_name} Bottom: {lap_data.iloc[vmin_idx]['speed_kmh']:.1f} km/h"], showlegend=False
                        ))
                        base_count += 1

                        if show_pedal_points and 'pedal_status' in lap_data.columns:
                            brake_mask = lap_data['pedal_status'] == 'Braking'
                            fig.add_trace(go.Scatter(
                                x=disp_lon[brake_mask], y=disp_lat[brake_mask],
                                mode='markers', name=f"{label_name} Brake",
                                marker=dict(size=8, color='#ff0055', symbol='circle', line=dict(width=2, color='#ffffff')),
                                showlegend=False, hoverinfo='text',
                                text=[f"{label_name} Brake | {ceil_2(sp):.2f} km/h" for sp in lap_data['speed_kmh'][brake_mask]]
                            ))
                            base_count += 1

                    if manual_start_tuple:
                        m_rot_lat, m_rot_lon = rotate_coordinates(
                            pd.DataFrame([{'lat': manual_start_tuple[0], 'lon': manual_start_tuple[1]}]),
                            rotation_angle, center_lat, center_lon
                        )
                        fig.add_trace(go.Scatter(
                            x=m_rot_lon + auto_offset_x, y=m_rot_lat + auto_offset_y,
                            mode='markers+text',
                            marker=dict(size=22, color='#ffcc00', symbol='hexagram', line=dict(width=3, color='#000000')),
                            text=[" CONTROL LINE (.cln)"] if cln_start_tuple else [" START LINE"], textposition="top center",
                            textfont=dict(size=16, color='#ffcc00'),
                            name="Start Marker", showlegend=False
                        ))

                    if cln_df is not None and len(cln_df) >= 2:
                        cln_rot_df = cln_df.copy()
                        cln_rot_df['rot_lat'], cln_rot_df['rot_lon'] = rotate_coordinates(cln_rot_df, rotation_angle, center_lat, center_lon)
                        fig.add_trace(go.Scatter(
                            x=cln_rot_df['rot_lon'] + auto_offset_x, y=cln_rot_df['rot_lat'] + auto_offset_y,
                            mode='lines+markers', name="Control Line Gate",
                            line=dict(width=4, color='#ff9900', dash='dot'),
                            marker=dict(size=10, color='#ffcc00'), showlegend=False
                        ))

                    init_x, init_y, init_text, init_colors = [], [], [], []
                    for lap_id in selected_laps:
                        c_info = cached_lap_data[lap_id]
                        pt0 = c_info['df'].iloc[0]
                        init_x.append(pt0['plot_x'])
                        init_y.append(pt0['plot_y'])
                        init_text.append(f" {c_info['name']}: {ceil_2(pt0['speed_kmh']):.1f}km/h")
                        init_colors.append(c_info['color'])

                    fig.add_trace(go.Scatter(
                        x=init_x, y=init_y,
                        mode='markers+text',
                        marker=dict(size=14, color=init_colors, line=dict(width=2, color='#ffffff')),
                        text=init_text,
                        textfont=dict(size=marker_font_size, color=init_colors),
                        textposition="top right",
                        name="All Bikes",
                        showlegend=False
                    ))
                    animated_trace_idx = len(fig.data) - 1

                    frames = []
                    for f_idx in range(0, max_lap_len, base_stride):
                        cur_x, cur_y, cur_text = [], [], []
                        for lap_id in selected_laps:
                            c_info = cached_lap_data[lap_id]
                            ldf = c_info['df']
                            pos = min(f_idx, len(ldf) - 1)
                            pt = ldf.iloc[pos]
                            cur_x.append(pt['plot_x'])
                            cur_y.append(pt['plot_y'])
                            cur_text.append(f" {c_info['name']}: {ceil_2(pt['speed_kmh']):.1f}km/h")

                        frames.append(go.Frame(
                            data=[go.Scatter(
                                x=cur_x, y=cur_y,
                                mode='markers+text',
                                text=cur_text,
                                marker=dict(size=14, color=init_colors, line=dict(width=2, color='#ffffff')),
                                textfont=dict(size=marker_font_size, color=init_colors),
                                textposition="top right"
                            )],
                            name=str(f_idx),
                            traces=[animated_trace_idx]
                        ))

                    fig.frames = frames

                    if clicked_point is not None:
                        fig.add_trace(go.Scatter(
                            x=[clicked_point['rot_lon'] + auto_offset_x], y=[clicked_point['rot_lat'] + auto_offset_y],
                            mode='markers',
                            marker=dict(size=18, color='#ffff00', symbol='star', line=dict(width=2, color='#000000')),
                            name="Selected Point", showlegend=False
                        ))

                    # 緯度経度のアスペクト比補正係数
                    lat_rad = np.radians(center_lat)
                    aspect_scaleratio = float(np.cos(lat_rad))

                    layout_kwargs = dict(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                        font=dict(color=cur_theme['text']), height=map_height_px if not is_zoomed else 320,
                        # X軸をY軸に完全拘束して回転時も一切歪まないよう固定
                        xaxis=dict(showgrid=True, gridcolor=cur_theme['grid'], scaleanchor="y", scaleratio=aspect_scaleratio),
                        yaxis=dict(showgrid=True, gridcolor=cur_theme['grid']),
                        margin=dict(l=5, r=5, t=35, b=5),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        updatemenus=[dict(
                            type="buttons", showactive=False, x=0.01, y=0.99,
                            buttons=[
                                dict(
                                    label="▶ PLAY",
                                    method="animate",
                                    args=[None, {
                                        "frame": {"duration": 30, "redraw": False},
                                        "fromcurrent": True,
                                        "transition": {"duration": 0}
                                    }]
                                ),
                                dict(
                                    label="⏸ PAUSE",
                                    method="animate",
                                    args=[[None], {
                                        "frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}
                                    }]
                                )
                            ]
                        )]
                    )

                    if is_zoomed and target_center is not None:
                        zoom_span = 0.0006
                        layout_kwargs["xaxis"]["range"] = [target_center[0] - zoom_span, target_center[0] + zoom_span]
                        layout_kwargs["yaxis"]["range"] = [target_center[1] - zoom_span, target_center[1] + zoom_span]

                    fig.update_layout(**layout_kwargs)
                    return fig

                fig_map = build_map_figure(is_zoomed=False)
                st.plotly_chart(fig_map, use_container_width=True, config=COMMON_PLOTLY_CONFIG)

            if not hide_hud_panel and col_trace_half is not None:
                with col_trace_half:
                    st.markdown(f"##### {L['hud_title']}")
                    
                    hud_cols = st.columns(2)
                    for idx, lap_id in enumerate(selected_laps):
                        row = sum_df[sum_df['Lap'] == lap_id].iloc[0]
                        color = colors[idx % len(colors)]
                        label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                        
                        lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                        sync_pt = lap_data.iloc[0]
                        lean_deg = sync_pt['lean_angle_deg'] if 'lean_angle_deg' in sync_pt else 0.0
                        
                        target_col = hud_cols[idx % 2]
                        with target_col:
                            st.markdown(f"""
                            <div class="metric-card-slim" style="border-left: 4px solid {color}; margin-bottom: 6px;">
                                <div class="metric-title-slim" style="color:{color};">{label_name}</div>
                                <div class="metric-value-slim">[{row['LapTime']}]</div>
                                <div class="metric-unit-slim">最高速 {row['MaxSpeed']:.1f} km/h</div>
                                <div class="metric-unit-slim" style="opacity:0.75;">({ceil_2(sync_pt['speed_kmh']):.1f}km/h | {lean_deg:.0f}°)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("キープ", key=f"keep_lap_{lap_id}"):
                                keep_name = f"{label_name} [{row['LapTime']}] ({row['StartTime']})"
                                st.session_state['saved_kept_laps'][keep_name] = lap_data
                                st.success("保存完了")

            # -----------------------------------------------------------------
            # 8. 車速・デルタトレース ＆ G-G Diagram ＆ 詳細分析レポート
            # -----------------------------------------------------------------
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
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                margin=dict(l=10, r=10, t=35, b=10)
            )
            st.plotly_chart(fig_speed, use_container_width=True, config=COMMON_PLOTLY_CONFIG)

            col_delta_half, col_gg_half = st.columns([1.0, 1.0])

            with col_delta_half:
                st.markdown(f"### {L['delta_traces']}")
                fig_delta = go.Figure()
                
                best_lap_df = df[df['lap'] == best_lap_id].reset_index(drop=True)
                best_cum_time = np.arange(len(best_lap_df)) * 0.05
                best_cum_dist = np.cumsum(best_lap_df['speed_kmh'] / 3.6 * 0.05)

                for idx, lap_id in enumerate(selected_laps):
                    lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                    color = colors[idx % len(colors)]
                    label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                    
                    lap_cum_dist = np.cumsum(lap_data['speed_kmh'] / 3.6 * 0.05)
                    lap_cum_time = np.arange(len(lap_data)) * 0.05
                    
                    interp_best_time = np.interp(lap_cum_dist, best_cum_dist, best_cum_time)
                    delta_sec = lap_cum_time - interp_best_time
                    
                    fig_delta.add_trace(go.Scatter(
                        x=lap_cum_dist, y=delta_sec,
                        mode='lines', name=f"{label_name} Delta",
                        line=dict(width=2.0, color=color),
                        hovertemplate="距離: %{x:.1f}m | タイム差: %{y:+.3f}秒<extra></extra>"
                    ))

                if len(best_cum_dist) > 0:
                    fig_delta.add_shape(type="line", x0=0, y0=0, x1=max(best_cum_dist), y1=0, line=dict(color=cur_theme['text'], width=1, dash="dash"))
                fig_delta.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                    font=dict(color=cur_theme['text']), height=280,
                    xaxis=dict(title=L['dist_m'], showgrid=True, gridcolor=cur_theme['grid']),
                    yaxis=dict(title="Delta (sec)", showgrid=True, gridcolor=cur_theme['grid']),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=35, b=10)
                )
                st.plotly_chart(fig_delta, use_container_width=True, config=COMMON_PLOTLY_CONFIG)

            with col_gg_half:
                st.markdown(f"### {L['gg_diagram']}")
                fig_gg = go.Figure()
                
                for idx, lap_id in enumerate(selected_laps):
                    lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                    color = colors[idx % len(colors)]
                    label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                    
                    fig_gg.add_trace(go.Scatter(
                        x=lap_data['cornering_g'], y=lap_data['accel_g'],
                        mode='markers', name=label_name,
                        marker=dict(size=4, color=color, opacity=0.6),
                        hovertemplate="横G: %{x:+.2f}G | 縦G: %{y:+.2f}G<extra></extra>"
                    ))

                theta = np.linspace(0, 2*np.pi, 100)
                fig_gg.add_trace(go.Scatter(
                    x=1.0*np.cos(theta), y=1.0*np.sin(theta),
                    mode='lines', name="1.0G Limit Circle",
                    line=dict(color=cur_theme['text'], dash="dash", width=1.5),
                    showlegend=False, hoverinfo='skip'
                ))

                fig_gg.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                    font=dict(color=cur_theme['text']), height=280,
                    xaxis=dict(title="横G (コーナリングG)", showgrid=True, gridcolor=cur_theme['grid'], range=[-1.5, 1.5]),
                    yaxis=dict(title="縦G (加減速G)", showgrid=True, gridcolor=cur_theme['grid'], range=[-1.5, 1.5]),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=35, b=10)
                )
                st.plotly_chart(fig_gg, use_container_width=True, config=COMMON_PLOTLY_CONFIG)

            st.markdown(f"### {L['sector_analysis']}")
            sec_rows = []
            for lap_id in selected_laps:
                ldf = df[df['lap'] == lap_id].reset_index(drop=True)
                n_pts = len(ldf)
                s1_df = ldf.iloc[:n_pts//3]
                s2_df = ldf.iloc[n_pts//3 : 2*n_pts//3]
                s3_df = ldf.iloc[2*n_pts//3:]
                
                s1_t = len(s1_df) * 0.05
                s2_t = len(s2_df) * 0.05
                s3_t = len(s3_df) * 0.05
                
                brake_pct = (len(ldf[ldf['pedal_status'] == 'Braking']) / n_pts) * 100.0 if n_pts > 0 else 0.0
                accel_pct = (len(ldf[ldf['pedal_status'] == 'Accel']) / n_pts) * 100.0 if n_pts > 0 else 0.0
                
                sec_rows.append({
                    "Lap": custom_names.get(lap_id, f"Lap {lap_id}"),
                    "S1 (秒)": f"{s1_t:.3f}",
                    "S2 (秒)": f"{s2_t:.3f}",
                    "S3 (秒)": f"{s3_t:.3f}",
                    "Total (秒)": f"{(s1_t+s2_t+s3_t):.3f}",
                    "Max Speed": f"{ldf['speed_kmh'].max():.2f} km/h",
                    "Bottom Speed": f"{ldf['speed_kmh'].min():.2f} km/h",
                    "Accel率 (%)": f"{accel_pct:.1f}%",
                    "Brake率 (%)": f"{brake_pct:.1f}%",
                    "Max Lean": f"{ldf['lean_angle_deg'].abs().max():.1f}°"
                })
            
            report_df = pd.DataFrame(sec_rows)
            st.dataframe(report_df, use_container_width=True)

            csv_report_bytes = report_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label=L['report_export'],
                data=csv_report_bytes,
                file_name="circuit_analysis_report.csv",
                mime="text/csv"
            )

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

elif pth_paths:
    st.info("コース形状データ (.pth) が読み込まれました。")
    all_pth_pts = pd.concat(pth_paths, ignore_index=True)
    c_lat, c_lon = all_pth_pts['lat'].mean(), all_pth_pts['lon'].mean()
    
    fig_pth_only = go.Figure()
    pth_width = max(1.0, auto_track_width / 2.0)
    for pth_df in pth_paths:
        pth_df['rot_lat'], pth_df['rot_lon'] = rotate_coordinates(pth_df, rotation_angle, c_lat, c_lon)
        fig_pth_only.add_trace(go.Scatter(
            x=pth_df['rot_lon'] + auto_offset_x,
            y=pth_df['rot_lat'] + auto_offset_y,
            mode='lines', name="PTH Circuit Boundary",
            line=dict(width=pth_width, color=cur_theme['pth_line']),
            hoverinfo='skip', showlegend=False
        ))
    
    if cln_df is not None and not cln_df.empty:
        cln_rot_df = cln_df.copy()
        cln_rot_df['rot_lat'], cln_rot_df['rot_lon'] = rotate_coordinates(cln_rot_df, rotation_angle, c_lat, c_lon)
        fig_pth_only.add_trace(go.Scatter(
            x=cln_rot_df['rot_lon'] + auto_offset_x, y=cln_rot_df['rot_lat'] + auto_offset_y,
            mode='lines+markers', name="Control Line Gate",
            line=dict(width=4, color='#ff9900', dash='dot'),
            marker=dict(size=10, color='#ffcc00'), showlegend=False
        ))

    lat_rad = np.radians(c_lat)
    aspect_scaleratio = float(np.cos(lat_rad))

    fig_pth_only.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
        font=dict(color=cur_theme['text']), height=map_height_px,
        xaxis=dict(showgrid=False, visible=False, scaleanchor="y", scaleratio=aspect_scaleratio),
        yaxis=dict(showgrid=False, visible=False),
        margin=dict(l=5, r=5, t=35, b=5)
    )
    st.plotly_chart(fig_pth_only, use_container_width=True, config=COMMON_PLOTLY_CONFIG)

else:
    st.info(L['drop_info'])