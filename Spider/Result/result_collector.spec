# -*- mode: python -*-

block_cipher = None


a = Analysis(['result_collector.py'],
             pathex=['C:\\Python27\\Lib\\site-packages\\zmq', 'D:\\gitRepository\\BMSystem\\Spider\\Result'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='result_collector',
          debug=False,
          strip=False,
          upx=True,
          console=True )
