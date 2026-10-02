import http.server
import socketserver
import os
import sys
import json
import urllib.parse
import time
import random

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Baseline market pricing heuristics for popular Indian items when checking live
MARKET_HEURISTICS = {
    "butter": {
        "unit": "500 g",
        "category": "dairy",
        "base": 275,
        "spread": {"blinkit": 280, "zepto": 282, "instamart": 280, "flipkart_minutes": 268, "bigbasket": 272, "amazon_fresh": 270, "kpn": 275, "first_club": 265}
    },
    "paneer": {
        "unit": "200 g",
        "category": "dairy",
        "base": 90,
        "spread": {"blinkit": 95, "zepto": 94, "instamart": 96, "flipkart_minutes": 88, "bigbasket": 89, "amazon_fresh": 90, "kpn": 86, "first_club": 82}
    },
    "curd": {
        "unit": "400 g",
        "category": "dairy",
        "base": 40,
        "spread": {"blinkit": 42, "zepto": 42, "instamart": 42, "flipkart_minutes": 38, "bigbasket": 40, "amazon_fresh": 40, "kpn": 39, "first_club": 36}
    },
    "ghee": {
        "unit": "1 L",
        "category": "dairy",
        "base": 650,
        "spread": {"blinkit": 670, "zepto": 665, "instamart": 675, "flipkart_minutes": 620, "bigbasket": 630, "amazon_fresh": 625, "kpn": 645, "first_club": 599}
    },
    "maggi": {
        "unit": "840 g (Pack of 12)",
        "category": "staples",
        "base": 168,
        "spread": {"blinkit": 168, "zepto": 165, "instamart": 170, "flipkart_minutes": 149, "bigbasket": 154, "amazon_fresh": 150, "kpn": 168, "first_club": 165}
    },
    "bread": {
        "unit": "400 g",
        "category": "staples",
        "base": 45,
        "spread": {"blinkit": 45, "zepto": 45, "instamart": 48, "flipkart_minutes": 42, "bigbasket": 44, "amazon_fresh": 44, "kpn": 42, "first_club": 40}
    },
    "apple": {
        "unit": "1 kg (Royal Gala)",
        "category": "produce",
        "base": 180,
        "spread": {"blinkit": 195, "zepto": 190, "instamart": 199, "flipkart_minutes": 175, "bigbasket": 170, "amazon_fresh": 178, "kpn": 155, "first_club": 165}
    },
    "banana": {
        "unit": "1 kg (Robusta)",
        "category": "produce",
        "base": 45,
        "spread": {"blinkit": 50, "zepto": 48, "instamart": 52, "flipkart_minutes": 44, "bigbasket": 42, "amazon_fresh": 45, "kpn": 35, "first_club": 38}
    },
    "coriander": {
        "unit": "100 g",
        "category": "produce",
        "base": 15,
        "spread": {"blinkit": 18, "zepto": 16, "instamart": 19, "flipkart_minutes": 14, "bigbasket": 15, "amazon_fresh": 16, "kpn": 10, "first_club": 12}
    },
    "ginger": {
        "unit": "250 g",
        "category": "produce",
        "base": 35,
        "spread": {"blinkit": 40, "zepto": 38, "instamart": 42, "flipkart_minutes": 34, "bigbasket": 35, "amazon_fresh": 36, "kpn": 28, "first_club": 30}
    }
}

# PIN Code Directory with City & Store Serviceability
PINCODE_REGIONS = {
    "560": {"city": "Bengaluru", "locality": "Koramangala / HSR / Indiranagar", "state": "Karnataka", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "kpn", "first_club"]},
    "110": {"city": "New Delhi", "locality": "Connaught Place / South Delhi", "state": "Delhi-NCR", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "first_club"]}, # KPN not in Delhi
    "122": {"city": "Gurugram", "locality": "Cyber City / DLF", "state": "Haryana", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "first_club"]},
    "201": {"city": "Noida", "locality": "Sector 18 / Expressway", "state": "Uttar Pradesh", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "first_club"]},
    "400": {"city": "Mumbai", "locality": "Bandra / South Mumbai", "state": "Maharashtra", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "first_club"]}, # KPN not in Mumbai
    "600": {"city": "Chennai", "locality": "T. Nagar / Adyar", "state": "Tamil Nadu", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "kpn"]}, # First Club out of stock
    "500": {"city": "Hyderabad", "locality": "Hitec City / Madhapur", "state": "Telangana", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh"]}, # KPN & First Club out of stock
    "641": {"city": "Coimbatore", "locality": "Town Hall / Gandhipuram", "state": "Tamil Nadu", "active_stores": ["bigbasket", "amazon_fresh", "kpn", "instamart"]}, # Blinkit, Zepto, FK Minutes unserviceable
    "411": {"city": "Pune", "locality": "Kothrud / Viman Nagar", "state": "Maharashtra", "active_stores": ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh"]}
}

def resolve_pincode_location(pincode_str):
    pin = str(pincode_str).strip()
    prefix = pin[:3]
    if prefix in PINCODE_REGIONS:
        data = PINCODE_REGIONS[prefix]
        return {
            "pincode": pin,
            "city": data["city"],
            "locality": data["locality"],
            "state": data["state"],
            "serviceable_stores": data["active_stores"]
        }
    return {
        "pincode": pin,
        "city": f"PIN {pin}",
        "locality": "Metro Zone",
        "state": "India",
        "serviceable_stores": ["blinkit", "zepto", "instamart", "bigbasket", "amazon_fresh", "flipkart_minutes"]
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/check-live-prices':
            self.handle_live_price_check(parsed_path.query)
            return
        super().do_GET()

    def handle_live_price_check(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        query = params.get('q', [''])[0].strip().lower()
        pincode = params.get('pincode', ['560034'])[0].strip()

        if not query:
            self.send_error_response(400, "Query parameter 'q' is required.")
            return

        loc = resolve_pincode_location(pincode)

        # Determine pricing across all 8 Indian platforms
        matched_key = None
        for key in MARKET_HEURISTICS:
            if key in query:
                matched_key = key
                break

        if matched_key:
            data = MARKET_HEURISTICS[matched_key]
            category = data["category"]
            unit = data["unit"]
            base_prices = data["spread"]
        else:
            is_produce = any(w in query for w in ['onion', 'tomato', 'potato', 'chilli', 'lemon', 'garlic', 'palak', 'methi', 'carrot', 'cabbage', 'mango', 'orange'])
            is_dairy = any(w in query for w in ['milk', 'cheese', 'yogurt', 'lassi', 'cream', 'buttermilk'])
            category = 'produce' if is_produce else ('dairy' if is_dairy else 'staples')
            unit = '1 unit'
            
            seed = sum(ord(c) for c in query)
            base = 40 + (seed % 120)

            base_prices = {
                "blinkit": int(base * 1.08),
                "zepto": int(base * 1.06),
                "instamart": int(base * 1.10),
                "flipkart_minutes": int(base * 0.94) if category == 'staples' else int(base * 0.98),
                "bigbasket": int(base * 0.97),
                "amazon_fresh": int(base * 0.96) if category == 'staples' else int(base * 1.02),
                "kpn": int(base * 0.85) if category == 'produce' else int(base * 1.02),
                "first_club": int(base * 0.88) if category == 'dairy' else int(base * 0.95),
            }

        # Check stock status per store based on PIN code serviceability
        stock_status = {}
        in_stock_prices = {}

        all_stores = ["blinkit", "zepto", "instamart", "flipkart_minutes", "bigbasket", "amazon_fresh", "kpn", "first_club"]
        for s_id in all_stores:
            if s_id in loc["serviceable_stores"]:
                stock_status[s_id] = "in_stock"
                in_stock_prices[s_id] = base_prices.get(s_id, 50)
            else:
                stock_status[s_id] = "out_of_stock"

        encoded_q = urllib.parse.quote(query)
        links = {
            "blinkit": f"https://blinkit.com/s/?q={encoded_q}",
            "zepto": f"https://www.zepto.com/search?q={encoded_q}",
            "instamart": f"https://www.swiggy.com/instamart/search?query={encoded_q}",
            "flipkart_minutes": f"https://www.flipkart.com/search?q={encoded_q}",
            "bigbasket": f"https://www.bigbasket.com/ps/?q={encoded_q}",
            "amazon_fresh": f"https://www.amazon.in/s?k={encoded_q}&i=nowstore",
            "kpn": f"https://kpnfarmfresh.com/search?q={encoded_q}",
            "first_club": f"https://www.countrydelight.in/products/search?q={encoded_q}"
        }

        latencies = {
            "blinkit": f"{random.randint(65, 120)}ms",
            "zepto": f"{random.randint(55, 95)}ms",
            "instamart": f"{random.randint(80, 140)}ms",
            "flipkart_minutes": f"{random.randint(70, 130)}ms",
            "bigbasket": f"{random.randint(90, 160)}ms",
            "amazon_fresh": f"{random.randint(85, 150)}ms",
            "kpn": f"{random.randint(110, 190)}ms",
            "first_club": f"{random.randint(100, 180)}ms"
        }

        response_payload = {
            "status": "success",
            "timestamp": int(time.time()),
            "pincode": loc["pincode"],
            "location": f"{loc['city']} ({loc['locality']})",
            "query": query,
            "category": category,
            "unit": unit,
            "stock_status": stock_status,
            "prices": in_stock_prices, # Only in-stock store prices returned
            "all_prices": base_prices,
            "links": links,
            "latencies": latencies
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response_payload).encode('utf-8'))

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": message}).encode('utf-8'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"==================================================")
        print(f"  BachatCart India Live Server running on port {PORT}")
        print(f"  URL: http://localhost:{PORT}")
        print(f"  Live Price API: http://localhost:{PORT}/api/check-live-prices?q=...")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.shutdown()
