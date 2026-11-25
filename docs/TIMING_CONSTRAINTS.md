# Setup and hold time — Chapter 1

Logic Lab → Sequential → Setup / hold adds an independent, bilingual exercise. Adjust the D rising/falling transitions, clock edge and setup/hold requirements in integer ticks. The waveform highlights the required stable windows; it reports early/late violations and coincident changes. The default pulse changes at ticks 7 and 12, with edge 10, setup 3 and hold 2: both boundary changes are permitted, sampled D=1. The violation example changes D at 8 and 11, so both constraints fail and the next Q is not predicted.

در بخش مدارهای ترتیبی، زمان تغییر D، لبه ساعت و بازه‌های آماده‌سازی و نگهداری را تغییر دهید. مثال پیش‌فرض در مرزهای مجاز قرار دارد؛ مثال نقض زمان‌بندی تغییرهای ۸ و ۱۱ را با لبه ۱۰ بررسی می‌کند. در صورت نقض، برنامه مقدار Q را حدس نمی‌زند.

The pure checker accepts a complete event list, assumes data stable before zero and after the final supplied event, ignores repeated writes of the same bit, treats a genuine transition exactly at the edge as ambiguous even when both constraints are zero, and permits transitions exactly at the outer setup/hold boundaries. Its UI is restricted to one pulse, 0–30 ticks. This is not a physical clock-to-Q, metastability, propagation-delay or analog electrical simulator. No mutation of the live ClockedCircuit, no new learning route or dependency.

Local execution: 11 pytest cases passed in 0.09 s, including 12,288 combinations of six-tick complete waveforms and timing windows, boundary and coincident cases, and invalid input. Git hashes match the tested files: timing_constraints.py a1114060414e9f21e0082a13079504ca6cc97020 and tests/test_timing_constraints.py cdf10063cf600122efae837c26da33b7d45430a3. Two Qt locale cases authored, not executed locally. Native visual acceptance and actual capture remain open. C01.08 stays partial; latches, asynchronous controls and physical timing remain future work.

Run: python -m pytest -q tests/test_timing_constraints.py
