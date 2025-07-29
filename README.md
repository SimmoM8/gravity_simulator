# Gravity Simulator 2

A real-time, interactive gravity simulation built in Python using `pygame` and `pygame_gui`. This tool allows users to create, modify, and observe the behavior of celestial objects under Newtonian gravitational physics in a 2D space.

## 🚀 Features

- 🪐 **Add/Edit/Delete Objects** with custom mass, radius, position, and velocity
- 🌌 **Realistic Gravity Simulation** using Newton’s law of universal gravitation
- 🧭 **Vector Field Visualization**: Toggleable directional field to show gravitational pull across space
- 🕒 **Time & Trail Control**:
  - Adjustable trail length (in seconds)
  - Show/hide object trails and velocity vectors
- 🎥 **Camera Control**:
  - Pan and zoom with mouse or keyboard
  - Dynamic scaling bar that adjusts with zoom level
- 🧠 **Preset Management**: Load preset object configurations via dropdown
- 🧪 **Collision Detection** with elastic collision response
- 🧰 **Extensible UI** framework (custom panel/page system)

## 🖼️ Screenshots

> *(Add screenshots or GIFs here once available)*

---

## 🛠️ Getting Started

### 🔧 Requirements

- Python 3.9 or newer
- `pygame`
- `pygame_gui`
- `numpy`

### 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### ▶️ Run the simulator

```bash
python main.py
```

> Make sure to run from the project root directory.

---

## 📁 Project Structure

```
gravity_simulator_2/
├── main.py                      # Entry point
├── core/
│   ├── gravity_simulator_2.py  # Main app class
│   ├── scene.py                # Physics simulation engine
│   ├── vector_field.py         # Vector field calculations
│   └── camera.py               # Camera zoom/pan logic
├── ui/
│   ├── ui_manager.py           # UI state manager
│   ├── ui_events.py            # Event handling
│   ├── ui_actions.py           # Button, slider, input logic
│   ├── ui_panels.py            # UI layout definition
│   └── panel_builder.py        # Builds UI panels
├── setup/
│   ├── config.py               # Constants & settings
│   └── presets.py              # Object presets
└── requirements.txt
```

---

## 📦 Executable Version

To build a standalone `.exe` without requiring Python:

```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

Find the `.exe` in the `dist/` folder.

---

## 💾 Download & Run the Executable

If you have downloaded a packaged version of Gravity Simulator 2, follow these simple steps to run it:

- **For Windows:**
  1. Download the `.zip` file containing the executable.
  2. Extract the `.zip` archive.
  3. Double-click the `.exe` file to launch the simulator.

- **For Mac:**
  1. Download the `.zip` file containing the application.
  2. Extract the `.zip` archive.
  3. Double-click the app to open and run the simulator.

No installation or additional setup is needed.

---

## 🧠 Physics Model

- Gravitational force between objects
- Elastic collision resolution using coefficient of restitution
- Euler integration for velocity/position updates
- Trail rendering and vector visualization per frame

---

## 📌 Future Features

- Heatmap-style gravity field visualization
- Save/load custom simulations
- 3D simulation engine (planned)

---

## 👤 Author

**Benjamin Simmons**  
[GitHub: @SimmoM8](https://github.com/SimmoM8)

---

## 📄 License

MIT License

Copyright (c) 2025 Benjamin Simmons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
