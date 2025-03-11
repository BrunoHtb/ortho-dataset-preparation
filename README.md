# 📌 Preparação do Dataset de Objetos das Ortofotos

## 📝 Descrição
Este repositório contém scripts para preparação e organização de datasets utilizados no treinamento de uma rede neural YOLO para detecção de objetos em ortofotos.

O objetivo principal é extrair, visualizar e corrigir objetos de interesse a partir de ortofotos e arquivos DXF, garantindo um dataset bem anotado e de alta qualidade.
___________________________________________________________________________________________________________________________________________

## 📁 Estrutura do Repositório

```bash
/ortho-dataset-preparation
│── 1-Extract_Object/          # 🔹 Extrai imagens dos objetos de interesse a partir das ortofotos
│   ├── main.py                # Script principal para extração de objetos
│   ├── .env                   # Arquivo de configuração com caminho dos arquivos DXF, ortofotos e a saída
│── 2-Visualize_Object_Layer/  # 🔹 Visualiza e corrige os layers deslocados
│   ├── main.py                # Script principal para visualização e ajuste
│   ├── .env                   # Arquivo de configuração com caminho das imagens
│── README.md                  # 🔹 Documentação do projeto
│── requirements.txt           # 🔹 Dependências do projeto
│── .gitignore                 # 🔹 Arquivos a serem ignorados pelo Git
```

## 🚀 Fluxo de Trabalho
### 🔹 Passo 1: Extração dos Objetos
- Diretório: 1-Extract_Object/
- Descrição:
  - O script associa arquivos .tif e .tfw que contêm informações de georreferenciamento.
  - Em seguida, vincula essas informações ao arquivo .dxf, que contém as marcações feitas pelos restituidores.
  - Por fim, extrai imagens contendo apenas os objetos de interesse, juntamente com suas coordenadas. 
- Objetivo: Criar imagens segmentadas para uso no treinamento da rede YOLO.

### 🔹 Passo 2: Visualização e Correção de Layers
- Diretório: 2-Visualize_Object_Layer/
- Descrição: 
  - O script permite visualizar e corrigir layers deslocados,
  - Verificar se os objetos são visíveis na ortofoto,
  - Criar novos layers caso necessário,
  - Excluir layers ou imagens inválidas.
- Objetivo: Garantir a qualidade das anotações no dataset antes do treinamento.

## 📦 Instalação
### 1️⃣ Crie um ambiente virtual e ative
```bash
python -m venv venv
venv\Scripts\activate
```

### 2️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração
- Os arquivos TIF, TFW e DXF devem ter o mesmo nome para que sejam corretamente associados.
- Os diretórios de entrada e saída são configuráveis via arquivos .env presentes em cada diretório.
