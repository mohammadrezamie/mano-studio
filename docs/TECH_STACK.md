# Technology decisions
## Current
Python and standalone standard-library RTL translator; independent scientific engines; PySide6 >=6.8,<7 (existing dependency); Qt 6 Widgets, QPainter, Qt SVG, Qt Model/View, QSettings, native Qt animation framework, pytest and Windows/Ubuntu GitHub Actions. All scientific operations offline. Windows 10/11 x64 is the intended distribution target, not a newly tested installer.

## Modernization strategy
Qt's current UI documentation distinguishes Qt Quick's GPU scene graph and rich effects from Widgets' mature desktop controls and text editing. Qt Quick can be embedded in a widget application, but an extra shell/renderer would add maintenance and packaging risks. Preserve working editors/engines and use modern native Qt primitives now. Evaluate Qt Quick/QML only for a concrete visual bottleneck with measured improvement, reduced-motion parity, offline assets, Windows high-DPI and graphics fallback tests. Do not introduce Electron, webview, remote assets, or duplicate runtime merely for novelty. No dependency upgrade without regression evidence.

Official sources: https://doc.qt.io/qt-6/topics-ui.html ; https://doc.qt.io/qt-6/qtquick-visualcanvas-scenegraph.html ; https://doc.qt.io/qtforpython-6/overviews/qtcore-animation-overview.html .
