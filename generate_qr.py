import qrcode

URL = "https://puppy.walmart.com/sharing/maa001e/consulta-items-cedi"

img = qrcode.make(URL, box_size=10, border=4)
img.save("QR_CONSULTA_ITEMS.png")
print("Listo! QR guardado para:", URL)
