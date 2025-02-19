
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [
    ("venv/lib/site-packages/streamlit/runtime", "streamlit/runtime"), 
    ("venv/lib/site-packages/streamlit_option_menu/frontend/dist", "streamlit_option_menu/frontend/dist"), 
    ("venv/lib/site-packages/streamlit_autorefresh", "streamlit_autorefresh"),
    ("venv/lib/site-packages/sklearn", "sklearn"),  
    ("venv/lib/site-packages/scapy", "scapy"),  
    ("data/database.db", "data"), 
]

 
datas += collect_data_files("streamlit_option_menu") 
datas += collect_data_files("streamlit")  
datas += collect_data_files("streamlit_autorefresh") 
datas += collect_data_files("scapy")
datas += collect_data_files("numpy")  
datas += collect_data_files("pandas")
datas += collect_data_files("plotly")
datas += collect_data_files("matplotlib")
datas += collect_data_files("sklearn")  


datas += copy_metadata("streamlit")  
datas += copy_metadata("streamlit_option_menu")  
datas += copy_metadata("streamlit_autorefresh")  


block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=["streamlit_option_menu", "streamlit_autorefresh", "sklearn", "scapy", "requests", "urllib3", "numpy", "pandas"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="app/assets/shield.ico",
)

coll = COLLECT(
    exe,
    a.files,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='run',
)
