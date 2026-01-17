# Ortho Dataset Preparation for Object Detection

Scripts to prepare and organize datasets used for training YOLO object detection models on high-resolution orthophotos.

---

## 🇧🇷 Preparação do Dataset de Objetos das Ortofotos

Este repositório contém scripts para preparação e organização de datasets utilizados no treinamento de uma rede neural YOLO para detecção de objetos em ortofotos.


## 📝 Project Overview

This project prepares training datasets for YOLO object detection models by combining orthophotos
(TIF/TFW) with DXF annotations, generating cropped object images, reviewing layer alignment,
and applying data augmentation.

---

## 🇧🇷📝 Visão Geral do Projeto

Este projeto prepara datasets de treinamento para modelos YOLO ao integrar ortofotos (TIF/TFW)
com anotações DXF, gerando recortes de objetos, revisando alinhamento de layers e aplicando
técnicas de data augmentation.


## 📁 Estrutura do Repositório

```bash
/ortho-dataset-preparation
│── 1-Extract_Object/          # 🔹 Extrai imagens dos objetos de interesse a partir das ortofotos
│   ├── main.py                # Script principal para extração de objetos
│   ├── .env                   # Arquivo de configuração com caminho dos arquivos DXF, ortofotos e a saída
│── 2-Visualize_Object_Layer/  # 🔹 Visualiza e corrige os layers deslocados
│   ├── main.py                # Script principal para visualização e ajuste
│   ├── .env                   # Arquivo de configuração com caminho das imagens
│── 3-Data_Augmentation/       # 🔹 Aplica técnica de data augmentation
│   ├── main.py                # Script principal para aplicar data augmentation
│   ├── .env                   # Arquivo de configuração com caminho das imagens e caminho para salvar
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

### 🔹 Passo 3: Aplicação de Data Augmentation
- Diretório: 3-Data_Augmentation/
- Descrição: 
  - O script aplica algumas técnicas de data augmentation
  - Ele pega as imagens do dataset preparado e rotaciona em 90°, 180° e 270°
  - Recalcula as coordenadas dos layers para manter as marcações
- Objetivo: Aumentar a variedade de imagens no dataset

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
