# BachatCart India 🇮🇳
### Quick-Commerce & Hyperlocal Grocery Price Arbitrage Engine

BachatCart India is an Indian quick-commerce price arbitrage application that compares grocery baskets in real-time across 8 major delivery platforms, calculates combinatorial 2-store split savings (*Bachat Jugaad*), models platform surcharges (delivery waivers, handling fees, bag fees), and features an interactive AI voice search assistant.

---

## 🚀 Quick Start & Local Preview

### Prerequisites
- Python 3.8+ (already available on standard development environments)
- Modern web browser (Chrome, Edge, Safari, or Firefox)

### 1. Launch the Local Server
From the project folder:
```bash
python server.py
```
Or with `npm`:
```bash
npm start
```

### 2. Open in Browser
Open your browser and navigate to:
```
http://localhost:3000
```

---

## ⚡ Modeled Platforms & Fee Mechanics

| Platform | Delivery Fee | Free Delivery Threshold | Handling Fee | Bag Fee |
| :--- | :--- | :--- | :--- | :--- |
| **Blinkit** | ₹25 | Free over ₹249 | ₹16 | ₹5 |
| **Zepto** | ₹30 | Free over ₹249 | ₹10 | ₹5 |
| **Swiggy Instamart** | ₹25 | Free over ₹299 | ₹6 | ₹9 |
| **Flipkart Minutes** | ₹20 | Free over ₹199 | ₹7 | ₹5 |
| **BigBasket / BB Now** | ₹30 | Free over ₹450 | ₹0 | ₹6 |
| **Amazon Now / Fresh** | ₹35 | Free over ₹499 | ₹0 | ₹0 |
| **KPN Farm Fresh** *(Kovai Pazhamudir Nilayam)* | ₹25 | Free over ₹299 | ₹0 | ₹4 |
| **First Club** *(Country Delight)* | ₹20 | Free over ₹199 | ₹0 | ₹0 |

---

## 💡 Key Architectural Features

1. **Single-App Champion vs. Smart Split (Bachat Jugaad)**:
   - **Single-App Champion**: Finds the single cheapest platform for the entire order, calculating exact delivery threshold waivers and handling surcharges.
   - **Smart Split Engine**: Tests combinatorial store pairings and partitions items to the cheapest available store, accounting for dual delivery and handling charges.

2. **AI Voice Search Assistant**:
   - Integrated with Web Speech API (`SpeechRecognition` & `SpeechSynthesis`).
   - Query by voice (e.g., *"How much is 1kg onion?"*, *"Cheapest Nandini milk 1L"*).
   - Audio toggle to mute/unmute spoken verdicts.
   - Simulated voice prompt chips for instant testing even without microphone access.

3. **WhatsApp / Notepad List Importer**:
   - Paste natural shopping lists directly from WhatsApp or Notes.
   - Regex and fuzzy keyword matcher maps text to catalog items and quantities.

4. **Serviceability Bar**:
   - Toggle individual store availability to reflect specific PIN code coverage in Indian metros (Bengaluru, Mumbai, Delhi-NCR, Chennai, Hyderabad).

---

## 📁 Project Structure
```
bachatcart-india/
├── index.html        # Self-contained frontend application
├── server.py         # Python HTTP server running on port 3000
├── package.json      # Metadata and start script
└── README.md         # Documentation & guide
```
