import cv2
import os
import numpy as np
from PIL import Image

# Importar a função de processamento principal do app.py
# Certifique-se de que app.py e os módulos que ele importa (processar_imagem, etc.)
# estão no PYTHONPATH ou no mesmo diretório.
from app import adaptar_e_processar_placa 

# Diretórios
DIR_IMAGENS_USUARIO = "user_test_images"
DIR_RESULTADOS_TESTE_V2 = "test_results_v2"

# Certifique-se de que o diretório de resultados exista
if not os.path.exists(DIR_RESULTADOS_TESTE_V2):
    os.makedirs(DIR_RESULTADOS_TESTE_V2)

# Listar todas as imagens no diretório de teste do usuário e pegar as 5 primeiras
nome_arquivos_originais = sorted([f for f in os.listdir(DIR_IMAGENS_USUARIO) if os.path.isfile(os.path.join(DIR_IMAGENS_USUARIO, f)) and f.lower().endswith((".png", ".jpg", ".jpeg"))])
nome_arquivos_teste = nome_arquivos_originais[:5]

print(f"Encontradas {len(nome_arquivos_originais)} imagens na pasta do usuário. Testando com as 5 primeiras: {nome_arquivos_teste}")

resultados_documentacao_v2 = []

for i, nome_arquivo in enumerate(nome_arquivos_teste):
    caminho_imagem_original_teste = os.path.join(DIR_IMAGENS_USUARIO, nome_arquivo)
    print(f"\nProcessando imagem {i+1}/{len(nome_arquivos_teste)}: {nome_arquivo}")

    # Salvar uma cópia da imagem original no diretório de resultados para referência no relatório
    try:
        img_pil_original_copia = Image.open(caminho_imagem_original_teste)
        # Converter para PNG para consistência no relatório, se não for já
        nome_base_original_salvo = f"teste_v2_{i+1}_{os.path.splitext(nome_arquivo)[0]}_original.png"
        caminho_original_salvo_copia = os.path.join(DIR_RESULTADOS_TESTE_V2, nome_base_original_salvo)
        img_pil_original_copia.save(caminho_original_salvo_copia)
    except Exception as e_save_orig:
        print(f"  Erro ao salvar cópia da imagem original {nome_arquivo}: {e_save_orig}")
        caminho_original_salvo_copia = "N/A"

    # Chamar a função de processamento adaptada do app.py
    # Ela espera um caminho de arquivo ou bytes. Vamos passar o caminho.
    img_original_cv, placa_recortada_cv, texto_extraido, img_processada_contornos_cv, placa_recortada_processada_ocr_cv = adaptar_e_processar_placa(caminho_imagem_original_teste)

    print(f"  Texto extraído: {texto_extraido}")

    # Salvar imagens processadas retornadas pelo pipeline
    nome_base_resultado = f"teste_v2_{i+1}_{os.path.splitext(nome_arquivo)[0]}"
    
    caminho_img_proc_contornos = "N/A"
    if img_processada_contornos_cv is not None:
        try:
            caminho_img_proc_contornos = os.path.join(DIR_RESULTADOS_TESTE_V2, f"{nome_base_resultado}_proc_contornos.png")
            cv2.imwrite(caminho_img_proc_contornos, img_processada_contornos_cv)
            print(f"  Imagem pré-processada (contornos) salva em: {caminho_img_proc_contornos}")
        except Exception as e_save_proc_cont:
            print(f"  Erro ao salvar imagem pré-processada (contornos): {e_save_proc_cont}")
            caminho_img_proc_contornos = "Erro ao salvar"

    caminho_placa_recortada = "N/A"
    if placa_recortada_cv is not None:
        try:
            caminho_placa_recortada = os.path.join(DIR_RESULTADOS_TESTE_V2, f"{nome_base_resultado}_placa_recortada.png")
            cv2.imwrite(caminho_placa_recortada, placa_recortada_cv)
            print(f"  Placa recortada (original) salva em: {caminho_placa_recortada}")
        except Exception as e_save_recortada:
            print(f"  Erro ao salvar placa recortada: {e_save_recortada}")
            caminho_placa_recortada = "Erro ao salvar"

    caminho_placa_recortada_proc_ocr = "N/A"
    if placa_recortada_processada_ocr_cv is not None:
        try:
            caminho_placa_recortada_proc_ocr = os.path.join(DIR_RESULTADOS_TESTE_V2, f"{nome_base_resultado}_placa_rec_proc_ocr.png")
            cv2.imwrite(caminho_placa_recortada_proc_ocr, placa_recortada_processada_ocr_cv)
            print(f"  Placa recortada (processada p/ OCR) salva em: {caminho_placa_recortada_proc_ocr}")
        except Exception as e_save_rec_proc:
            print(f"  Erro ao salvar placa recortada processada p/ OCR: {e_save_rec_proc}")
            caminho_placa_recortada_proc_ocr = "Erro ao salvar"

    # Salvar texto extraído
    caminho_texto_extraido_salvo = os.path.join(DIR_RESULTADOS_TESTE_V2, f"{nome_base_resultado}_texto.txt")
    try:
        with open(caminho_texto_extraido_salvo, "w", encoding="utf-8") as f_text:
            f_text.write(f"Imagem Original Testada: {nome_arquivo}\n")
            f_text.write(f"Texto Extraído: {texto_extraido}\n")
        print(f"  Texto extraído salvo em: {caminho_texto_extraido_salvo}")
    except Exception as e_save_text:
        print(f"  Erro ao salvar texto extraído: {e_save_text}")
        caminho_texto_extraido_salvo = "Erro ao salvar"
    
    resultados_documentacao_v2.append({
        "original_filename_test": nome_arquivo,
        "original_saved_path_copy": caminho_original_salvo_copia,
        "img_proc_contornos_path": caminho_img_proc_contornos,
        "placa_recortada_path": caminho_placa_recortada,
        "placa_recortada_proc_ocr_path": caminho_placa_recortada_proc_ocr,
        "extracted_text": texto_extraido,
        "text_file_path": caminho_texto_extraido_salvo
    })

print("\n--- Resumo dos Resultados para Documentação (v2) ---")
for res in resultados_documentacao_v2:
    print(res)

# Salvar o resumo dos resultados em um arquivo markdown para facilitar a documentação
resumo_md_path_v2 = os.path.join(DIR_RESULTADOS_TESTE_V2, "resumo_testes_v2.md")
with open(resumo_md_path_v2, "w", encoding="utf-8") as f_md:
    f_md.write("# Relatório de Testes da Leitura de Placas (Pipeline do Usuário v2)\n\n")
    for i, res in enumerate(resultados_documentacao_v2):
        f_md.write(f"## Teste {i+1}: {res['original_filename_test']}\n\n")
        f_md.write(f"- Imagem Original Testada: `{os.path.join(DIR_IMAGENS_USUARIO, res['original_filename_test'])}`\n")
        if os.path.exists(res['original_saved_path_copy']):
            f_md.write(f"  (Cópia salva em: `{os.path.basename(res['original_saved_path_copy'])}`)\n")
            f_md.write(f"  <img src='{os.path.basename(res['original_saved_path_copy'])}' alt='Original: {res['original_filename_test']}' width='250'/>\n\n")
        else:
            f_md.write(f"  (Falha ao salvar cópia da imagem original)\n\n")

        if os.path.exists(res['img_proc_contornos_path']):
            f_md.write(f"- Imagem Pré-Processada (p/ Contornos): `{os.path.basename(res['img_proc_contornos_path'])}`\n")
            f_md.write(f"  <img src='{os.path.basename(res['img_proc_contornos_path'])}' alt='Pré-Processada Contornos: {res['original_filename_test']}' width='250'/>\n\n")
        else:
            f_md.write(f"- Imagem Pré-Processada (p/ Contornos): {res['img_proc_contornos_path']}\n\n")

        if os.path.exists(res['placa_recortada_path']):
            f_md.write(f"- Região da Placa Recortada (Original): `{os.path.basename(res['placa_recortada_path'])}`\n")
            f_md.write(f"  <img src='{os.path.basename(res['placa_recortada_path'])}' alt='Placa Recortada: {res['original_filename_test']}' width='200'/>\n\n")
        else:
            f_md.write(f"- Região da Placa Recortada (Original): {res['placa_recortada_path']}\n\n")

        if os.path.exists(res['placa_recortada_proc_ocr_path']):
            f_md.write(f"- Região da Placa Processada (p/ OCR): `{os.path.basename(res['placa_recortada_proc_ocr_path'])}`\n")
            f_md.write(f"  <img src='{os.path.basename(res['placa_recortada_proc_ocr_path'])}' alt='Placa Processada OCR: {res['original_filename_test']}' width='200'/>\n\n")
        else:
            f_md.write(f"- Região da Placa Processada (p/ OCR): {res['placa_recortada_proc_ocr_path']}\n\n")

        f_md.write(f"- Texto Extraído: **{res['extracted_text']}**\n")
        if os.path.exists(res['text_file_path']):
            f_md.write(f"  (Salvo em: `{os.path.basename(res['text_file_path'])}`)\n")
        f_md.write("---\n\n")

print(f"\nResumo dos testes (v2) salvo em: {resumo_md_path_v2}")
print("Script de teste (v2) concluído.")

