# Motion policy
Use motion only to communicate interaction or model events. Implemented shared MotionTabs uses Qt QVariantAnimation, OutCubic easing and 160 ms underline transition; no content opacity, geometry shifts, or background loops. Rapid selection retargets the current indicator; hide/resize/reduced motion snaps. The existing reduced_motion setting is propagated to the application and cancels in-flight indicators. CPU/datapath motion remains driven by simulation events and its existing preferences.

Future motion budgets: 100–180 ms for control feedback, 160–240 ms for meaningful navigation, no artificial wait. Never animate schematic correctness or substitute decoration for actual simulation state. Respect reduced motion; verify native Windows performance and keyboard focus before acceptance.

Official references: https://doc.qt.io/qtforpython-6/overviews/qtcore-animation-overview.html and https://doc.qt.io/qtforpython-6/PySide6/QtCore/QEasingCurve.html .
