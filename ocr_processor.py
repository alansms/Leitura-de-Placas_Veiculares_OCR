import cv2
import pytesseract
from PIL import Image
import numpy as np

# Configuração do caminho do Tesseract (ajuste se necessário para seu ambiente)
# No Streamlit Cloud, isso geralmente é tratado pela configuração do ambiente.
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def carregar_imagem(caminho_imagem):
    """Carrega uma imagem a partir de um caminho de arquivo."""
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem do caminho: {caminho_imagem}")
    return imagem

def carregar_imagem_pil(stream_imagem):
    """Carrega uma imagem a partir de um stream (ex: UploadedFile do Streamlit)."""
    imagem_pil = Image.open(stream_imagem)
    # Converte para formato OpenCV (BGR)
    imagem_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    return imagem_cv

if __name__ == '__main__':
    # Exemplo de uso (para teste local)
    try:
        # Crie uma imagem de teste chamada 'placa_teste.png' no mesmo diretório
        # ou substitua pelo caminho de uma imagem de placa real.
        # Para este exemplo, vamos apenas simular o carregamento.
        print("Módulo ocr_processor.py carregado.")
        print("Para testar, crie uma imagem 'placa_teste.png' ou similar e descomente o código abaixo.")
        # img = carregar_imagem('placa_teste.png')
        # cv2.imshow('Imagem Carregada', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    except Exception as e:
        print(f"Erro no teste: {e}")



def pre_processar_imagem(imagem):
    """Aplica pré-processamento na imagem para melhorar a detecção do OCR."""
    # 1. Conversão para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    # 2. Binarização adaptativa para destacar texto
    # O threshold adaptativo pode ser melhor para condições de iluminação variáveis
    imagem_binarizada = cv2.adaptiveThreshold(
        imagem_cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2 # O 11 e 2 são blockSize e C, podem precisar de ajuste
    )
    
    # (Opcional) Aplicar um desfoque gaussiano leve para reduzir ruído antes da binarização
    # imagem_cinza_blur = cv2.GaussianBlur(imagem_cinza, (5, 5), 0)
    # _, imagem_binarizada_otsu = cv2.threshold(imagem_cinza_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # (Opcional) Outras técnicas como detecção de bordas (Canny) ou operações morfológicas (erosão, dilatação)
    # poderiam ser exploradas aqui dependendo da qualidade das imagens de entrada.

    return imagem_binarizada, imagem_cinza




def encontrar_area_placa(imagem_original, imagem_processada):
    """Tenta encontrar a área da placa na imagem processada e retorna as coordenadas.
       Retorna também a imagem original com a placa destacada se encontrada.
    """
    # Encontrar contornos na imagem binarizada
    # Usamos RETR_EXTERNAL para obter apenas os contornos externos
    # Usamos CHAIN_APPROX_SIMPLE para economizar memória
    contornos, _ = cv2.findContours(imagem_processada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    imagem_com_placa_destacada = imagem_original.copy()
    area_placa_img = None
    coordenadas_placa = None # (x, y, w, h)

    # Iterar sobre os contornos encontrados
    for contorno in contornos:
        # Aproximar o contorno para um polígono
        perimetro = cv2.arcLength(contorno, True)
        aproximacao = cv2.approxPolyDP(contorno, 0.02 * perimetro, True) # 0.018 a 0.03 é um bom range para o epsilon

        # Assumimos que uma placa é aproximadamente retangular (4 vértices)
        if len(aproximacao) == 4:
            x, y, w, h = cv2.boundingRect(aproximacao)
            
            # Filtrar por proporção (aspect ratio) e área mínima/máxima
            # Proporção típica de placas brasileiras (Mercosul: 40x13cm -> ~3.07, Antigas: ~3.0 a 4.0)
            proporcao = w / float(h)
            area = cv2.contourArea(contorno)

            # Esses valores são empíricos e podem precisar de ajuste
            if 2.0 < proporcao < 5.0 and area > 1000 and w > 80 and h > 20: # Ajustar área mínima e dimensões
                # Desenhar o retângulo na imagem original
                cv2.rectangle(imagem_com_placa_destacada, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Recortar a região da placa da imagem original (em escala de cinza para OCR)
                # É melhor passar a imagem em escala de cinza original para o OCR, não a binarizada diretamente
                # para evitar perda de informação, mas a binarizada ajudou a encontrar.
                imagem_cinza_original = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)
                area_placa_img = imagem_cinza_original[y:y+h, x:x+w]
                coordenadas_placa = (x, y, w, h)
                #print(f"Placa potencial encontrada: x={x}, y={y}, w={w}, h={h}, proporcao={proporcao:.2f}, area={area}")
                break # Assumir que a primeira placa encontrada com bons critérios é a correta
    
    if area_placa_img is None:
        #print("Nenhuma placa encontrada com os critérios definidos. Tentando OCR na imagem inteira (processada).")
        # Se nenhuma placa for isolada, pode-se tentar OCR na imagem inteira (pré-processada)
        # ou retornar None para indicar que a placa não foi localizada.
        # Para este caso, retornaremos None para area_placa_img se não for encontrada.
        pass

    return area_placa_img, imagem_com_placa_destacada, coordenadas_placa




def extrair_texto_da_placa(imagem_area_placa):
    """Extrai texto da imagem da área da placa usando Tesseract OCR."""
    if imagem_area_placa is None:
        return "Placa não detectada ou ilegível"

    # Configurações do Tesseract
    # --psm 6: Assumir um único bloco uniforme de texto.
    # --psm 7: Tratar a imagem como uma única linha de texto.
    # --psm 8: Tratar a imagem como uma única palavra.
    # --psm 13: Modo Raw line. Tratar a imagem como uma única linha de texto, bypassando hacks específicos do Tesseract.
    # Para placas, PSM 7 ou 8 costumam funcionar bem. PSM 6 também pode ser útil.
    # O idioma 'por' é para português.
    # O parâmetro -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 define os caracteres esperados.
    config_tesseract = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' # PSM 6 é um bom ponto de partida
    
    try:
        # Aplicar um pequeno pré-processamento adicional na área da placa pode ajudar
        # Aumentar o tamanho da imagem da placa pode melhorar a precisão do OCR
        altura, largura = imagem_area_placa.shape[:2]
        if altura > 0 and largura > 0:
            imagem_area_placa_redimensionada = cv2.resize(imagem_area_placa, (largura*2, altura*2), interpolation=cv2.INTER_CUBIC)
        else:
            imagem_area_placa_redimensionada = imagem_area_placa

        # Binarização Otsu na região da placa pode ser útil se não foi feito antes ou se a iluminação variar muito
        # _, imagem_placa_bin = cv2.threshold(imagem_area_placa_redimensionada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Tentar com a imagem em escala de cinza redimensionada
        texto_placa = pytesseract.image_to_string(Image.fromarray(imagem_area_placa_redimensionada), lang='por', config=config_tesseract)
        
        # Limpeza básica do texto extraído
        texto_placa_limpo = ''.join(filter(str.isalnum, texto_placa)).upper()
        
        # Heurística simples para validar se parece uma placa (ex: 7 caracteres)
        # if len(texto_placa_limpo) < 5 or len(texto_placa_limpo) > 7: # Ajustar conforme o padrão de placa esperado
            # print(f"Texto extraído ({texto_placa_limpo}) não parece uma placa válida. Tentando PSM 7.")
            # config_tesseract_psm7 = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            # texto_placa_psm7 = pytesseract.image_to_string(Image.fromarray(imagem_area_placa_redimensionada), lang='por', config=config_tesseract_psm7)
            # texto_placa_limpo_psm7 = ''.join(filter(str.isalnum, texto_placa_psm7)).upper()
            # if len(texto_placa_limpo_psm7) >= 5 and len(texto_placa_limpo_psm7) <= 7:
                # return texto_placa_limpo_psm7
        
        return texto_placa_limpo if texto_placa_limpo else "Texto não extraído"

    except pytesseract.TesseractNotFoundError:
        return "Erro: Tesseract não encontrado. Verifique a instalação e o PATH."
    except Exception as e:
        return f"Erro na extração de texto: {str(e)}"

# Função principal para orquestrar o processo
def processar_placa_veicular(imagem_entrada):
    """Processa uma imagem de placa veicular, realizando pré-processamento, detecção e OCR."""
    if isinstance(imagem_entrada, str): # Se for um caminho de arquivo
        imagem_original = carregar_imagem(imagem_entrada)
    else: # Se for um stream de bytes (UploadedFile do Streamlit)
        imagem_original = carregar_imagem_pil(imagem_entrada)

    imagem_processada_bin, _ = pre_processar_imagem(imagem_original)
    area_placa_recortada, imagem_com_destaque, coords = encontrar_area_placa(imagem_original, imagem_processada_bin)
    
    texto_extraido = ""
    if area_placa_recortada is not None:
        texto_extraido = extrair_texto_da_placa(area_placa_recortada)
    else:
        # Se a placa não foi detectada, tentar OCR na imagem inteira (pode ser menos preciso)
        # print("Placa não detectada. Tentando OCR na imagem inteira pré-processada (binarizada).")
        # texto_extraido = extrair_texto_da_placa(imagem_processada_bin) # Usar a binarizada inteira
        texto_extraido = "Placa não localizada na imagem."

    return imagem_original, imagem_com_destaque, texto_extraido, coords

if __name__ == '__main__':
    print("Módulo ocr_processor.py - Teste de processamento completo")
    # Crie uma imagem de teste 'teste_placa.jpg' ou 'teste_placa.png'
    # no mesmo diretório para testar o fluxo completo.
    # Exemplo:
    # try:
    #     img_original, img_destacada, texto, _ = processar_placa_veicular('caminho_para_sua_imagem_de_placa.png')
    #     print(f"Texto da Placa: {texto}")
    #     cv2.imshow('Original', img_original)
    #     cv2.imshow('Placa Destacada', img_destacada)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    # except Exception as e:
    #     print(f"Erro no processamento: {e}")

