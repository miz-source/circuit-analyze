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
import io
import base64
from PIL import Image

# -----------------------------------------------------------------------------
# 1. ページ基本設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CIRCUIT ANALYZE ver2.0",
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
        "circuit_bg": "サーキット背景画像 (.png / .jpg)",
        "render_style": "描画背景タイプ",
        "track_width": "想定コース幅 (ピクセル)",
        "track_opacity": "想定コース透明度",
        "track_shift_x": "全体コース位置 X (東西シフト)",
        "track_shift_y": "全体コース位置 Y (南北シフト)",
        "scale_adjust": "スケール・比率調整 (倍率)",
        "scale_x": "横幅倍率 (Scale X)",
        "scale_y": "縦幅倍率 (Scale Y)",
        "north_rotation": "北基準回転角度 (°)",
        "bg_shift": "コース図面画像の位置・比率調整",
        "offset_x": "位置 X (東西)",
        "offset_y": "位置 Y (南北)",
        "opacity": "透明度",
        "lap_time_range": "有効周回タイム許容範囲 (秒: 最小〜最大)",
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
        "drop_info": "左側のサイドバーから .bnx / .bnx4 / .dtb / .csv / .nma 走行ログをドロップしてください。",
        "dist_m": "走行距離 (m)",
        "time_s": "経過時間 (秒)",
        "speed_kmh": "車速 (km/h)",
        "lean_deg": "バンク角",
        "report_export": "全テレメトリー比較レポート (CSV) をダウンロード",
        "bg_map_opacity": "背景写真 / 地図透明度"
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
        "circuit_bg": "Circuit Track Image (.png / .jpg)",
        "render_style": "Track Render Style",
        "track_width": "Track Width (px)",
        "track_opacity": "Track Opacity",
        "track_shift_x": "Track Shift X (East-West)",
        "track_shift_y": "Track Shift Y (North-South)",
        "scale_adjust": "Scale & Ratio Adjust",
        "scale_x": "Scale X",
        "scale_y": "Scale Y",
        "north_rotation": "North Align Rotation (°)",
        "bg_shift": "Image Offset & Scale Adjust",
        "offset_x": "Offset X (East-West)",
        "offset_y": "Offset Y (North-South)",
        "opacity": "Opacity",
        "lap_time_range": "Valid Lap Time Range (sec: Min - Max)",
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
        "drop_info": "DROP .BNX, .BNX4, .DTB, .CSV, OR .NMA TELEMETRY FILES FROM SIDEBAR.",
        "dist_m": "Distance (m)",
        "time_s": "Time (s)",
        "speed_kmh": "Speed (km/h)",
        "lean_deg": "Lean",
        "report_export": "Export Full Telemetry Report (CSV)",
        "bg_map_opacity": "Satellite / Map Opacity"
    }
}

THEMES = {
    "Dark (夜間解析用)": {
        "bg_app": "#040806", "bg_panel": "#09120e", "bg_card": "#0d1a14",
        "border": "#1b3a2b", "text": "#e2e8f0", "subtext": "#94a3b8", "accent": "#00ff66", "pth_line": "rgba(160, 180, 200, 0.5)",
        "plot_bg": "#06110b", "grid": "#13281c",
        "drop_bg": "#14231b", "drop_border": "#27543d",
        "colors": ["#00f2fe", "#ff2a5f", "#00ff88", "#ffb703", "#a855f7", "#00ff66", "#f43f5e", "#06b6d4", "#eab308", "#ec4899"]
    },
    "High Contrast (日中日陰用)": {
        "bg_app": "#ffffff", "bg_panel": "#f1f5f9", "bg_card": "#e2e8f0",
        "border": "#94a3b8", "text": "#000000", "subtext": "#334155", "accent": "#1d4ed8", "pth_line": "rgba(15, 23, 42, 0.9)",
        "plot_bg": "#f8fafc", "grid": "#cbd5e1",
        "drop_bg": "#e2e8f0", "drop_border": "#64748b",
        "colors": ["#1d4ed8", "#dc2626", "#15803d", "#c2410c", "#7e22ce", "#0369a1", "#a16207", "#be123c", "#3730a3", "#047857"]
    }
}

TEXT_POSITIONS = ["top right", "top left", "bottom right", "bottom left", "top center", "bottom center", "middle right", "middle left"]

def ceil_2(val):
    if pd.isna(val) or val is None: return 0.0
    return math.ceil(val * 100.0) / 100.0

# -----------------------------------------------------------------------------
# 3. 衛星写真・地図タイル取得
# -----------------------------------------------------------------------------
def deg2num(lat_deg, lon_deg, zoom):
    lat_deg = max(-85.0511, min(85.0511, lat_deg))
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

@st.cache_data(show_spinner=False)
def fetch_raw_stitched_map(min_lat_q, max_lat_q, min_lon_q, max_lon_q, provider="ESRI 衛星写真 (高画質)"):
    tile_urls = {
        "ESRI 衛星写真 (高画質)": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "標準地図 (OSM)": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "国土地理院写真": "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg"
    }
    url_template = tile_urls.get(provider, tile_urls["ESRI 衛星写真 (高画質)"])
    zoom = 16
    
    x_min, y_min = deg2num(max_lat_q, min_lon_q, zoom)
    x_max, y_max = deg2num(min_lat_q, max_lon_q, zoom)
    
    if abs(x_max - x_min) > 5 or abs(y_max - y_min) > 5:
        zoom = 15
        x_min, y_min = deg2num(max_lat_q, min_lon_q, zoom)
        x_max, y_max = deg2num(min_lat_q, max_lon_q, zoom)

    width_tiles = max(1, (x_max - x_min) + 1)
    height_tiles = max(1, (y_max - y_min) + 1)
    
    stitched_img = Image.new('RGB', (width_tiles * 256, height_tiles * 256), color=(20, 25, 20))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CircuitAnalyzer/2.0'}
    
    success_count = 0
    for i, x in enumerate(range(x_min, x_max + 1)):
        for j, y in enumerate(range(y_min, y_max + 1)):
            url = url_template.format(z=zoom, x=x, y=y)
            try:
                res = requests.get(url, headers=headers, timeout=2.5)
                if res.status_code == 200:
                    tile = Image.open(io.BytesIO(res.content))
                    stitched_img.paste(tile, (i * 256, j * 256))
                    success_count += 1
            except Exception:
                pass

    if success_count == 0:
        return None, 0, 0, 0, 0

    top_lat, left_lon = num2deg(x_min, y_min, zoom)
    bottom_lat, right_lon = num2deg(x_max + 1, y_max + 1, zoom)
    stitched_img.thumbnail((750, 750), Image.BILINEAR)
    
    return stitched_img, top_lat, bottom_lat, left_lon, right_lon

def get_processed_map_image(min_lat, max_lat, min_lon, max_lon, provider, rotation_deg, center_lat, center_lon):
    min_lat_q = round(min_lat, 4)
    max_lat_q = round(max_lat, 4)
    min_lon_q = round(min_lon, 4)
    max_lon_q = round(max_lon, 4)

    stitched_img, top_lat, bottom_lat, left_lon, right_lon = fetch_raw_stitched_map(
        min_lat_q, max_lat_q, min_lon_q, max_lon_q, provider
    )
    if stitched_img is None:
        return None, 0, 0, 0, 0

    if rotation_deg != 0.0:
        corners_df = pd.DataFrame([
            {'lat': top_lat, 'lon': left_lon},
            {'lat': top_lat, 'lon': right_lon},
            {'lat': bottom_lat, 'lon': right_lon},
            {'lat': bottom_lat, 'lon': left_lon}
        ])
        rot_lat, rot_lon = rotate_coordinates(corners_df, rotation_deg, center_lat, center_lon)
        min_x, max_x = rot_lon.min(), rot_lon.max()
        min_y, max_y = rot_lat.min(), rot_lat.max()
        
        rgba_img = stitched_img.convert('RGBA')
        final_img = rgba_img.rotate(rotation_deg, resample=Image.BILINEAR, expand=True)
    else:
        min_x, max_x = left_lon, right_lon
        min_y, max_y = bottom_lat, top_lat
        final_img = stitched_img

    buf = io.BytesIO()
    final_img.save(buf, format="PNG", optimize=True)
    b64_str = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return b64_str, min_x, max_y, (max_x - min_x), (max_y - min_y)

# -----------------------------------------------------------------------------
# 4. 高精度データパーサー (全サーキット対応 20Hz抽出)
# -----------------------------------------------------------------------------
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
                    except Exception:
                        pass
            if len(pts) >= 2:
                paths.append(pd.DataFrame(pts))
    except Exception:
        pass
    return paths

def decode_extended_float(chunk_10b):
    try:
        mantissa = struct.unpack('<Q', chunk_10b[:8])[0]
        exp_sign = struct.unpack('<H', chunk_10b[8:10])[0]
        sign = -1.0 if (exp_sign & 0x8000) else 1.0
        exp = (exp_sign & 0x7FFF) - 16383
        if exp == -16383: return 0.0
        return sign * (mantissa / (2**63)) * (2**exp)
    except Exception:
        return 0.0

@st.cache_data
def parse_bnx4_binary_cached(data_bytes):
    records = []
    length = len(data_bytes)
    
    lat_min, lat_max = 30.0, 45.0
    lon_min, lon_max = 128.0, 145.0
    
    sync_sig = b'*+\xbb\xbb\xbb\xbb'
    sig_len = len(sync_sig)
    
    pos = 0
    indices = []
    while True:
        idx = data_bytes.find(sync_sig, pos)
        if idx == -1:
            break
        indices.append(idx)
        pos = idx + sig_len

    if len(indices) >= 5:
        for k in range(len(indices)):
            curr_idx = indices[k]
            next_idx = indices[k+1] if k + 1 < len(indices) else min(curr_idx + 256, length)
            chunk = data_bytes[curr_idx:next_idx]
            chunk_len = len(chunk)
            
            off = 0
            while off + 16 <= chunk_len:
                try:
                    d1 = struct.unpack('<d', chunk[off:off+8])[0]
                    d2 = struct.unpack('<d', chunk[off+8:off+16])[0]
                    
                    lat, lon = None, None
                    if lat_min <= d1 <= lat_max and lon_min <= d2 <= lon_max:
                        lat, lon = d1, d2
                    elif lat_min <= d2 <= lat_max and lon_min <= d1 <= lon_max:
                        lat, lon = d2, d1
                        
                    if lat is not None and lon is not None:
                        speed = 0.0
                        for s_off in [off - 4, off + 16, off - 8, off + 20]:
                            if 0 <= s_off <= chunk_len - 4:
                                try:
                                    f_spd = struct.unpack('<f', chunk[s_off:s_off+4])[0]
                                    if 0.5 <= f_spd <= 300.0:
                                        speed = f_spd
                                        break
                                except Exception:
                                    pass
                                    
                        records.append({
                            'lat': lat,
                            'lon': lon,
                            'speed_kmh': float(speed),
                            'elevation_m': 0.0,
                            'orig_idx': len(records)
                        })
                        off += 16
                        continue
                except Exception:
                    pass
                off += 2
    else:
        stride = 128
        pos = 0
        while pos + stride <= length:
            chunk = data_bytes[pos:pos + stride]
            try:
                d32 = struct.unpack('<d', chunk[32:40])[0]
                d48 = struct.unpack('<d', chunk[48:56])[0]
                lat, lon = None, None
                if lat_min <= d32 <= lat_max and lon_min <= d48 <= lon_max:
                    lat, lon = d32, d48
                elif lat_min <= d48 <= lat_max and lon_min <= d32 <= lon_max:
                    lat, lon = d48, d32
                if lat and lon:
                    records.append({'lat': lat, 'lon': lon, 'speed_kmh': 0.0, 'elevation_m': 0.0, 'orig_idx': len(records)})
            except Exception:
                pass
            pos += stride

    df_res = pd.DataFrame(records)
    if not df_res.empty:
        total_pts = len(df_res)
        dt = 0.05

        d_lat = np.radians(np.gradient(df_res['lat']))
        d_lon = np.radians(np.gradient(df_res['lon']))
        a = np.sin(d_lat / 2)**2 + np.cos(np.radians(df_res['lat'])) * np.sin(d_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(np.clip(1 - a, 0, 1)))
        dist_m = 6371000.0 * c
        calc_spd = np.clip(dist_m / dt * 3.6, 0.0, 300.0)

        if df_res['speed_kmh'].max() < 5.0 or (df_res['speed_kmh'] > 280.0).sum() > total_pts * 0.05:
            df_res['speed_kmh'] = pd.Series(calc_spd).rolling(5, min_periods=1, center=True).median().values
        else:
            df_res['speed_kmh'] = df_res['speed_kmh'].rolling(3, min_periods=1, center=True).median().clip(0.0, 300.0).values

        start_t = datetime.datetime.now().replace(hour=10, minute=0, second=0)
        df_res['time_str'] = [(start_t + datetime.timedelta(seconds=idx * dt)).strftime("%H:%M:%S") for idx in range(total_pts)]

    return df_res

@st.cache_data
def parse_dtb_binary_cached(data_bytes, lap_idx=1, total_files=1):
    records = []
    length = len(data_bytes)
    stride = 36
    i = 0
    while i + stride <= length:
        chunk = data_bytes[i:i + stride]
        try:
            lat = struct.unpack('<d', chunk[8:16])[0]
            lon = struct.unpack('<d', chunk[16:24])[0]
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and abs(lat) > 1.0:
                speed = struct.unpack('<f', chunk[0:4])[0]
                records.append({
                    'lat': lat,
                    'lon': lon,
                    'speed_kmh': max(0.0, float(speed)),
                    'elevation_m': 0.0,
                    'orig_idx': i // stride
                })
        except Exception:
            pass
        i += stride

    df_res = pd.DataFrame(records)
    if not df_res.empty:
        total_pts = len(df_res)
        df_res['time_str'] = [(datetime.datetime.now() + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(total_pts)]
    return df_res

def parse_nma_text_stream(text):
    records = []
    pattern = re.compile(r'\$(?:GP|GN|GL|GA|BD|QZ)RMC,([0-9.]+),([AV]),([0-9.]+),([NS]),([0-9.]+),([EW]),([0-9.]*)', re.IGNORECASE)
    for m in pattern.finditer(text):
        t_raw, status, lat_raw, ns, lon_raw, ew, spd_raw = m.groups()
        if status.upper() == 'A':
            try:
                lat_val = float(lat_raw)
                lon_val = float(lon_raw)
                lat = int(lat_val / 100) + (lat_val % 100) / 60.0
                if ns.upper() == 'S': lat = -lat
                lon = int(lon_val / 100) + (lon_val % 100) / 60.0
                if ew.upper() == 'W': lon = -lon

                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and abs(lat) > 1.0:
                    speed = float(spd_raw) * 1.852 if spd_raw else 0.0
                    t_str = f"{t_raw[0:2]}:{t_raw[2:4]}:{t_raw[4:6]}" if len(t_raw) >= 6 else "00:00:00"
                    records.append({
                        'lat': lat,
                        'lon': lon,
                        'speed_kmh': speed,
                        'time_str': t_str
                    })
            except Exception:
                continue

    if len(records) >= 10:
        return pd.DataFrame(records)
    return pd.DataFrame()

def parse_csv_data(data_bytes):
    try:
        try:
            df = pd.read_csv(pd.io.common.BytesIO(data_bytes))
            if len(df.columns) < 2:
                df = pd.read_csv(pd.io.common.BytesIO(data_bytes), sep=r'\s+')
        except Exception:
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
            df['time_str'] = [(start_t + datetime.timedelta(seconds=idx * 0.05)).strftime("%H:%M:%S") for idx in range(len(df))]
        return df
    except Exception:
        return pd.DataFrame()

def auto_detect_and_parse(f_bytes, fname):
    fname_lower = fname.lower()

    if fname_lower.endswith('.bnx4') or fname_lower.endswith('.bnx'):
        df = parse_bnx4_binary_cached(f_bytes)
        if not df.empty and len(df) >= 10:
            return df

    elif fname_lower.endswith('.nma'):
        text_content = f_bytes.decode('utf-8', errors='ignore')
        df = parse_nma_text_stream(text_content)
        if not df.empty and len(df) >= 10:
            return df

    elif fname_lower.endswith('.dtb'):
        df = parse_dtb_binary_cached(f_bytes)
        if not df.empty and len(df) >= 10:
            return df

    df_bnx = parse_bnx4_binary_cached(f_bytes)
    if not df_bnx.empty and len(df_bnx) >= 10:
        return df_bnx

    if b'$G' in f_bytes[:4096]:
        text_content = f_bytes.decode('utf-8', errors='ignore')
        df_nma = parse_nma_text_stream(text_content)
        if not df_nma.empty and len(df_nma) >= 10:
            return df_nma

    df_dtb = parse_dtb_binary_cached(f_bytes)
    if not df_dtb.empty and len(df_dtb) >= 10:
        return df_dtb

    return parse_csv_data(f_bytes)

def split_time_sessions(df, gap_seconds=300):
    if df is None or df.empty: return [df]
    idx_diff = np.diff(df.index)
    session_cuts = np.where(idx_diff > (gap_seconds * 20))[0]

    sessions = []
    start_idx = 0
    for cut in session_cuts:
        sess = df.iloc[start_idx:cut + 1].copy()
        if len(sess) >= 10:
            sessions.append(sess)
        start_idx = cut + 1
    last_sess = df.iloc[start_idx:].copy()
    if len(last_sess) >= 10:
        sessions.append(last_sess)

    return sessions if sessions else [df]

# -----------------------------------------------------------------------------
# 5. 周回カット・仮想コントロールライン横断判定 (20Hz同期)
# -----------------------------------------------------------------------------
def process_lap_telemetry(df, min_seconds=20.0, manual_start=None):
    if df is None or df.empty or 'lat' not in df.columns or len(df) < 5:
        if df is not None and not df.empty and 'lap' not in df.columns:
            df['lap'] = 1
        return df

    dt = 0.05

    speed_ms = df['speed_kmh'] / 3.6
    accel_m_s2 = np.gradient(speed_ms, dt)
    df['accel_g'] = np.clip(accel_m_s2 / 9.80665, -1.8, 1.8)

    d_lat = np.gradient(df['lat'])
    d_lon = np.gradient(df['lon'])
    heading = np.arctan2(d_lon, d_lat)
    d_heading = np.gradient(heading)
    d_heading = (d_heading + np.pi) % (2 * np.pi) - np.pi
    omega = d_heading / dt
    a_lat = speed_ms * omega
    df['cornering_g'] = np.clip(a_lat / 9.80665, -1.8, 1.8)
    df['lean_angle_deg'] = np.degrees(np.arctan(df['cornering_g']))

    conditions = [(df['accel_g'] < -0.15), (df['accel_g'] > 0.12)]
    choices = ['Braking', 'Accel']
    df['pedal_status'] = np.select(conditions, choices, default='Coasting')

    # スタートライン地点と進行方向ベクトルの決定
    if manual_start and manual_start[0] != 0.0:
        start_lat, start_lon = manual_start[0], manual_start[1]
        near_idx = np.argmin((df['lat'] - start_lat)**2 + (df['lon'] - start_lon)**2)
        dir_lat = d_lat[near_idx]
        dir_lon = d_lon[near_idx]
    else:
        # 周回数の多い本コース上の高頻度高速通過エリア（メインストレート）を抽出
        sp_cut = max(25.0, df['speed_kmh'].max() * 0.45)
        fast_mask = df['speed_kmh'] > sp_cut
        fast_df = df[fast_mask]
        if not fast_df.empty:
            hist, xedges, yedges = np.histogram2d(fast_df['lat'], fast_df['lon'], bins=40)
            max_bin = np.unravel_index(hist.argmax(), hist.shape)
            start_lat = (xedges[max_bin[0]] + xedges[max_bin[0] + 1]) / 2.0
            start_lon = (yedges[max_bin[1]] + yedges[max_bin[1] + 1]) / 2.0
            near_idx = np.argmin((df['lat'] - start_lat)**2 + (df['lon'] - start_lon)**2)
            dir_lat = d_lat[near_idx]
            dir_lon = d_lon[near_idx]
        else:
            start_lat, start_lon = df['lat'].iloc[0], df['lon'].iloc[0]
            dir_lat, dir_lon = 1.0, 0.0

    norm = math.hypot(dir_lat, dir_lon)
    if norm > 0:
        dir_lat /= norm
        dir_lon /= norm
    else:
        dir_lat, dir_lon = 1.0, 0.0

    # コース幅ゲート（左右20m）
    gate_width = 0.00020
    norm_lat = -dir_lon * gate_width
    norm_lon =  dir_lat * gate_width
    gate_p1 = (start_lat - norm_lat, start_lon - norm_lon)
    gate_p2 = (start_lat + norm_lat, start_lon + norm_lon)

    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def intersect(A, B, C, D):
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    guard_pts = int(min_seconds / dt)
    laps = []
    lap_num = 1
    pts_since_lap = 0

    lats = df['lat'].values
    lons = df['lon'].values

    for i in range(len(df)):
        pts_since_lap += 1
        if i > 0 and pts_since_lap > guard_pts:
            p_prev = (lats[i-1], lons[i-1])
            p_curr = (lats[i], lons[i])

            if abs(p_curr[0] - start_lat) < 0.00050 and abs(p_curr[1] - start_lon) < 0.00050:
                if intersect(p_prev, p_curr, gate_p1, gate_p2):
                    move_lat = p_curr[0] - p_prev[0]
                    move_lon = p_curr[1] - p_prev[1]
                    dot = move_lat * dir_lat + move_lon * dir_lon
                    if dot > 0:
                        lap_num += 1
                        pts_since_lap = 0

        laps.append(lap_num)

    df['lap'] = laps
    df['auto_start_lat'] = start_lat
    df['auto_start_lon'] = start_lon
    return df

def align_laps_entire_track(df, pth_paths=None):
    if df is None or df.empty or 'lat' not in df.columns: return df

    fast_pts = df[df['speed_kmh'] > 15.0]
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

def rotate_coordinates(df, angle_deg, center_lat, center_lon, scale_x=1.0, scale_y=1.0):
    rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(rad), np.sin(rad)
    d_lat = (df['lat'] - center_lat) * scale_y
    d_lon = (df['lon'] - center_lon) * np.cos(np.radians(center_lat)) * scale_x
    rot_lon = d_lon * cos_a - d_lat * sin_a
    rot_lat = d_lon * sin_a + d_lat * cos_a
    new_lat = center_lat + rot_lat
    new_lon = center_lon + rot_lon / np.cos(np.radians(center_lat))
    return new_lat, new_lon

def format_lap_time(seconds):
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# -----------------------------------------------------------------------------
# 6. サイドバーUI ＆ スタイル定義
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

    h1, h2, h3, h4, h5, h6, label, p, .stMarkdown {{
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
        border-radius: 4px;
        padding: 2px 4px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

    div[data-baseweb="select"] > div {{
        background-color: {cur_theme['bg_card']} !important;
        border-color: {cur_theme['border']} !important;
        color: {cur_theme['text']} !important;
    }}
    div[data-baseweb="select"] span, div[data-baseweb="select"] input {{
        color: {cur_theme['text']} !important;
    }}

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-testid="stSelectboxVirtualDropdown"],
    div[data-testid="stSelectboxVirtualDropdown"] * {{
        background-color: {cur_theme['bg_card']} !important;
        color: {cur_theme['text']} !important;
        border-color: {cur_theme['border']} !important;
    }}

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] li[aria-selected="true"] * {{
        background-color: {cur_theme['bg_panel']} !important;
        color: {cur_theme['accent']} !important;
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

uploaded_files = st.sidebar.file_uploader(L['telemetry_file'], type=["bnx", "bnx4", "dtb", "csv", "nma"], accept_multiple_files=True)
uploaded_pth_file = st.sidebar.file_uploader(L['circuit_pth'], type=["pth"])
uploaded_bg_img = st.sidebar.file_uploader(L['circuit_bg'], type=["png", "jpg", "jpeg"])

pth_paths = []
if uploaded_pth_file is not None:
    pth_paths = parse_pth_course_text(uploaded_pth_file.getvalue().decode('utf-8', errors='ignore'))

map_style_options = [
    "自動生成 想定コース幅（路面帯）",
    "ESRI 衛星写真 (高画質)",
    "標準地図 (OSM)",
    "国土地理院写真",
    "独自画像背景",
    "背景なし (シンプル表示)"
]

default_map_idx = 1 if not pth_paths else 0
saved_map_style = saved_settings.get("map_style", None)
if saved_map_style in map_style_options:
    default_map_idx = map_style_options.index(saved_map_style)

map_style = st.sidebar.selectbox(f"{L['render_style']}:", map_style_options, index=default_map_idx)

auto_track_width = 9
auto_track_opacity = 0.25
bg_map_opacity = 0.85

if map_style == "自動生成 想定コース幅（路面帯）":
    auto_track_width = st.sidebar.slider(L['track_width'], 4, 30, int(saved_settings.get("auto_track_width", 9)), 1)
    auto_track_opacity = st.sidebar.slider(L['track_opacity'], 0.05, 0.80, float(saved_settings.get("auto_track_opacity", 0.25)), 0.05)

if map_style in ["ESRI 衛星写真 (高画質)", "標準地図 (OSM)", "国土地理院写真"]:
    bg_map_opacity = st.sidebar.slider(L['bg_map_opacity'], 0.10, 1.00, float(saved_settings.get("bg_map_opacity", 0.85)), 0.05)

# スケール・位置調整（常時表示）
st.sidebar.markdown("---")
st.sidebar.markdown(f"**📐 {L['scale_adjust']} ＆ 位置微調整**")

auto_offset_x_int = st.sidebar.number_input(L['track_shift_x'], min_value=-300, max_value=300, value=int(saved_settings.get("auto_offset_x_int", 0)), step=1)
auto_offset_y_int = st.sidebar.number_input(L['track_shift_y'], min_value=-300, max_value=300, value=int(saved_settings.get("auto_offset_y_int", 0)), step=1)

auto_offset_x = auto_offset_x_int * 0.00001
auto_offset_y = auto_offset_y_int * 0.00001

scale_x = st.sidebar.number_input(L['scale_x'], value=float(saved_settings.get("scale_x", 1.000)), min_value=0.200, max_value=5.000, step=0.010, format="%.3f")
scale_y = st.sidebar.number_input(L['scale_y'], value=float(saved_settings.get("scale_y", 1.000)), min_value=0.200, max_value=5.000, step=0.010, format="%.3f")

rotation_angle = st.sidebar.number_input(
    L['north_rotation'],
    min_value=-180.00, max_value=180.00,
    value=float(saved_settings.get("rotation_angle", 0.00)),
    step=0.01, format="%.2f"
)

# 有効ラップタイム範囲（ミニサーキット〜岡山国際・鈴鹿等）
default_min_lap_sec = float(saved_settings.get("min_lap_sec", 25.0))
default_max_lap_sec = float(saved_settings.get("max_lap_sec", 180.0))
lap_range = st.sidebar.slider(
    L['lap_time_range'],
    min_value=15.0, max_value=260.0,
    value=(default_min_lap_sec, default_max_lap_sec),
    step=5.0
)
valid_min_sec, valid_max_sec = lap_range
split_sec = max(12.0, valid_min_sec * 0.6)

map_height_px = st.sidebar.slider(L['map_height_label'], 400, 1200, 680, 20)
marker_font_size = st.sidebar.slider(L['marker_text_size'], 10, 30, 14, 1)

col_gps_btn1, col_gps_btn2 = st.sidebar.columns(2)
with col_gps_btn1:
    auto_align = st.button(L['auto_gps'])
with col_gps_btn2:
    reset_gps_btn = st.button(L['reset_gps'])

# -----------------------------------------------------------------------------
# 7. マルチファイルパース ＆ セッション管理
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
            single_df = parse_dtb_binary_cached(f_bytes, lap_idx=f_idx + 1, total_files=total_files)
            if not single_df.empty:
                single_df['lap'] = f_idx + 1
                single_df['file_lap'] = True
                dfs_list.append(single_df)
        st.session_state['cached_raw_df'] = pd.concat(dfs_list, ignore_index=True) if dfs_list else pd.DataFrame()
    else:
        u_f = uploaded_files[0]
        f_bytes = u_f.getvalue()
        st.session_state['cached_raw_df'] = auto_detect_and_parse(f_bytes, u_f.name)

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
            except Exception:
                pass
        df = pd.concat(selected_dfs, ignore_index=True) if selected_dfs else raw_df.copy()
    else:
        df = raw_df.copy()

    st.sidebar.markdown("---")
    use_visual_start = st.sidebar.checkbox(L['visual_start'], value=False)
    manual_start_tuple = None

    if use_visual_start and df is not None and not df.empty and len(df) > 50:
        sp_cut = max(20.0, df['speed_kmh'].max() * 0.45)
        fast_df = df[df['speed_kmh'] > sp_cut].reset_index(drop=True)
        if not fast_df.empty:
            max_sp_idx = fast_df['speed_kmh'].idxmax()
            hist, xedges, yedges = np.histogram2d(fast_df['lat'], fast_df['lon'], bins=40)
            max_bin = np.unravel_index(hist.argmax(), hist.shape)
            c_lat = (xedges[max_bin[0]] + xedges[max_bin[0] + 1]) / 2.0
            c_lon = (yedges[max_bin[1]] + yedges[max_bin[1] + 1]) / 2.0
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
        df = process_lap_telemetry(df, min_seconds=split_sec, manual_start=manual_start_tuple)
        if st.session_state.get('gps_aligned_flag', False):
            df = align_laps_entire_track(df, pth_paths=pth_paths)

# -----------------------------------------------------------------------------
# 8. メイン解析領域 (スタートライン位置完全同期)
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">CIRCUIT ANALYZE <span style="font-size:1.6rem; font-weight:200; opacity:0.6;">ver2.0</span></div>', unsafe_allow_html=True)
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
    all_lap_list = []
    total_laps_detected = int(df['lap'].max())
    dt = 0.05

    for lap_no, group in df.groupby('lap'):
        if len(group) < 10: continue
        lap_sec = len(group) * dt
        max_sp = ceil_2(group['speed_kmh'].max())
        avg_sp = ceil_2(group['speed_kmh'].mean())
        start_time_str = group['time_str'].iloc[0] if 'time_str' in group.columns else "00:00:00"

        item = {
            'Lap': int(lap_no),
            'StartTime': start_time_str,
            'LapTime': format_lap_time(lap_sec),
            'RawSec': lap_sec,
            'MaxSpeed': max_sp,
            'AvgSpeed': avg_sp,
            'Points': len(group)
        }
        all_lap_list.append(item)
        if valid_min_sec <= lap_sec <= valid_max_sec:
            lap_list.append(item)

    sum_df = pd.DataFrame(lap_list)
    if sum_df.empty and all_lap_list:
        sum_df = pd.DataFrame(all_lap_list)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🏁 **周回分割ステータス**: 全{total_laps_detected}周検知 ➔ 有効周回 {len(sum_df)} LAP")

    if not sum_df.empty:
        sum_df_sorted = sum_df.sort_values('RawSec').reset_index(drop=True)
        best_row = sum_df_sorted.iloc[0]
        best_lap_id = int(best_row['Lap'])
        available_laps = sum_df_sorted['Lap'].tolist()

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

        custom_names = {}
        loaded_custom_names = saved_settings.get("custom_names", {})
        for lap_id in selected_laps:
            custom_names[lap_id] = loaded_custom_names.get(lap_id, loaded_custom_names.get(str(lap_id), f"Lap {lap_id}"))

        if selected_laps:
            center_lat, center_lon = df['lat'].mean(), df['lon'].mean()
            # スケール X / Y および回転の同時適用
            df['rot_lat'], df['rot_lon'] = rotate_coordinates(df, rotation_angle, center_lat, center_lon, scale_x=scale_x, scale_y=scale_y)

            main_lap_id = selected_laps[0]
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

            step_stride = {"0.5x": 1, "1.0x": 2, "2.0x": 4, "4.0x": 8}[speed_factor]

            if not hide_hud_panel:
                col_map_half, col_trace_half = st.columns([4.5, 1.0])
            else:
                col_map_half = st.container()
                col_trace_half = None

            with col_map_half:
                def build_map_figure(is_zoomed=False, target_center=None, clicked_point=None):
                    fig = go.Figure()
                    base_count = 0

                    bg_layout_images = []
                    if map_style in ["ESRI 衛星写真 (高画質)", "標準地図 (OSM)", "国土地理院写真"]:
                        lat_pad = 0.0020
                        lon_pad = 0.0025
                        min_lat = df['lat'].min() - lat_pad
                        max_lat = df['lat'].max() + lat_pad
                        min_lon = df['lon'].min() - lon_pad
                        max_lon = df['lon'].max() + lon_pad

                        b64_src, img_x, img_y, img_w, img_h = get_processed_map_image(
                            min_lat, max_lat, min_lon, max_lon,
                            provider=map_style,
                            rotation_deg=rotation_angle,
                            center_lat=center_lat,
                            center_lon=center_lon
                        )

                        if b64_src:
                            bg_layout_images.append(dict(
                                source=b64_src,
                                xref="x",
                                yref="y",
                                x=(img_x - center_lon) * scale_x + center_lon + auto_offset_x,
                                y=(img_y - center_lat) * scale_y + center_lat + auto_offset_y,
                                sizex=img_w * scale_x,
                                sizey=img_h * scale_y,
                                xanchor="left",
                                yanchor="top",
                                sizing="stretch",
                                opacity=bg_map_opacity,
                                layer="below"
                            ))

                    pth_width = max(1.5, auto_track_width / 2.0)

                    if pth_paths:
                        for pth_df in pth_paths:
                            pth_df['rot_lat'], pth_df['rot_lon'] = rotate_coordinates(pth_df, rotation_angle, center_lat, center_lon, scale_x=scale_x, scale_y=scale_y)
                            fig.add_trace(go.Scatter(
                                x=pth_df['rot_lon'] + auto_offset_x,
                                y=pth_df['rot_lat'] + auto_offset_y,
                                mode='lines', name="PTH Circuit Boundary",
                                line=dict(width=pth_width, color=cur_theme['pth_line']),
                                hoverinfo='skip', showlegend=False
                            ))
                            base_count += 1

                    if map_style == "自動生成 想定コース幅（路面帯）":
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

                    for idx, lap_id in enumerate(selected_laps):
                        lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                        color = colors[idx % len(colors)]
                        label_name = custom_names.get(lap_id, f"Lap {lap_id}")

                        ind_off = st.session_state['individual_lap_offsets'].get(lap_id, (0.0, 0.0))

                        disp_lon = lap_data['rot_lon'] + auto_offset_x + ind_off[0]
                        disp_lat = lap_data['rot_lat'] + auto_offset_y + ind_off[1]

                        if line_color_mode == "車速グラデーション":
                            fig.add_trace(go.Scatter(
                                x=disp_lon, y=disp_lat,
                                mode='markers+lines', name=f"{label_name}",
                                line=dict(width=1.5, color=color),
                                marker=dict(size=4, color=lap_data['speed_kmh'], colorscale='Jet'),
                                customdata=np.stack((lap_data.index, lap_data['speed_kmh'], lap_data['lean_angle_deg']), axis=-1),
                                hovertemplate="%{data.name}<br>速: %{customdata[1]:.1f}km/h | 傾: %{customdata[2]:.1f}°<extra></extra>"
                            ))
                        elif line_color_mode == "ブレーキGグラデーション":
                            fig.add_trace(go.Scatter(
                                x=disp_lon, y=disp_lat,
                                mode='markers+lines', name=f"{label_name}",
                                line=dict(width=1.5, color=color),
                                marker=dict(size=4, color=np.abs(lap_data['accel_g']), colorscale='Reds'),
                                customdata=np.stack((lap_data.index, lap_data['speed_kmh'], lap_data['lean_angle_deg']), axis=-1),
                                hovertemplate="%{data.name}<br>速: %{customdata[1]:.1f}km/h | 減速G: %{customdata[2]:.2f}G<extra></extra>"
                            ))
                        else:
                            fig.add_trace(go.Scatter(
                                x=disp_lon, y=disp_lat,
                                mode='lines', name=f"{label_name}",
                                line=dict(width=3.5, color=color),
                                customdata=np.stack((lap_data.index, lap_data['speed_kmh'], lap_data['lean_angle_deg']), axis=-1),
                                hovertemplate="%{data.name}<br>速: %{customdata[1]:.1f}km/h | 傾: %{customdata[2]:.1f}°<extra></extra>"
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

                    # -------------------------------------------------------------
                    # スタートラインマーカーの座標を走行ラインと完全同期
                    # -------------------------------------------------------------
                    start_pt_lat = manual_start_tuple[0] if manual_start_tuple else df.get('auto_start_lat', pd.Series([center_lat])).iloc[0]
                    start_pt_lon = manual_start_tuple[1] if manual_start_tuple else df.get('auto_start_lon', pd.Series([center_lon])).iloc[0]

                    m_rot_lat, m_rot_lon = rotate_coordinates(
                        pd.DataFrame([{'lat': start_pt_lat, 'lon': start_pt_lon}]),
                        rotation_angle, center_lat, center_lon, scale_x=scale_x, scale_y=scale_y
                    )
                    fig.add_trace(go.Scatter(
                        x=m_rot_lon + auto_offset_x, y=m_rot_lat + auto_offset_y,
                        mode='markers+text',
                        marker=dict(size=20, color='#ffcc00', symbol='hexagram', line=dict(width=3, color='#000000')),
                        text=[" START LINE"], textposition="top center",
                        textfont=dict(size=15, color='#ffcc00'),
                        name="Start Marker", showlegend=False
                    ))
                    base_count += 1

                    initial_animated_indices = []
                    for idx, lap_id in enumerate(selected_laps):
                        ldf = df[df['lap'] == lap_id].reset_index(drop=True)
                        color = colors[idx % len(colors)]
                        label_name = custom_names.get(lap_id, f"Lap {lap_id}")
                        curr_pt = ldf.iloc[0]
                        ind_off = st.session_state['individual_lap_offsets'].get(lap_id, (0.0, 0.0))

                        pos_str = TEXT_POSITIONS[idx % len(TEXT_POSITIONS)]
                        fig.add_trace(go.Scatter(
                            x=[curr_pt['rot_lon'] + auto_offset_x + ind_off[0]], y=[curr_pt['rot_lat'] + auto_offset_y + ind_off[1]],
                            mode='markers+text',
                            marker=dict(size=14, color=color, line=dict(width=2, color='#ffffff')),
                            text=[f" {label_name}: {ceil_2(curr_pt['speed_kmh']):.2f} km/h"],
                            textfont=dict(size=marker_font_size, color=color),
                            textposition=pos_str, showlegend=False
                        ))
                        initial_animated_indices.append(base_count + idx)

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
                            ind_off = st.session_state['individual_lap_offsets'].get(lap_id, (0.0, 0.0))

                            pos_str = TEXT_POSITIONS[idx % len(TEXT_POSITIONS)]
                            frame_data.append(go.Scatter(
                                x=[curr_pt['rot_lon'] + auto_offset_x + ind_off[0]], y=[curr_pt['rot_lat'] + auto_offset_y + ind_off[1]],
                                mode='markers+text',
                                marker=dict(size=14, color=color, line=dict(width=2, color='#ffffff')),
                                text=[f" {label_name}: {ceil_2(curr_pt['speed_kmh']):.2f} km/h"],
                                textfont=dict(size=marker_font_size, color=color),
                                textposition=pos_str
                            ))
                        frames.append(go.Frame(data=frame_data, name=str(f_idx), traces=initial_animated_indices))

                    fig.frames = frames

                    if clicked_point is not None:
                        fig.add_trace(go.Scatter(
                            x=[clicked_point['rot_lon'] + auto_offset_x], y=[clicked_point['rot_lat'] + auto_offset_y],
                            mode='markers',
                            marker=dict(size=18, color='#ffff00', symbol='star', line=dict(width=2, color='#000000')),
                            name="Selected Point", showlegend=False
                        ))

                    plot_bg = "rgba(0,0,0,0)" if map_style in ["ESRI 衛星写真 (高画質)", "標準地図 (OSM)", "国土地理院写真"] else cur_theme['plot_bg']

                    # 走行ラインの実際の範囲にのみ余白をつけて自動フォーカス
                    disp_all_lons = df['rot_lon'] + auto_offset_x
                    disp_all_lats = df['rot_lat'] + auto_offset_y
                    pad_x = (disp_all_lons.max() - disp_all_lons.min()) * 0.08
                    pad_y = (disp_all_lats.max() - disp_all_lats.min()) * 0.08

                    layout_kwargs = dict(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=plot_bg,
                        font=dict(color=cur_theme['text']), height=map_height_px if not is_zoomed else 320,
                        xaxis=dict(showgrid=True, gridcolor=cur_theme['grid'], scaleanchor="y", scaleratio=1,
                                   range=[disp_all_lons.min() - pad_x, disp_all_lons.max() + pad_x]),
                        yaxis=dict(showgrid=True, gridcolor=cur_theme['grid'],
                                   range=[disp_all_lats.min() - pad_y, disp_all_lats.max() + pad_y]),
                        margin=dict(l=5, r=5, t=35, b=5),
                        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0.0),
                        images=bg_layout_images,
                        updatemenus=[dict(
                            type="buttons", showactive=False, x=0.01, y=0.99,
                            buttons=[
                                dict(label="PLAY", method="animate", args=[None, {"frame": {"duration": 50, "redraw": False}, "fromcurrent": True}]),
                                dict(label="PAUSE", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
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
                st.plotly_chart(fig_map, use_container_width=True)

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
                            <div class="metric-card-slim" style="border-left: 3px solid {color}; margin-bottom: 3px;">
                                <div class="metric-title-slim" style="color:{color};">{label_name}</div>
                                <div class="metric-value-slim" style="color:{color};">[{row['LapTime']}]</div>
                                <div class="metric-unit-slim">{ceil_2(sync_pt['speed_kmh']):.1f}k ({lean_deg:.0f}°)</div>
                            </div>
                            """, unsafe_allow_html=True)

                            if st.button("キープ", key=f"keep_lap_{lap_id}"):
                                keep_name = f"Lap {lap_id} [{row['LapTime']}] ({row['StartTime']})"
                                st.session_state['saved_kept_laps'][keep_name] = lap_data
                                st.success("保存完了")

            # -----------------------------------------------------------------
            # 9. 車速・デルタトレース ＆ G-G Diagram ＆ 詳細分析レポート
            # -----------------------------------------------------------------
            st.markdown(f"### {L['speed_traces']}")
            fig_speed = go.Figure()

            for idx, lap_id in enumerate(selected_laps):
                lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                row = sum_df.loc[sum_df['Lap']==lap_id].iloc[0]
                color = colors[idx % len(colors)]
                label_name = custom_names.get(lap_id, f"Lap {lap_id}")

                if x_axis_type in ["Distance (m)", "走行距離 (m)"]:
                    x_vals = np.cumsum(lap_data['speed_kmh'] / 3.6 * dt)
                    x_title = L['dist_m']
                else:
                    x_vals = np.arange(len(lap_data)) * dt
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

            col_delta_half, col_gg_half = st.columns([1.0, 1.0])

            with col_delta_half:
                st.markdown(f"### {L['delta_traces']}")
                fig_delta = go.Figure()

                best_lap_df = df[df['lap'] == best_lap_id].reset_index(drop=True)
                best_cum_time = np.arange(len(best_lap_df)) * dt
                best_cum_dist = np.cumsum(best_lap_df['speed_kmh'] / 3.6 * dt)

                for idx, lap_id in enumerate(selected_laps):
                    lap_data = df[df['lap'] == lap_id].reset_index(drop=True)
                    color = colors[idx % len(colors)]
                    label_name = custom_names.get(lap_id, f"Lap {lap_id}")

                    lap_cum_dist = np.cumsum(lap_data['speed_kmh'] / 3.6 * dt)
                    lap_cum_time = np.arange(len(lap_data)) * dt

                    interp_best_time = np.interp(lap_cum_dist, best_cum_dist, best_cum_time)
                    delta_sec = lap_cum_time - interp_best_time

                    fig_delta.add_trace(go.Scatter(
                        x=lap_cum_dist, y=delta_sec,
                        mode='lines', name=f"{label_name} Delta",
                        line=dict(width=2.0, color=color),
                        hovertemplate="距離: %{x:.1f}m | タイム差: %{y:+.3f}秒<extra></extra>"
                    ))

                fig_delta.add_shape(type="line", x0=0, y0=0, x1=max(best_cum_dist), y1=0, line=dict(color=cur_theme['text'], width=1, dash="dash"))
                fig_delta.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
                    font=dict(color=cur_theme['text']), height=280,
                    xaxis=dict(title=L['dist_m'], showgrid=True, gridcolor=cur_theme['grid']),
                    yaxis=dict(title="Delta (sec)", showgrid=True, gridcolor=cur_theme['grid']),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_delta, use_container_width=True)

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
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_gg, use_container_width=True)

            st.markdown(f"### {L['sector_analysis']}")
            sec_rows = []
            for lap_id in selected_laps:
                ldf = df[df['lap'] == lap_id].reset_index(drop=True)
                n_pts = len(ldf)
                s1_df = ldf.iloc[:n_pts//3]
                s2_df = ldf.iloc[n_pts//3 : 2*n_pts//3]
                s3_df = ldf.iloc[2*n_pts//3:]

                s1_t = len(s1_df) * dt
                s2_t = len(s2_df) * dt
                s3_t = len(s3_df) * dt

                brake_pct = (len(ldf[ldf['pedal_status'] == 'Braking']) / n_pts) * 100.0
                accel_pct = (len(ldf[ldf['pedal_status'] == 'Accel']) / n_pts) * 100.0

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
                "map_style": map_style,
                "auto_offset_x_int": auto_offset_x_int,
                "auto_offset_y_int": auto_offset_y_int,
                "scale_x": scale_x,
                "scale_y": scale_y,
                "auto_track_width": auto_track_width,
                "auto_track_opacity": auto_track_opacity,
                "bg_map_opacity": bg_map_opacity,
                "min_lap_sec": valid_min_sec,
                "max_lap_sec": valid_max_sec,
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
        pth_df['rot_lat'], pth_df['rot_lon'] = rotate_coordinates(pth_df, rotation_angle, c_lat, c_lon, scale_x=scale_x, scale_y=scale_y)
        fig_pth_only.add_trace(go.Scatter(
            x=pth_df['rot_lon'] + auto_offset_x,
            y=pth_df['rot_lat'] + auto_offset_y,
            mode='lines', name="PTH Circuit Boundary",
            line=dict(width=pth_width, color=cur_theme['pth_line']),
            hoverinfo='skip', showlegend=False
        ))
    fig_pth_only.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=cur_theme['plot_bg'],
        font=dict(color=cur_theme['text']), height=map_height_px,
        xaxis=dict(showgrid=False, visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, visible=False),
        margin=dict(l=5, r=5, t=5, b=5)
    )
    st.plotly_chart(fig_pth_only, use_container_width=True)

else:
    st.info(L['drop_info'])