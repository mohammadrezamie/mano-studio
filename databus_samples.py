"""Original ready-to-run examples for the combined RAM/register bus lab."""
SAMPLES = [
  {
    "format": "mano-databus",
    "version": 1,
    "id": "ram-roundtrip",
    "title": [
      "RAM write and read",
      "نوشتن و خواندن RAM"
    ],
    "task": [
      "Write A at address 3, then load R1 from RAM.",
      "مقدار A را در آدرس ۳ بنویسید و سپس R1 را از RAM بارگذاری کنید."
    ],
    "steps": [
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "AR"
        ],
        "external": 3
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "RAM"
        ],
        "external": 10
      },
      {
        "sources": [
          "RAM"
        ],
        "destinations": [
          "R1"
        ],
        "external": 0
      }
    ],
    "expected": {
      "registers": [
        3,
        0,
        10
      ],
      "memory": [
        [
          3,
          10
        ]
      ]
    }
  },
  {
    "format": "mano-databus",
    "version": 1,
    "id": "parallel-load",
    "title": [
      "Parallel register transfer",
      "انتقال موازی ثبات‌ها"
    ],
    "task": [
      "Copy R0 to both AR and R1; write RAM at the old AR.",
      "R0 را هم‌زمان در AR و R1 بارگذاری و حافظه را در آدرس قبلی AR بنویسید."
    ],
    "steps": [
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "AR"
        ],
        "external": 9
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R0"
        ],
        "external": 6
      },
      {
        "sources": [
          "R0"
        ],
        "destinations": [
          "AR",
          "R1",
          "RAM"
        ],
        "external": 0
      }
    ],
    "expected": {
      "registers": [
        6,
        6,
        6
      ],
      "memory": [
        [
          9,
          6
        ]
      ]
    }
  },
  {
    "format": "mano-databus",
    "version": 1,
    "id": "bus-contention",
    "title": [
      "Conflicting bus drivers",
      "تداخل راه‌اندازهای گذرگاه"
    ],
    "task": [
      "Drive 0101 and 0110 together; observe 01XX without loading destinations.",
      "دو مقدار 0101 و 0110 را هم‌زمان روی گذرگاه قرار دهید؛ 01XX را بدون بارگذاری مشاهده کنید."
    ],
    "steps": [
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R0"
        ],
        "external": 5
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R1"
        ],
        "external": 6
      },
      {
        "sources": [
          "R0",
          "R1"
        ],
        "destinations": [],
        "external": 0
      }
    ],
    "expected": {
      "registers": [
        0,
        5,
        6
      ],
      "memory": [],
      "bus": "01XX"
    }
  },
  {
    "format": "mano-databus",
    "version": 1,
    "id": "alu-overflow",
    "title": [
      "ALU signed overflow and store",
      "سرریز علامت‌دار و ذخیره ALU"
    ],
    "task": [
      "Load R0=7, R1=1, AR=9. Add, store result 8 in RAM[9] and R0; observe C=0, V=1, N=1, Z=0.",
      "R0=7، R1=1 و AR=9 را بارگذاری کنید. جمع را در RAM[9] و R0 ذخیره و پرچم‌های C=0، V=1، N=1، Z=0 را مشاهده کنید."
    ],
    "steps": [
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "AR"
        ],
        "external": 9
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R0"
        ],
        "external": 7
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R1"
        ],
        "external": 1
      },
      {
        "sources": [
          "ALU"
        ],
        "destinations": [
          "R0",
          "RAM"
        ],
        "external": 0
      }
    ],
    "expected": {
      "registers": [
        9,
        8,
        1
      ],
      "memory": [
        [
          9,
          8
        ]
      ],
      "bus": "1000",
      "flags": [
        0,
        True,
        True,
        False
      ]
    }
  },
  {
    "format": "mano-databus",
    "version": 1,
    "id": "alu-borrow",
    "title": [
      "ALU subtraction and borrow",
      "تفریق ALU و قرض"
    ],
    "task": [
      "Subtract 5 from 2, write D into RAM[3] and R0; observe C=0 (borrow), V=0, N=1, Z=0.",
      "۵ را از ۲ کم کنید، D را در RAM[3] و R0 بنویسید؛ پرچم‌های C=0 (قرض)، V=0، N=1، Z=0 را مشاهده کنید."
    ],
    "steps": [
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "AR"
        ],
        "external": 3
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R0"
        ],
        "external": 2
      },
      {
        "sources": [
          "EXT"
        ],
        "destinations": [
          "R1"
        ],
        "external": 5
      },
      {
        "sources": [
          "ALU"
        ],
        "destinations": [
          "R0",
          "RAM"
        ],
        "external": 0,
        "operation": "SUB",
        "carry": 0
      }
    ],
    "expected": {
      "registers": [
        3,
        13,
        5
      ],
      "memory": [
        [
          3,
          13
        ]
      ],
      "bus": "1101",
      "flags": [
        0,
        False,
        True,
        False
      ]
    }
  }
]


def sample(key):
    return next(s for s in SAMPLES if s["id"] == key)


def run_sample(model, scenario):
    """Replay a complete example from its reproducible reset state."""
    model.reset()
    for step in scenario["steps"]:
        model.tick(step["sources"], step["destinations"], step["external"], step.get("operation", "ADD"), step.get("carry", 0))
    return model
