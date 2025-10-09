[app]

# application metadata
title = ViloXTerm
project_dir = .
input_file = viloxterm_main.py
exec_directory = .
icon =

[python]

# python environment
python_path = /home/jasonvi/GitHub/vfwidgets/.direnv/python-3.12.3/bin/python3
packages = PySide6==6.9.0,vfwidgets-theme-system,chrome-tabbed-window,vfwidgets-multisplit,vfwidgets-terminal,vfwidgets-keybinding

# exclude development dependencies
excluded_qml_plugins = QtCharts,QtDataVisualization,QtWebView,QtTest,Qt3D

[qt]

# qt modules required by viloxterm
modules = Widgets,DBus,Gui,Core

# qml is not used
qml_files = 
excluded_qml_plugins = QtQuick,QtQuick.Controls,QtQuick.Layouts
plugins = accessiblebridge,egldeviceintegrations,generic,iconengines,imageformats,platforminputcontexts,platforms,platforms/darwin,platformthemes,styles,xcbglintegrations

[nuitka]

# nuitka compilation options
mode = onefile

# enable optimizations
lto = no

# disable console window on windows
macos_create_app_bundle = true

# performance options
jobs = 4

# additional nuitka options for qwebengineview support
# include package data (resources defined in pyproject.toml)
extra_args = --nofollow-import-to=pytest --nofollow-import-to=black --nofollow-import-to=ruff --nofollow-import-to=mypy --include-package-data=vfwidgets_terminal --include-package-data=vfwidgets_theme

