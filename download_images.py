import urllib.request
import os

images = [
    ("iphone15pro.jpg",    "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=800&hei=800&fmt=jpeg&qlt=90"),
    ("samsung_s24.jpg",    "https://fdn2.gsmarena.com/vv/bigpics/samsung-galaxy-s24-ultra-5g.jpg"),
    ("oneplus12.jpg",      "https://fdn2.gsmarena.com/vv/bigpics/oneplus-12.jpg"),
    ("macbook_air_m3.jpg", "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/macbook-air-midnight-config-20220606?wid=820&hei=498&fmt=jpeg&qlt=90"),
    ("dell_xps15.jpg",     "https://fdn2.gsmarena.com/vv/bigpics/dell-xps-15-9530.jpg"),
    ("asus_rog.jpg",       "https://fdn2.gsmarena.com/vv/bigpics/asus-rog-zephyrus-g14-2024.jpg"),
    ("sony_xm5.jpg",       "https://fdn2.gsmarena.com/vv/bigpics/sony-wh-1000xm5.jpg"),
    ("bose_qc45.jpg",      "https://fdn2.gsmarena.com/vv/bigpics/bose-quietcomfort-45.jpg"),
    ("jbl_flip6.jpg",      "https://fdn2.gsmarena.com/vv/bigpics/jbl-flip-6.jpg"),
    ("apple_watch9.jpg",   "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQDY3ref_VW_34FR+watch-45-alum-midnight-nc-9s_VW_34FR_WF_CO?wid=800&hei=800&fmt=jpeg&qlt=90"),
    ("samsung_watch6.jpg", "https://fdn2.gsmarena.com/vv/bigpics/samsung-galaxy-watch6-classic.jpg"),
    ("ps5.jpg",            "https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21?$facebook$"),
]

folder = os.path.join("static", "images", "products")
os.makedirs(folder, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for filename, url in images:
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        print(f"✅ Already exists: {filename}")
        continue
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(path, 'wb') as f:
                f.write(response.read())
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"❌ Failed: {filename} — {e}")

print("\n🎉 Done!")