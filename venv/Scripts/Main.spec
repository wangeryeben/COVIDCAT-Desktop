# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Main.py'],
             pathex=['resources_rc.py', 'MainUI.py', 'C:\\Users\\qq199694\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages', 'ico.ico', 'C:\\Users\\qq199694\\Dropbox\\ED Project\\Qian Cheng\\COVID19\\Interface 2\\venv\\Scripts'],
             binaries=[],
             datas=[],
             hiddenimports=['ico', 'MainUI', 'resources_rc'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='ico.ico')
