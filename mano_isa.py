"""Named instructions of Mano's Basic Computer, chapter 5 table 5-2."""
MEMORY = dict(zip("AND ADD LDA STA BUN BSA ISZ".split(), range(7)))
FIXED = dict(zip(
    "CLA CLE CMA CME CIR CIL INC SPA SNA SZA SZE HLT INP OUT SKI SKO ION IOF".split(),
    (0x7800, 0x7400, 0x7200, 0x7100, 0x7080, 0x7040, 0x7020, 0x7010,
     0x7008, 0x7004, 0x7002, 0x7001, 0xF800, 0xF400, 0xF200, 0xF100, 0xF080, 0xF040)))
MEMORY_BY_CODE = {value: name for name, value in MEMORY.items()}
FIXED_BY_CODE = {value: name for name, value in FIXED.items()}
