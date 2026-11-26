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
    }
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
    }
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
    }
  }
]


def load_sample(key):
    sample = next((s for s in SAMPLES if s["id"] == key), None)
    if sample is None:
        raise ValueError("Unknown sample")
    return CircuitDocument.loads(json.dumps(sample["document"]))
