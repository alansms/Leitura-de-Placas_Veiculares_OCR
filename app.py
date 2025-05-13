import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import pytesseract
import re
from paddleocr import PaddleOCR

os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
# Torch/Streamlit workaround: evita inspeção de módulos __path__ quebrados

paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

# Importar funções dos módulos fornecidos pelo usuário
from processar_imagem import processar_imagem
from processar_contornos import processar_contornos
from aplicar_ocr import aplicar_ocr
# A função exibir_resultado de utils.py usa matplotlib, que não é ideal para Streamlit.
# Vamos recriar a lógica de exibição diretamente no Streamlit ou adaptar utils.py se necessário.

st.set_page_config(layout="wide", page_title="Leitor de Placas Veiculares OCR v2")

st.title("🚗 Leitura de Placas Veiculares com OCR (Base no Código Fornecido)")
st.markdown("""
Esta aplicação utiliza o código fornecido para extrair o texto de placas veiculares
a partir de imagens. Você pode fazer o upload de uma imagem local ou usar a câmera do seu dispositivo.
""")

# Configuração do Tesseract (IMPORTANTE: Remover ou comentar a linha pytesseract.pytesseract.tesseract_cmd do código original)
# No Streamlit Cloud, o Tesseract é instalado via packages.txt e deve estar no PATH.
# Se estiver testando localmente e o Tesseract não estiver no PATH, você pode precisar configurá-lo aqui temporariamente,
# mas para deploy, a configuração via packages.txt é o ideal.
# Exemplo: # import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # Ajuste para seu ambiente local se necessário

TEMP_IMAGE_DIR = "temp_images_v2"
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

def corrigir_inclinacao(imagem):
    # Converte para escala de cinza
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    # Parâmetros suavizados para Canny e HoughLinesP
    edges = cv2.Canny(gray, 50, 150, apertureSize=3, L2gradient=True)
    # Parâmetros mais flexíveis para linhas
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=40, maxLineGap=30)
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Considera apenas linhas próximas da horizontal
            if -45 < angle < 45:
                angles.append(angle)
        if angles:
            angle = np.mean(angles)
            (h, w) = imagem.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(imagem, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            return rotated_image
    return imagem  # Se não encontrar linhas, retorna a imagem original

def adaptar_e_processar_placa(imagem_bytes_ou_path):
    """Adapta a lógica do main.py fornecido para processar uma imagem e retornar os resultados."""
    try:
        if isinstance(imagem_bytes_ou_path, str): # Se for um caminho de arquivo
            imagem_original_cv = cv2.imread(imagem_bytes_ou_path)
            if imagem_original_cv is None:
                raise ValueError(f"Não foi possível carregar a imagem do caminho: {imagem_bytes_ou_path}")
        else: # Se for um stream de bytes (UploadedFile do Streamlit ou CameraInput)
            pil_image = Image.open(imagem_bytes_ou_path)
            imagem_original_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Corrigir inclinação logo após carregar a imagem
        imagem_original_cv = corrigir_inclinacao(imagem_original_cv)
        st.write("[DEBUG] Imagem original carregada e corrigida com sucesso.")

        # 1. Pré-processamento da imagem (do processar_imagem.py)
        imagem_processada_cv = processar_imagem(imagem_original_cv)

        st.write("[DEBUG] Imagem pré-processada para contornos.")

        # 2. Processamento de Contornos (do processar_contornos.py)
        # Parâmetros suavizados para caso a imagem não esteja nítida
        lista_possiveis_placas = processar_contornos(
            imagem_original_cv.copy(),
            imagem_processada_cv.copy()
        )
        if lista_possiveis_placas is None:
            st.warning("Nenhuma lista de possíveis placas retornada pelo processar_contornos (NoneType).")
            lista_possiveis_placas = []

        st.write(f"[DEBUG] {len(lista_possiveis_placas)} possíveis placas detectadas por contornos.")

        if not lista_possiveis_placas:
            st.write("[DEBUG] Nenhuma placa detectada. Tentando Haar Cascade.")
            # Fallback de detecção via Haar Cascade
            gray_full = cv2.cvtColor(imagem_original_cv, cv2.COLOR_BGR2GRAY)
            plates = plate_cascade.detectMultiScale(gray_full, scaleFactor=1.1, minNeighbors=3, minSize=(50, 15))
            st.write(f"[DEBUG] {len(plates)} placas detectadas pelo Haar Cascade.")
            if len(plates) > 0:
                # Selecionar a maior placa detectada (caso haja várias)
                plates = sorted(plates, key=lambda x: x[2] * x[3], reverse=True)
                x, y, w, h = plates[0]
                # Ajuste dos parâmetros de recorte: aumentar o retângulo para garantir que a placa seja totalmente capturada
                margem_x = int(w * 0.20)  # Aumentar 20% nas laterais
                margem_y_sup = int(h * 0.25)  # Aumentar 25% acima
                margem_y_inf = int(h * 0.20)  # Aumentar 20% abaixo
                x_ini = max(x - margem_x, 0)
                x_fim = min(x + w + margem_x, imagem_original_cv.shape[1])
                y_ini = max(y - margem_y_sup, 0)
                y_fim = min(y + h + margem_y_inf, imagem_original_cv.shape[0])
                recorte = imagem_original_cv[y_ini: y_fim, x_ini: x_fim]
                # Redimensionar para aumentar a qualidade do OCR (ex: 3x o tamanho padrão de placa)
                target_width, target_height = 660, 210  # 3x (220x70)
                recorte = cv2.resize(recorte, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
                # Pré-processamento do recorte para melhorar leitura
                gray_plate = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
                placa_denoise = cv2.bilateralFilter(gray_plate, 7, 15, 15)
                blur = cv2.GaussianBlur(placa_denoise, (7, 7), 0)
                placa_eq = cv2.equalizeHist(blur)
                placa_thresh = cv2.adaptiveThreshold(placa_eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 3)
                # OCR primário: Tesseract
                st.write("[DEBUG] Tentando OCR com Tesseract.")
                config_tess = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                texto = pytesseract.image_to_string(placa_thresh, config=config_tess).strip()
                texto = texto.replace("MERCOSUL", "").replace("BRASIL", "")
                # Fallback de OCR melhorado
                if not texto or texto == "" or texto.isspace():
                    try:
                        st.write("[DEBUG] Tentando fallback com PaddleOCR (ajuste adaptativo).")
                        # Fallback: usar imagem sem threshold, apenas equalizada se necessário
                        resultado = paddle_ocr.ocr(placa_eq, cls=True)
                        texto = ""
                        for linha in resultado or []:
                            for palavra in linha:
                                texto += palavra[1][0] + " "
                        texto = texto.strip()
                        # Se ainda falhar, tenta com a imagem original recortada
                        if not texto or texto == "" or texto.isspace():
                            resultado = paddle_ocr.ocr(recorte, cls=True)
                            texto = ""
                            for linha in resultado or []:
                                for palavra in linha:
                                    texto += palavra[1][0] + " "
                            texto = texto.strip()
                    except Exception as e:
                        st.warning(f"Erro ao usar PaddleOCR como fallback: {e}")
                # Se o texto extraído não for válido, use uma expressão regular para validar se o texto corresponde ao padrão de placa
                texto_limpo = re.sub(r'[^A-Za-z0-9]', '', texto).upper()
                m_final = re.search(r'[A-Z]{3}[0-9]{4}', texto_limpo)
                if m_final:
                    texto = m_final.group()
                else:
                    texto = texto_limpo or "Nenhum texto extraído"
                return imagem_original_cv, recorte, texto, placa_denoise, placa_thresh
            return imagem_original_cv, None, "Nenhuma placa encontrada após ajustes.", None, None

        # 3. Aplicar OCR (do aplicar_ocr.py)
        # Se lista_possiveis_placas está vazia, evitar passar para aplicar_ocr e retornar resultado padrão
        if not lista_possiveis_placas:
            return imagem_original_cv, None, "Nenhuma placa encontrada após ajustes.", imagem_processada_cv, None

        resultado_ocr = aplicar_ocr(lista_possiveis_placas)

        if resultado_ocr:
            texto_placa, placa_recortada_cv, placa_recortada_processada_ocr_cv = resultado_ocr
            st.write("[DEBUG] Texto retornado pelo aplicar_ocr:", texto_placa)

            # Validação do texto vindo do aplicar_ocr; força fallback se não for placa válida
            padrao_brasil   = r'^[A-Z]{3}[0-9]{4}$'          # formato antigo ABC1234
            padrao_mercosul = r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$'  # formato Mercosul ABC1D23
            if not re.fullmatch(padrao_brasil, texto_placa) and not re.fullmatch(padrao_mercosul, texto_placa):
                st.write("[DEBUG] Texto não bate com padrão de placa. Forçando fallback PaddleOCR.")
                texto_placa = ""  # isso dispara o bloco de fallback logo abaixo

            if not texto_placa or texto_placa == "Texto não extraído":
                try:
                    st.write("[DEBUG] Tentando fallback com PaddleOCR (adaptativo).")
                    placa_gray = cv2.cvtColor(placa_recortada_cv, cv2.COLOR_BGR2GRAY)
                    placa_denoise = cv2.bilateralFilter(placa_gray, 7, 15, 15)
                    blur = cv2.GaussianBlur(placa_denoise, (7, 7), 0)
                    placa_eq = cv2.equalizeHist(blur)
                    placa_thresh = cv2.adaptiveThreshold(placa_eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                         cv2.THRESH_BINARY, 17, 3)
                    # Testa PaddleOCR com diferentes versões da imagem
                    texto_placa_raw = ""
                    for img_try in [placa_thresh, placa_eq, placa_recortada_cv]:
                        resultado = paddle_ocr.ocr(img_try, cls=True)
                        raw = ""
                        for linha in resultado or []:
                            for palavra in linha:
                                raw += palavra[1][0] + " "
                        raw = raw.strip().replace("MERCOSUL", "").replace("BRASIL", "")
                        if raw:
                            texto_placa_raw = raw
                            break
                    st.write("[DEBUG] Texto OCR completo (pré-limpeza):", texto_placa_raw)
                    if placa_recortada_cv is not None:
                        st.image(placa_recortada_cv, caption="Recorte analisado pelo PaddleOCR", use_column_width=True)
                    texto_placa_raw = re.sub(r'[^A-Za-z0-9]', '', texto_placa_raw.upper())
                    padrao_brasil = re.search(r'^[A-Z]{3}[0-9]{4}$', texto_placa_raw)
                    padrao_mercosul = re.search(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', texto_placa_raw)
                    if padrao_mercosul:
                        texto_placa = padrao_mercosul.group()
                    elif padrao_brasil:
                        texto_placa = padrao_brasil.group()
                    else:
                        texto_placa = texto_placa_raw or "Texto não extraído"
                    st.write("[DEBUG] Texto final extraído após limpeza rigorosa:", texto_placa)
                except Exception as e:
                    st.warning(f"Erro ao usar PaddleOCR como fallback: {e}")

            return imagem_original_cv, placa_recortada_cv, texto_placa, imagem_processada_cv, placa_recortada_processada_ocr_cv
        else:
            return imagem_original_cv, None, "Nenhuma placa encontrada após ajustes.", imagem_processada_cv, None

    except Exception as e:
        st.error(f"Erro durante o processamento da placa: {e}")
        return None, None, f"Erro: {e}", None, None

def mostrar_resultados_v2(img_original_pil, img_placa_recortada_pil, texto_extraido, img_processada_pipeline_pil, img_placa_recortada_processada_ocr_pil):
    st.subheader("🔍 Resultados do Processamento (Pipeline do Usuário)")

    col1, col2 = st.columns(2)
    with col1:
        st.write("[DEBUG] Exibindo imagem original/pre-processada/recortada.")
        if img_original_pil:
            st.image(img_original_pil, caption="Imagem Original Fornecida", use_container_width=True)
        else:
            st.warning("Imagem original não disponível.")

    with col2:
        if img_processada_pipeline_pil:
            st.image(img_processada_pipeline_pil, caption="Imagem Pré-Processada (p/ Contornos)", use_container_width=True)
        else:
            st.info("Imagem pré-processada não disponível.")

    st.markdown("---_---")
    col3, col4 = st.columns(2)
    with col3:
        if img_placa_recortada_pil:
            st.image(img_placa_recortada_pil, caption="Região da Placa Recortada (Original)", use_container_width=True)
        else:
            st.info("Nenhuma região de placa foi recortada ou retornada para exibição.")
    with col4:
        if img_placa_recortada_processada_ocr_pil:
            st.image(img_placa_recortada_processada_ocr_pil, caption="Região da Placa Processada (p/ OCR)", use_container_width=True)
        else:
            st.info("Nenhuma região de placa processada para OCR foi retornada.")

    st.subheader("📝 Texto Extraído da Placa:")
    st.write("[DEBUG] Texto final extraído:", texto_extraido)
    if texto_extraido and "Erro" not in texto_extraido and "Nenhuma placa" not in texto_extraido and "não conseguiu extrair" not in texto_extraido:
        st.success(f"**{texto_extraido}**")
    elif texto_extraido:
        st.warning(texto_extraido)
    else:
        st.error("Nenhum texto pôde ser extraído ou retornado.")

# --- Opções de Entrada --- #
st.sidebar.header("Opções de Imagem")
opcao_entrada = st.sidebar.radio(
    "Escolha a fonte da imagem:",
    ("Upload de Arquivo Local", "Capturar com a Câmera"),
    key="input_option_v2"
)

# --- Lógica Principal da Aplicação ---
if __name__ == '__main__':
    imagem_original_pil_para_exibir = None
    imagem_placa_recortada_pil = None
    texto_final = None
    imagem_processada_para_contornos_pil = None
    imagem_placa_recortada_processada_ocr_pil = None

    if opcao_entrada == "Upload de Arquivo Local":
        uploaded_file = st.sidebar.file_uploader("Escolha uma imagem de placa veicular...", type=["jpg", "jpeg", "png"], key="uploader_v2")
        if uploaded_file is not None:
            st.sidebar.success("Imagem carregada com sucesso!")
            imagem_original_pil_para_exibir = Image.open(uploaded_file)

            with st.spinner('Processando imagem com o pipeline fornecido... Por favor, aguarde.'):
                img_orig_cv, img_recortada_cv, texto, img_proc_cont_cv, img_rec_proc_ocr_cv = adaptar_e_processar_placa(uploaded_file)
                texto_final = texto
                if img_recortada_cv is not None:
                    imagem_placa_recortada_pil = Image.fromarray(cv2.cvtColor(img_recortada_cv, cv2.COLOR_BGR2RGB))
                if img_proc_cont_cv is not None:
                    imagem_processada_para_contornos_pil = Image.fromarray(cv2.cvtColor(img_proc_cont_cv, cv2.COLOR_BGR2RGB))
                if img_rec_proc_ocr_cv is not None:
                    imagem_placa_recortada_processada_ocr_pil = Image.fromarray(
                        cv2.cvtColor(img_rec_proc_ocr_cv, cv2.COLOR_BGR2RGB)
                    )

    elif opcao_entrada == "Capturar com a Câmera":
        st.sidebar.info("A funcionalidade de câmera pode solicitar permissão no seu navegador.")
        img_file_buffer = st.camera_input("Tire uma foto da placa veicular", key="camera_v2")

        if img_file_buffer is not None:
            st.sidebar.success("Foto capturada com sucesso!")
            imagem_original_pil_para_exibir = Image.open(img_file_buffer)

            with st.spinner('Processando imagem da câmera com o pipeline fornecido... Por favor, aguarde.'):
                img_orig_cv, img_recortada_cv, texto, img_proc_cont_cv, img_rec_proc_ocr_cv = adaptar_e_processar_placa(img_file_buffer)
                texto_final = texto
                if img_recortada_cv is not None:
                    imagem_placa_recortada_pil = Image.fromarray(cv2.cvtColor(img_recortada_cv, cv2.COLOR_BGR2RGB))
                if img_proc_cont_cv is not None:
                    imagem_processada_para_contornos_pil = Image.fromarray(cv2.cvtColor(img_proc_cont_cv, cv2.COLOR_BGR2RGB))
                if img_rec_proc_ocr_cv is not None:
                    imagem_placa_recortada_processada_ocr_pil = Image.fromarray(cv2.cvtColor(img_rec_proc_ocr_cv, cv2.COLOR_BGR2RGB))

    if imagem_original_pil_para_exibir:
        mostrar_resultados_v2(imagem_original_pil_para_exibir, imagem_placa_recortada_pil, texto_final, imagem_processada_para_contornos_pil, imagem_placa_recortada_processada_ocr_pil)
    else:
        st.info("Aguardando imagem para processamento. Use as opções na barra lateral.")

    st.markdown("---_---")
