# GreenGrid AI ⚡
### Generative AI-Powered Hyper-Local Peer-to-Peer Energy Trading System

GreenGrid AI is an intelligent neighborhood microgrid platform designed for 7 households to monitor renewable solar energy consumption, trade surplus power peer-to-peer (P2P), interact with real-time topology visualizations, and receive GenAI recommendations and 24/7 helpdesk support.

---

## 🌟 Key Features

- **P2P Energy Trading Engine**: Buy surplus solar power directly from neighboring households in real time with dynamic cost and carbon offset calculations.
- **7 Neighborhood Household Profiles**:
  1. **Srujana** (House 101) – Prosumer Node (Solar + Battery Storage)
  2. **Bhumi** (House 102) – Producer Node (7.0 kW Solar Array)
  3. **Yashu** (House 103) – Consumer Node
  4. **Harshi** (House 104) – Prosumer Node
  5. **Meghana** (House 105) – Prosumer Node
  6. **Pranavi** (House 106) – Producer Node (8.5 kW Solar Array - Lowest Rates)
  7. **Pooji** (House 107) – Prosumer Node
- **Interactive Microgrid Topology Map**: Real-time HTML5 Canvas rendering of 7 house nodes surrounding the Central AI Energy Hub with animated glowing energy particles (Green for supply, Orange for demand) and clickable node inspection modals.
- **Executive Analytics Dashboard**: 8 KPI Cards tracking Today's, Weekly, Monthly, and Yearly consumption, Available Energy, Wallet Balance (₹), Energy Sold, and Energy Bought, integrated with Chart.js graphs.
- **24/7 Helpdesk & Ticketing Assistant**: Floating chatbot with instant Q&A (cheapest rates, highest power appliances, member stats) and interactive support ticket creation (`TICKET-XXXX`) with escalation hotline (`+91 98765 43210`).

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, Flask Web Framework, Jinja2 Templates, Session Authentication
- **Frontend**: HTML5, Modern Vanilla CSS3 (Glassmorphism Dark Theme), JavaScript (ES6+)
- **Visualizations**: Chart.js for energy metrics & HTML5 Canvas for topology animation
- **Data Persistence**: JSON Database (`data/energy_data.json`)

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ installed on your system.

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/greengrid-ai.git
cd greengrid-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access in Browser
Open your browser and navigate to:
- **Local Address**: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔐 Demo Credentials

Log in using any of the 7 neighborhood member accounts:

| Member Name | House # | Username | Password | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Srujana** | House 101 | `srujana` | `12345` | Prosumer (Primary Admin) |
| **Bhumi** | House 102 | `bhumi` | `12345` | Producer Node |
| **Yashu** | House 103 | `yashu` | `12345` | Consumer Node |
| **Harshi** | House 104 | `harshi` | `12345` | Prosumer Node |
| **Meghana** | House 105 | `meghana` | `12345` | Prosumer Node |
| **Pranavi** | House 106 | `pranavi` | `12345` | Producer Node |
| **Pooji** | House 107 | `pooji` | `12345` | Prosumer Node |

---

## 📁 Project Architecture

```text
greengrid-ai/
├── app.py                  # Flask backend & API endpoints
├── test_app.py             # Unit test suite
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with AI Chatbot widget
│   ├── login.html          # Glassmorphism login page
│   ├── dashboard.html      # KPI cards & Chart.js graphs
│   ├── members.html        # 7 neighborhood household cards
│   ├── microgrid.html      # Interactive canvas topology map
│   ├── profile.html        # User statistics & solar specs
│   ├── trading.html        # P2P trade execution terminal
│   ├── transactions.html   # Transaction ledger table
│   └── notifications.html  # P2P energy request approval feed
│
├── static/                 # Static CSS & JS assets
│   ├── css/
│   │   ├── style.css       # Master visual design system
│   │   ├── dashboard.css   # KPI & chart styles
│   │   ├── members.css     # Household card styles
│   │   └── microgrid.css   # Canvas overlay styles
│   └── js/
│       ├── dashboard.js   # Chart.js graph logic
│       ├── trading.js     # P2P cost calculations & trade modal
│       ├── microgrid.js   # HTML5 Canvas topology animation
│       └── chatbot.js     # Helpdesk Q&A & ticket logging
│
└── data/
    └── energy_data.json   # Persistent JSON data store
```

---

## 📞 Support & Helpdesk Hotline
- **Grid Administrator**: Srujana (House 101)
- **Helpdesk Support Phone**: `+91 98765 43210`
- **Email**: `support@greengrid.ai`
