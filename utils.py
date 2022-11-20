import cv2
from pyzbar.pyzbar import decode
import json
from urllib.request import urlopen

composte_ready = ['wafle-kukurydziane']

def BarcodeReader(image):
    img = cv2.imread(image)
    detectedBarcodes = decode(img)
    if not detectedBarcodes:
        return -1
    else:
        for barcode in detectedBarcodes:
            return barcode.data
 
def getProductInfo(code):
    response = urlopen(f"https://world.openfoodfacts.org/api/v0/product/{code}.json")
    try:
        data = json.loads(response.read())['product']['categories_tags'][0]
    except:
        data = "no such data"
    print(data)
    if data in composte_ready:
        return True
    else:
        return False
print(getProductInfo(BarcodeReader("IMG_0649.jpg")))
