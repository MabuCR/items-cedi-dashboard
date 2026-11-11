import qrcode

URL = "https://mabucr.github.io/items-cedi-dashboard/"

img = qrcode.make(URL, box_size=10, border=4)
img.save("QR_GITHUB_PAGES.png")
print("Listo! QR guardado para:", URL)
