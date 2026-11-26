"""Original offline classic circuit samples; saved JSON copies mirror these data."""
import json
from circuit_document import CircuitDocument

SAMPLES = [
  {
    "id": "full-adder-halves",
    "title": [
      "Full adder from two half adders",
      "تمام‌جمع‌کننده با دو نیم‌جمع‌کننده"
    ],
    "task": [
      "Check S + 2×Cout = A+B+Cin.",
      "بررسی کنید S + 2×Cout = A+B+Cin."
    ],
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A",
        "B",
        "Cin"
      ],
      "gates": [
        {
          "output": "p",
          "op": "XOR",
          "inputs": [
            "A",
            "B"
          ]
        },
        {
          "output": "c1",
          "op": "AND",
          "inputs": [
            "A",
            "B"
          ]
        },
        {
          "output": "s",
          "op": "XOR",
          "inputs": [
            "p",
            "Cin"
          ]
        },
        {
          "output": "c2",
          "op": "AND",
          "inputs": [
            "p",
            "Cin"
          ]
        },
        {
          "output": "c",
          "op": "OR",
          "inputs": [
            "c1",
            "c2"
          ]
        }
      ],
      "outputs": [
        [
          "S",
          "s"
        ],
        [
          "Cout",
          "c"
        ]
      ],
      "positions": []
    },
    "section": "C01.05"
  },
  {
    "id": "nand-xor",
    "title": [
      "XOR from four NAND gates",
      "XOR با چهار گیت NAND"
    ],
    "task": [
      "Check XOR for all four input pairs.",
      "XOR را برای چهار ترکیب ورودی بررسی کنید."
    ],
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A",
        "B"
      ],
      "gates": [
        {
          "output": "n1",
          "op": "NAND",
          "inputs": [
            "A",
            "B"
          ]
        },
        {
          "output": "n2",
          "op": "NAND",
          "inputs": [
            "A",
            "n1"
          ]
        },
        {
          "output": "n3",
          "op": "NAND",
          "inputs": [
            "B",
            "n1"
          ]
        },
        {
          "output": "y",
          "op": "NAND",
          "inputs": [
            "n2",
            "n3"
          ]
        }
      ],
      "outputs": [
        [
          "Y",
          "y"
        ]
      ],
      "positions": []
    },
    "section": "C01.04"
  },
  {
    "id": "mux-majority",
    "title": [
      "Three-input majority using a MUX",
      "تابع اکثریت سه‌ورودی با مالتی‌پلکسر"
    ],
    "task": [
      "Y=1 exactly when at least two inputs are 1.",
      "Y فقط وقتی یک است که دست‌کم دو ورودی یک باشند."
    ],
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A",
        "B",
        "C"
      ],
      "gates": [
        {
          "output": "low",
          "op": "AND",
          "inputs": [
            "B",
            "C"
          ]
        },
        {
          "output": "high",
          "op": "OR",
          "inputs": [
            "B",
            "C"
          ]
        },
        {
          "output": "na",
          "op": "NOT",
          "inputs": [
            "A"
          ]
        },
        {
          "output": "p0",
          "op": "AND",
          "inputs": [
            "na",
            "low"
          ]
        },
        {
          "output": "p1",
          "op": "AND",
          "inputs": [
            "A",
            "high"
          ]
        },
        {
          "output": "y",
          "op": "OR",
          "inputs": [
            "p0",
            "p1"
          ]
        }
      ],
      "outputs": [
        [
          "Y",
          "y"
        ]
      ],
      "positions": []
    },
    "section": "C02.03"
  },
  {
    "id": "decoder-enabled-low",
    "title": [
      "Enabled active-low 2-to-4 decoder",
      "دیکودر ۲ به ۴ فعال با صفر"
    ],
    "task": [
      "EN=1 selects exactly one low output; EN=0 leaves all high.",
      "با EN=1 فقط خروجی انتخاب‌شده صفر است؛ با EN=0 همه یک هستند."
    ],
    "section": "C02.02",
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A1",
        "A0",
        "EN"
      ],
      "gates": [
        {
          "output": "n1",
          "op": "NOT",
          "inputs": [
            "A1"
          ]
        },
        {
          "output": "n0",
          "op": "NOT",
          "inputs": [
            "A0"
          ]
        },
        {
          "output": "d0",
          "op": "NAND",
          "inputs": [
            "n1",
            "n0",
            "EN"
          ]
        },
        {
          "output": "d1",
          "op": "NAND",
          "inputs": [
            "n1",
            "A0",
            "EN"
          ]
        },
        {
          "output": "d2",
          "op": "NAND",
          "inputs": [
            "A1",
            "n0",
            "EN"
          ]
        },
        {
          "output": "d3",
          "op": "NAND",
          "inputs": [
            "A1",
            "A0",
            "EN"
          ]
        }
      ],
      "outputs": [
        [
          "Y0",
          "d0"
        ],
        [
          "Y1",
          "d1"
        ],
        [
          "Y2",
          "d2"
        ],
        [
          "Y3",
          "d3"
        ]
      ],
      "positions": []
    }
  },
  {
    "id": "comparator-two-bit",
    "title": [
      "Two-bit cascaded magnitude comparator",
      "مقایسه‌گر آبشاری دو بیتی"
    ],
    "task": [
      "Compare unsigned A and B: exactly one of LT, EQ, GT is high.",
      "A و B بدون علامت را مقایسه کنید؛ فقط یکی از LT، EQ و GT یک است."
    ],
    "section": "C02.05",
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A1",
        "A0",
        "B1",
        "B0"
      ],
      "gates": [
        {
          "output": "e1",
          "op": "XNOR",
          "inputs": [
            "A1",
            "B1"
          ]
        },
        {
          "output": "e0",
          "op": "XNOR",
          "inputs": [
            "A0",
            "B0"
          ]
        },
        {
          "output": "na1",
          "op": "NOT",
          "inputs": [
            "A1"
          ]
        },
        {
          "output": "na0",
          "op": "NOT",
          "inputs": [
            "A0"
          ]
        },
        {
          "output": "nb1",
          "op": "NOT",
          "inputs": [
            "B1"
          ]
        },
        {
          "output": "nb0",
          "op": "NOT",
          "inputs": [
            "B0"
          ]
        },
        {
          "output": "lt1",
          "op": "AND",
          "inputs": [
            "na1",
            "B1"
          ]
        },
        {
          "output": "lt0",
          "op": "AND",
          "inputs": [
            "na0",
            "B0"
          ]
        },
        {
          "output": "gt1",
          "op": "AND",
          "inputs": [
            "A1",
            "nb1"
          ]
        },
        {
          "output": "gt0",
          "op": "AND",
          "inputs": [
            "A0",
            "nb0"
          ]
        },
        {
          "output": "lp",
          "op": "AND",
          "inputs": [
            "e1",
            "lt0"
          ]
        },
        {
          "output": "gp",
          "op": "AND",
          "inputs": [
            "e1",
            "gt0"
          ]
        },
        {
          "output": "l",
          "op": "OR",
          "inputs": [
            "lt1",
            "lp"
          ]
        },
        {
          "output": "e",
          "op": "AND",
          "inputs": [
            "e1",
            "e0"
          ]
        },
        {
          "output": "g",
          "op": "OR",
          "inputs": [
            "gt1",
            "gp"
          ]
        }
      ],
      "outputs": [
        [
          "LT",
          "l"
        ],
        [
          "EQ",
          "e"
        ],
        [
          "GT",
          "g"
        ]
      ],
      "positions": []
    }
  },
  {
    "id": "adder-subtractor-two-bit",
    "title": [
      "Two-bit selectable adder/subtractor",
      "جمع‌کننده و تفریق‌کننده دو بیتی"
    ],
    "task": [
      "M=0 adds; M=1 computes A−B modulo four. Cout=1 means no borrow in subtract mode.",
      "با M=0 جمع و با M=1 تفریق پیمانه چهار انجام می‌شود. Cout=1 در تفریق یعنی بدون قرض."
    ],
    "section": "C02.04",
    "document": {
      "format": "mano-logic",
      "version": 2,
      "inputs": [
        "A1",
        "A0",
        "B1",
        "B0",
        "M"
      ],
      "gates": [
        {
          "output": "x0",
          "op": "XOR",
          "inputs": [
            "B0",
            "M"
          ]
        },
        {
          "output": "x1",
          "op": "XOR",
          "inputs": [
            "B1",
            "M"
          ]
        },
        {
          "output": "p0",
          "op": "XOR",
          "inputs": [
            "A0",
            "x0"
          ]
        },
        {
          "output": "g0",
          "op": "AND",
          "inputs": [
            "A0",
            "x0"
          ]
        },
        {
          "output": "s0",
          "op": "XOR",
          "inputs": [
            "p0",
            "M"
          ]
        },
        {
          "output": "h0",
          "op": "AND",
          "inputs": [
            "p0",
            "M"
          ]
        },
        {
          "output": "c1",
          "op": "OR",
          "inputs": [
            "g0",
            "h0"
          ]
        },
        {
          "output": "p1",
          "op": "XOR",
          "inputs": [
            "A1",
            "x1"
          ]
        },
        {
          "output": "g1",
          "op": "AND",
          "inputs": [
            "A1",
            "x1"
          ]
        },
        {
          "output": "s1",
          "op": "XOR",
          "inputs": [
            "p1",
            "c1"
          ]
        },
        {
          "output": "h1",
          "op": "AND",
          "inputs": [
            "p1",
            "c1"
          ]
        },
        {
          "output": "c2",
          "op": "OR",
          "inputs": [
            "g1",
            "h1"
          ]
        }
      ],
      "outputs": [
        [
          "S1",
          "s1"
        ],
        [
          "S0",
          "s0"
        ],
        [
          "Cout",
          "c2"
        ]
      ],
      "positions": []
    }
  }
]


def load_sample(key):
    sample = next((s for s in SAMPLES if s["id"] == key), None)
    if sample is None:
        raise ValueError("Unknown sample")
    return CircuitDocument.loads(json.dumps(sample["document"]))
