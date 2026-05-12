# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TikTok Bot Windows .exe build.
Run: pyinstaller tiktok_bot.spec
"""

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('us_proxies.txt', '.'),
    ],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'undetected_chromedriver',
        'requests',
        'dotenv',
        'fake_useragent',
        'schedule',
        'colorama',
        'socks',
        'aiohttp',
        'aiohttp_socks',
        'bot',
        'bot.viewer',
        'bot.engager',
        'bot.follower',
        'bot.stats',
        'browser',
        'browser.driver',
        'utils',
        'utils.logger',
        'utils.helpers',
        'config',
        'proxy_scraper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TikTokBot',
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
    icon=None,
)
