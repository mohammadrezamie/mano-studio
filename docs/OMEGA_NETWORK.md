# Omega interconnection network

Chapter 13 development model. `omega_network.py` implements a blocking network of N/2 two-input/two-output switches per stage, for N = 2, 4, 8, 16, 32, or 64. There are log2(N) stages. Each switch chooses its output port using the next destination bit (MSB first). Between stages, perfect shuffle rotates the binary line index left by one bit. Each source/destination pair has one route.

A transfer round validates every request, then grants complete routes in ascending source order. If a stage output is already reserved by a granted source, the later request reports its blocking stage and owner; it does not reserve a partial path. Distinct destinations can still conflict internally. A 2x2 switch can carry two simultaneous transfers if they use distinct output ports.

## Verification

Local Python regression: 19 passed. All 5,460 individual routes across the six sizes, all 24 four-port destination permutations, 400 seeded rounds, straight/cross switching and input validation. Exact repository blob hashes matched the locally tested files: model 215faff66657985793327d0092d9c8b974e14beb; tests b60247f4383ab19d9b4b22ecf6fc578c04d7c5f8.

`python -m pytest -q tests/test_omega_network.py`

This is a circuit-path reservation teaching model, not a packet network, buffer simulator, electrical timing model or fairness guarantee. The fixed priority may starve repeated lower-priority requests. Interactive bilingual UI, catalog route, screenshot checks and full CI remain pending. The 43 existing learning routes are unchanged. No effect on the frozen beta or standalone translator.
