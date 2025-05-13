import cv2
import pytesseract

plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

def processar_placa_veicular(caminho_imagem):
    img_original_cv = cv2.imread(caminho_imagem)
    if img_original_cv is None:
        raise FileNotFoundError(f"Imagem não encontrada ou não pode ser carregada: {caminho_imagem}")

    # Detectar placa usando Haar Cascade
    gray = cv2.cvtColor(img_original_cv, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60,20))
    if len(plates) > 0:
        x, y, w, h = plates[0]
        img_destacada_cv = img_original_cv[y:y+h, x:x+w]
        texto = pytesseract.image_to_string(img_destacada_cv, config='--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        return img_original_cv, img_destacada_cv, texto.strip(), (int(x), int(y), int(w), int(h))
    else:
        return img_original_cv, None, "Placa não localizada na imagem.", None
