# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\git_repertory\\pythonDemo\\qt_demo\\barcode'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          name='绿米工厂打印',
          debug=False,
          bootloader_ignore_signals=False,
          version='D:\\git_repertory\\pythonDemo\\qt_demo\\barcode\\file_version_info.txt',
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='D:\\git_repertory\\pythonDemo\\qt_demo\\barcode\\image\\20190926084906988_easyicon_net_512.ico' )
