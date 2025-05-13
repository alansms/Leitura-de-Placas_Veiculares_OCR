# Projeto: Leitura de Placas Veiculares com OCR e Interface Web (v2 - Base no Código do Usuário)

## ✅ Objetivo

Desenvolver um sistema em Python que utiliza o Tesseract OCR para extrair textos de placas veiculares a partir de imagens, com pré-processamento utilizando OpenCV, baseado no código e lógica fornecidos pelo usuário. O projeto incluirá uma interface interativa desenvolvida com Streamlit, permitindo a escolha de arquivos locais ou a captura da placa através da câmera do dispositivo. O sistema será preparado para publicação no Streamlit Cloud via GitHub.

## 🎯 Requisitos do Sistema (Conforme Definido)

1.  Utilizar o código Python fornecido pelo usuário como base para o processamento OCR (`processar_imagem.py`, `processar_contornos.py`, `aplicar_ocr.py`, `utils.py`, `main.py`).
2.  Instalação e configuração do Tesseract OCR.
3.  Instalação do OpenCV para pré-processamento das imagens.
4.  Desenvolvimento da interface web com Streamlit, com opções para:
    *   Upload de imagem local (formatos JPG, JPEG, PNG).
    *   Captura da placa veicular via webcam.
5.  Testes com 5 imagens distintas de placas de carro ou moto (utilizando as imagens da pasta `images` fornecida pelo usuário).
6.  Criação de um `README.md` completo com instruções de instalação, guia de uso, explicação do pré-processamento, relatório dos testes e instruções de deploy.
7.  Geração de novos arquivos de configuração (`requirements.txt`, `packages.txt`, `setup.sh`) para o deploy no Streamlit Cloud.

## 🛠️ Funcionalidades Implementadas

*   **Interface Web com Streamlit:** Interface moderna e clean para interação do usuário.
*   **Upload de Arquivo Local:** Permite ao usuário carregar imagens de placas veiculares (JPG, JPEG, PNG).
*   **Captura via Webcam:** Permite ao usuário capturar imagens de placas utilizando a câmera do dispositivo.
*   **Processamento de Imagem (Baseado no Código do Usuário):**
    *   Conversão da imagem para escala de cinza (`processar_imagem.py`).
    *   Aplicação de filtros (Bilateral) e limiarização adaptativa (`processar_imagem.py`).
    *   Detecção de contornos para identificar possíveis regiões de placa (`processar_contornos.py`).
    *   Filtragem de contornos baseada em critérios como proporção, área e formato (`processar_contornos.py`).
    *   Recorte e processamento adicional da região da placa identificada (`processar_contornos.py`).
*   **Extração de Texto com Tesseract OCR (Baseado no Código do Usuário):**
    *   Aplicação do OCR na região da placa processada (`aplicar_ocr.py`).
    *   Tentativas de reconhecimento em português e inglês.
    *   Lógica para identificar placas no modelo antigo e Mercosul usando expressões regulares (`aplicar_ocr.py`).
    *   Geração de possibilidades de correção para caracteres incertos (`aplicar_ocr.py` e `utils.py`).
*   **Exibição de Resultados:**
    *   Apresentação da imagem original fornecida.
    *   Apresentação da imagem pré-processada (usada para detecção de contornos).
    *   Apresentação da região da placa recortada (original).
    *   Apresentação da região da placa processada (enviada ao OCR).
    *   Exibição do texto extraído da placa em tempo real na interface Streamlit.
*   **Estrutura para Deploy:** Preparado para publicação no Streamlit Cloud com `requirements.txt`, `packages.txt`, e `setup.sh`.

## 📂 Estrutura do Projeto

```
/Leitura_Placas_Streamlit_v2/
├── app.py                     # Arquivo principal da aplicação Streamlit
├── processar_imagem.py        # Módulo do usuário para pré-processamento de imagem
├── processar_contornos.py     # Módulo do usuário para detecção de contornos da placa
├── aplicar_ocr.py             # Módulo do usuário para aplicação do OCR
├── utils.py                   # Módulo do usuário com funções utilitárias (parcialmente adaptado)
├── requirements.txt           # Dependências Python para pip
├── packages.txt               # Dependências do sistema para Streamlit Cloud (ex: Tesseract)
├── setup.sh                   # Script de configuração para o ambiente Streamlit Cloud
├── todo.md                    # Lista de tarefas do desenvolvimento (para referência interna)
├── run_tests_v2.py            # Script para executar os testes automatizados (usando a lógica do app.py)
├── CP03_NLP_OCR/              # Diretório com os arquivos originais do usuário (para referência)
│   └── CP03 - NLP - OCR/
│       ├── images/
│       │   ├── img1.png
│       │   └── ... (outras imagens de teste do usuário)
│       └── ... (outros arquivos do projeto original do usuário)
└── test_results_v2/           # Diretório com os resultados dos testes da v2
    ├── teste_v2_1_img1_original.png
    ├── teste_v2_1_img1_proc_contornos.png
    ├── teste_v2_1_img1_placa_recortada.png
    ├── teste_v2_1_img1_placa_rec_proc_ocr.png
    ├── teste_v2_1_img1_texto.txt
    ├── resumo_testes_v2.md    # Relatório de testes em Markdown
    └── ... (outros resultados de teste)
```

## ⚙️ Instruções de Instalação das Dependências

### 1. Tesseract OCR

**Para execução local (Linux - Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-por
```

Para outros sistemas operacionais, consulte a [documentação oficial do Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html). Certifique-se de que o Tesseract esteja no PATH do sistema.

**Para deploy no Streamlit Cloud:**

O Tesseract OCR e o pacote de idioma português (`tesseract-ocr-por`) são instalados automaticamente através do arquivo `packages.txt`.

### 2. Bibliotecas Python

As dependências Python são listadas no arquivo `requirements.txt`. Para instalá-las localmente, utilize o pip em um ambiente virtual de sua preferência:

```bash
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate    # No Windows

pip3 install -r requirements.txt
```

As principais bibliotecas incluem:
*   `streamlit`: Para a interface web.
*   `opencv-python`: Para processamento de imagem.
*   `pytesseract`: Para a interface Python com o Tesseract OCR.
*   `Pillow`: Para manipulação de imagens.
*   `numpy`: Para operações numéricas.
*   `matplotlib`: Embora não usado diretamente na interface Streamlit final, é uma dependência dos módulos originais do usuário.

## 🚀 Guia de Uso da Aplicação

### Execução Local

1.  Certifique-se de que todas as dependências (Tesseract e bibliotecas Python) estão instaladas e o Tesseract está no PATH do sistema.
2.  Navegue até o diretório raiz do projeto (onde `app.py` está localizado).
3.  Execute o seguinte comando no terminal (com seu ambiente virtual ativado, se estiver usando um):

    ```bash
    streamlit run app.py
    ```
4.  A aplicação será aberta automaticamente no seu navegador web padrão.

### Utilizando a Interface

1.  **Escolha a Fonte da Imagem:** Na barra lateral esquerda, selecione "Upload de Arquivo Local" ou "Capturar com a Câmera".
2.  **Upload de Arquivo Local:**
    *   Clique em "Escolha uma imagem de placa veicular...".
    *   Selecione um arquivo de imagem (formatos suportados: JPG, JPEG, PNG) do seu computador.
    *   Aguarde o processamento.
3.  **Capturar com a Câmera:**
    *   Clique no botão "Tire uma foto da placa veicular".
    *   Seu navegador pode solicitar permissão para usar a câmera. Conceda a permissão.
    *   Enquadre a placa e capture a imagem.
    *   Aguarde o processamento.
4.  **Resultados:**
    *   A imagem original fornecida será exibida.
    *   A imagem pré-processada (usada para detecção de contornos) será exibida.
    *   A região da placa recortada (original) será exibida, se detectada.
    *   A região da placa processada (enviada ao OCR) será exibida, se detectada.
    *   O texto extraído da placa será mostrado abaixo das imagens.

## 🖼️ Explicação do Fluxo de Pré-processamento e OCR (Baseado no Código do Usuário)

O sistema utiliza a lógica de processamento de imagem e OCR fornecida nos módulos Python do usuário. O fluxo principal é o seguinte:

1.  **Carregamento da Imagem:** A imagem é carregada via upload ou captura da webcam e convertida para o formato OpenCV.

2.  **Pré-processamento da Imagem (`processar_imagem.py`):**
    *   **Conversão para Escala de Cinza:** A imagem é convertida para tons de cinza.
        ```python
        imagem_cinza = cv2.cvtColor(imagem_placa, cv2.COLOR_BGR2GRAY)
        ```
    *   **Filtragem de Ruído:** Um filtro bilateral é aplicado para suavizar a imagem e reduzir ruídos, preservando as bordas.
        ```python
        imagem_cinza = cv2.bilateralFilter(imagem_cinza, 9, 75, 75)
        ```
    *   **Limiarização Adaptativa:** Para destacar os caracteres, é aplicada uma limiarização adaptativa gaussiana.
        ```python
        imagem_limiarizada = cv2.adaptiveThreshold(
            imagem_cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ```
    Esta `imagem_limiarizada` é usada para a detecção de contornos.

3.  **Detecção de Contornos e Identificação de Placas (`processar_contornos.py`):**
    *   **Encontrar Contornos:** Contornos são detectados na `imagem_limiarizada` (resultado do `processar_imagem.py`).
        ```python
        contornos, _ = cv2.findContours(imagem_processada, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        ```
    *   **Filtragem de Contornos:** Cada contorno é analisado:
        *   Aproximação poligonal para verificar se é uma forma retangular (4 a 10 vértices no código original).
        *   Filtros de proporção (altura vs. largura) e área são aplicados para selecionar candidatos a placa.
    *   **Recorte e Processamento Adicional da Placa:** Para cada contorno candidato:
        *   A região correspondente é recortada da imagem original (`imagem_recortada`).
        *   Esta `imagem_recortada` é convertida para tons de cinza e uma nova limiarização (Otsu) é aplicada.
        *   Operações morfológicas (fechamento, abertura, dilatação, erosão) são aplicadas para refinar a imagem da placa para o OCR (`imagem_recortada_processada`).
    *   A função retorna uma lista de tuplas `(imagem_recortada, imagem_recortada_processada)` para as placas potenciais.

4.  **Aplicação do OCR (`aplicar_ocr.py`):**
    *   Itera sobre as placas potenciais fornecidas pelo `processar_contornos.py`.
    *   **Ajuste de Recorte (Modelo Antigo):** Se a altura da `imagem_recortada_processada` for maior que 120 pixels, um recorte adicional é feito para remover possíveis bordas superiores/inferiores.
    *   **Tesseract OCR:** O Pytesseract é usado para extrair texto da `imagem_recortada_processada`.
        *   Tentativa com idioma português (`lang='por'`).
        *   Configurações: `-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6 --oem 3`.
    *   **Validação do Padrão da Placa:** O texto extraído é verificado contra padrões de placas (modelo antigo e Mercosul) usando expressões regulares.
    *   **Tentativa com Idioma Inglês:** Se não houver sucesso com português, o OCR é tentado com `lang='eng'`.
    *   **Geração de Possibilidades:** Se a placa não for claramente identificada, o código tenta gerar possibilidades de correção para os últimos 4 caracteres, utilizando um dicionário de substituições comuns (letra por número) presente em `utils.py`.
    *   A função retorna o texto da primeira placa validada, a `imagem_recortada` original e a `imagem_recortada_processada` que foi usada no OCR.

5.  **Exibição dos Resultados (em `app.py`):**
    *   A imagem original, a imagem pré-processada para contornos, a região da placa recortada (original) e a região da placa processada para OCR são exibidas usando `st.image`.
    *   O texto extraído é exibido usando `st.success`, `st.warning` ou `st.error` dependendo do resultado.

## 🧪 Relatório dos Resultados dos Testes (Pipeline do Usuário v2)

Foram realizados testes com 5 imagens distintas da pasta `images/` fornecida no arquivo zip do usuário. Os resultados detalhados, incluindo as imagens originais, imagens processadas e o texto extraído, estão documentados abaixo. As imagens referenciadas estão no diretório `test_results_v2/`.

# Relatório de Testes da Leitura de Placas (Pipeline do Usuário v2)

## Teste 1: img1.png

- Imagem Original Testada: `CP03_NLP_OCR/CP03 - NLP - OCR/images/img1.png`
  (Cópia salva em: `test_results_v2/teste_v2_1_img1_original.png`)
  <img src='test_results_v2/teste_v2_1_img1_original.png' alt='Original: img1.png' width='250'/>

- Imagem Pré-Processada (p/ Contornos): `test_results_v2/teste_v2_1_img1_proc_contornos.png`
  <img src='test_results_v2/teste_v2_1_img1_proc_contornos.png' alt='Pré-Processada Contornos: img1.png' width='250'/>

- Região da Placa Recortada (Original): `test_results_v2/teste_v2_1_img1_placa_recortada.png`
  <img src='test_results_v2/teste_v2_1_img1_placa_recortada.png' alt='Placa Recortada: img1.png' width='200'/>

- Região da Placa Processada (p/ OCR): `test_results_v2/teste_v2_1_img1_placa_rec_proc_ocr.png`
  <img src='test_results_v2/teste_v2_1_img1_placa_rec_proc_ocr.png' alt='Placa Processada OCR: img1.png' width='200'/>

- Texto Extraído: **DIC6B71**
  (Salvo em: `test_results_v2/teste_v2_1_img1_texto.txt`)
---

## Teste 2: img2.png

- Imagem Original Testada: `CP03_NLP_OCR/CP03 - NLP - OCR/images/img2.png`
  (Cópia salva em: `test_results_v2/teste_v2_2_img2_original.png`)
  <img src='test_results_v2/teste_v2_2_img2_original.png' alt='Original: img2.png' width='250'/>

- Imagem Pré-Processada (p/ Contornos): `test_results_v2/teste_v2_2_img2_proc_contornos.png`
  <img src='test_results_v2/teste_v2_2_img2_proc_contornos.png' alt='Pré-Processada Contornos: img2.png' width='250'/>

- Região da Placa Recortada (Original): `test_results_v2/teste_v2_2_img2_placa_recortada.png`
  <img src='test_results_v2/teste_v2_2_img2_placa_recortada.png' alt='Placa Recortada: img2.png' width='200'/>

- Região da Placa Processada (p/ OCR): `test_results_v2/teste_v2_2_img2_placa_rec_proc_ocr.png`
  <img src='test_results_v2/teste_v2_2_img2_placa_rec_proc_ocr.png' alt='Placa Processada OCR: img2.png' width='200'/>

- Texto Extraído: **FJQ1896

Mercosul:
FJQL896
FJQ1E96
**
  (Salvo em: `test_results_v2/teste_v2_2_img2_texto.txt`)
---

## Teste 3: img3.png

- Imagem Original Testada: `CP03_NLP_OCR/CP03 - NLP - OCR/images/img3.png`
  (Cópia salva em: `test_results_v2/teste_v2_3_img3_original.png`)
  <img src='test_results_v2/teste_v2_3_img3_original.png' alt='Original: img3.png' width='250'/>

- Imagem Pré-Processada (p/ Contornos): N/A

- Região da Placa Recortada (Original): N/A

- Região da Placa Processada (p/ OCR): N/A

- Texto Extraído: **Nenhuma placa potencial encontrada pelos contornos.**
  (Salvo em: `test_results_v2/teste_v2_3_img3_texto.txt`)
---

## Teste 4: img4.png

- Imagem Original Testada: `CP03_NLP_OCR/CP03 - NLP - OCR/images/img4.png`
  (Cópia salva em: `test_results_v2/teste_v2_4_img4_original.png`)
  <img src='test_results_v2/teste_v2_4_img4_original.png' alt='Original: img4.png' width='250'/>

- Imagem Pré-Processada (p/ Contornos): `test_results_v2/teste_v2_4_img4_proc_contornos.png`
  <img src='test_results_v2/teste_v2_4_img4_proc_contornos.png' alt='Pré-Processada Contornos: img4.png' width='250'/>

- Região da Placa Recortada (Original): `test_results_v2/teste_v2_4_img4_placa_recortada.png`
  <img src='test_results_v2/teste_v2_4_img4_placa_recortada.png' alt='Placa Recortada: img4.png' width='200'/>

- Região da Placa Processada (p/ OCR): `test_results_v2/teste_v2_4_img4_placa_rec_proc_ocr.png`
  <img src='test_results_v2/teste_v2_4_img4_placa_rec_proc_ocr.png' alt='Placa Processada OCR: img4.png' width='200'/>

- Texto Extraído: **LLW1168

Mercosul:
LLWL168
LLW1I68
LLW116B
**
  (Salvo em: `test_results_v2/teste_v2_4_img4_texto.txt`)
---

## Teste 5: img5.png

- Imagem Original Testada: `CP03_NLP_OCR/CP03 - NLP - OCR/images/img5.png`
  (Cópia salva em: `test_results_v2/teste_v2_5_img5_original.png`)
  <img src='test_results_v2/teste_v2_5_img5_original.png' alt='Original: img5.png' width='250'/>

- Imagem Pré-Processada (p/ Contornos): `test_results_v2/teste_v2_5_img5_proc_contornos.png`
  <img src='test_results_v2/teste_v2_5_img5_proc_contornos.png' alt='Pré-Processada Contornos: img5.png' width='250'/>

- Região da Placa Recortada (Original): `test_results_v2/teste_v2_5_img5_placa_recortada.png`
  <img src='test_results_v2/teste_v2_5_img5_placa_recortada.png' alt='Placa Recortada: img5.png' width='200'/>

- Região da Placa Processada (p/ OCR): `test_results_v2/teste_v2_5_img5_placa_rec_proc_ocr.png`
  <img src='test_results_v2/teste_v2_5_img5_placa_rec_proc_ocr.png' alt='Placa Processada OCR: img5.png' width='200'/>

- Texto Extraído: **DRJ5E67**
  (Salvo em: `test_results_v2/teste_v2_5_img5_texto.txt`)
---

## ☁️ Instruções para Deploy no Streamlit Cloud via GitHub

Para publicar esta aplicação no Streamlit Cloud, siga os passos:

1.  **Crie um Repositório no GitHub:**
    *   Envie todos os arquivos do projeto para um novo repositório no GitHub. Os arquivos essenciais são:
        *   `app.py`
        *   `processar_imagem.py`
        *   `processar_contornos.py`
        *   `aplicar_ocr.py`
        *   `utils.py`
        *   `requirements.txt`
        *   `packages.txt` (para dependências do sistema como Tesseract)
        *   `setup.sh` (para comandos de configuração adicionais, se houver)
    *   Você pode incluir a pasta `test_results_v2/` com as imagens de exemplo dos testes se desejar que elas façam parte do repositório e sejam referenciadas corretamente no `README.md`.

2.  **Conecte sua Conta Streamlit Cloud ao GitHub:**
    *   Acesse [share.streamlit.io](https://share.streamlit.io/).
    *   Faça login com sua conta GitHub.

3.  **Faça o Deploy da Aplicação:**
    *   Clique em "New app".
    *   Selecione o repositório GitHub que você criou.
    *   Selecione o branch apropriado (geralmente `main` ou `master`).
    *   Verifique se o arquivo principal da aplicação (`app.py`) está corretamente identificado.
    *   Clique em "Deploy!".

4.  **Acompanhe o Build:**
    *   O Streamlit Cloud irá construir o ambiente, instalando as dependências listadas em `requirements.txt` e `packages.txt`, e executando o `setup.sh`.
    *   Você pode acompanhar os logs do build na interface do Streamlit Cloud.

5.  **Acesso à Aplicação:**
    *   Após o deploy bem-sucedido, sua aplicação estará disponível publicamente em uma URL fornecida pelo Streamlit Cloud.

---
Desenvolvido por Manus IA (utilizando pipeline de OCR fornecido pelo usuário)

