# Canon T5i Webcam

Transforma uma **Canon EOS Rebel T5i / 700D** em uma webcam virtual com alta qualidade,
incluindo remoção de HUD (ícones da câmera, ISO, velocidade etc.) em tempo real.

Utiliza dois caminhos de captura:

- **EDSDK (Canon EOS Utility)** — Live View nativo da câmera pela API oficial da Canon.
- **OpenCV / DirectShow (EOS Webcam Utility)** — captura via driver de webcam da Canon.

O processamento remove o HUD, permite recorte (crop), e o resultado pode ser enviado
para uma **webcam virtual** (OBS Virtual Camera) para uso em chamadas de vídeo,
streaming e gravações.

---

## Funcionalidades

- **Captura ao vivo** da Canon T5i (via EDSDK Live View ou EOS Webcam Utility).
- **Remoção de HUD** em tempo real (borra ou remove ISO, velocidade, ícones de foco etc.).
- **Detecção automática** das regiões de HUD na imagem.
- **Crop manual** (recorte X, Y, W, H).
- **Saída para webcam virtual** (OBS Virtual Camera).
- **Painel de controle da câmera** (ISO, velocidade, abertura, foco).
- **Interface gráfica** (Tkinter) e **CLI** de processamento standalone.

---

## Requisitos

| Software | Versão mínima |
|---|---|
| Python | 3.10+ (testado com 3.12) |
| Windows | 10/11 (uso de ctypes/`WinDLL`) |

> **Atenção:** o uso do EDSDK é específico do Windows. O projeto foi testado no Windows.

### Dependências Python

- `opencv-python >= 4.8.0`
- `pyvirtualcam >= 0.4.0`
- `numpy >= 1.24.0`
- `Pillow >= 10.0.0`

### Software externo (opcional)

- **Canon EOS Utility / EDSDK** — para captura via Live View (EDSDK). O
  `EDSDK.dll` procura em vários locais, incluindo `Program Files\Canon\...`.
- **OBS Virtual Camera** — necessária para a saída como webcam virtual
  (`pyvirtualcam`). Instale o [OBS Studio](https://obsproject.com/) e ative a
  "Virtual Camera".

- **Canon EOS Webcam Utility** — driver que expõe a T5i como webcam via DirectShow
  (caminho OpenCV). Baixe no site oficial da Canon.

---

## Estrutura do projeto

```
canon-webcam/
├── main.py                     # Entry point da GUI (adiciona src/ ao path)
├── setup.bat                   # Instalador das dependências (Windows)
├── requirements.txt            # Dependências pip
├── libs/                       # EDSDK.dll / EdsImage.dll (se presentes)
├── src/canon_webcam/           # Pacote principal
│   ├── __main__.py             # Suporte a `python -m canon_webcam`
│   ├── cli.py                  # CLI standalone de processamento
│   ├── sdk/                    # Wrapper ctypes do EDSDK (loader, constants, errors)
│   ├── domain/                 # Modelos de domínio (devices, settings)
│   ├── capture/                # Fontes de captura (edsdk, opencv, factory)
│   ├── processing/             # HUD removal
│   ├── output/                 # Saídas (virtual cam)
│   ├── services/               # Scanner, pipeline, controle de câmera
│   └── ui/                     # Interface Tkinter (app, panels)
└── tests/                      # Testes de unidade
```

---

## Instalação

### 1. Instalar Python

Baixe o Python 3.10+ em <https://www.python.org/downloads/> e, durante a
instalação, marque **"Add Python to PATH"**.

### 2. Clonar o repositório

```bat
git clone <URL-do-repositorio>
cd canon-webcam
```

### 3. Instalar dependências

**Opção A — executar o script de setup (Windows):**

```bat
setup.bat
```

**Opção B — manualmente:**

```bat
pip install -r requirements.txt
```

### 4. EDSDK.dll

O programa procura a `EDSDK.dll` automaticamente. Se ela não existir em
`libs/`, tente copiar de uma instalação do **Canon EOS Utility**:

```text
C:\Program Files\Canon\EOS Utility\bin\EDSDK.dll
```

para:

```text
libs\EDSDK.dll
```

> Sem a DLL, a captura via EDSDK não estará disponível (o modo OpenCV / Webcam
> Utility continua funcionando).

---

## Como usar

### Interface gráfica (modo recomendado)

```bat
python main.py
```

1. Clique em **Scan Devices** para listar as câmeras encontradas.
2. Selecione o dispositivo (Canon via EDSDK ou OpenCV) e clique em **Start**.
3. Ajuste a remoção de HUD (blur, auto-detect, crop) conforme necessário.
4. Em **Virtual Webcam Output**, clique em **Start Virtual Cam** para enviar o
   resultado para o OBS Virtual Camera.
5. No aplicativo de vídeo (Zoom, Teams, OBS...), selecione a câmera virtual da OBS.

### Linha de comando (CLI)

Processa a webcam ou um arquivo de vídeo sem abrir a GUI:

```bat
:: Webcam (índice 0) com saída para virtual cam
python -m canon_webcam.cli --source 0 --virtual

:: Arquivo de vídeo -> arquivo processado
python -m canon_webcam.cli --source video.mp4 --output saida.mp4
```

Argumentos:

| Argumento | Descrição |
|---|---|
| `--source` | Índice da webcam (`0`) ou caminho de arquivo de vídeo |
| `--output` | Caminho do arquivo de saída (para processamento de arquivo) |
| `--virtual` | Também envia o resultado para a webcam virtual |

Atalhos na janela de preview da CLI:

- `q` — sair.
- `h` — ligar/desligar o blur de HUD.
- `c` — ligar/desligar o crop.
- `a` — auto-detetar as regiões de HUD.

---

## Configurações da câmera (EDSDK)

O painel **Camera Controls** permite ajustar, quando conectado via EDSDK:

- **ISO** — sensibilidade.
- **Velocidade (TV)** — tempo de exposição.
- **Abertura (AV)** — diafragma.
- **Foco** — Auto / Near / Far.

Esses controles só aparecem quando a câmera está conectada pela API EDSDK
(Live View). No modo OpenCV (Webcam Utility) eles não se aplicam.

---

## Estrutura de pastas de captura

| Pasta | Conteúdo |
|---|---|
| `libs/` | DLLs do EDSDK (EDSDK.dll, EdsImage.dll). |
| `src/canon_webcam/sdk/` | Wrapper ctypes do EDSDK. |
| `src/canon_webcam/capture/` | Fontes de captura: `edsdk_source`, `opencv_source`, `factory`. |
| `src/canon_webcam/processing/` | `hud_remover` (remov/add de HUD, crop, blur). |
| `src/canon_webcam/output/` | `virtual_cam` (saída via pyvirtualcam). |
| `src/canon_webcam/services/` | `scanner`, `pipeline`, `camera_control`. |
| `src/canon_webcam/ui/` | Interface Tkinter. |
| `tests/` | Testes de unidade. |

---

## Testes

Execute a suíte de testes de unidade:

```bat
python -m unittest discover -s tests -t .
```

---

## Solução de problemas

**"EDSDK.dll não encontrada" (caminho EDSDK)**
Instale o Canon EOS Utility e copie a DLL para `libs/` (veja a seção Instalação).

**Erro de permissão ao abrir sessão EDSDK (`0x00000002`)**
A câmera já está sendo usada por outro programa (ex.: Canon EOS Webcam Utility
ou EOS Utility). Feche o outro programa e tente novamente.

**Virtual camera não disponível**
Nenhum driver de virtual camera instalado. Instale o OBS Studio e inicie a
"Virtual Camera" antes de usar. Cheque também se `pyvirtualcam` está instalado.

**Nenhum frame no modo OpenCV**
A EOS Webcam Utility pode estar segurando a câmera; feche-a e use o modo EDSDK,
ou reinicie o serviço.

---

## Licença

Este projeto é um utilitário pessoal. O SDK da Canon (EDSDK) e a EOS Webcam
Utility são de propriedade da Canon Inc. e estão sujeitos aos termos de uso da
Canon. Consulte a documentação da Canon para uso comercial ou redistribuição.
