# -*- coding: utf-8 -*-
"""Detecção de imagens com pessoas.ipynb

Automatically generated by Colaboratory.

"""

from google.colab import drive
drive.mount('/content/drive')

!ls drive/My\ Drive/People_Detection/dadosImagem

!ln -s drive/My\ Drive/People_Detection/dadosImagem /content/Aula

!ls Aula/Treinamento/positivos

import cv2

img_caminho = 'Aula/Treinamento/positivos/crop_000010.png'
img_teste = cv2.imread(img_caminho)

cv2.imshow('img',img_teste)

from google.colab.patches import cv2_imshow

cv2_imshow(img_teste)

print(type(img_teste)) #RGB - Red Green Blue
print(img_teste.shape)

import numpy as np

print(img_teste)

print("Minimo: ", np.min(img_teste))
print("Máximo: ", np.max(img_teste))

img_teste_cinza = cv2.cvtColor(img_teste, cv2.COLOR_RGB2GRAY)
cv2_imshow(img_teste_cinza)
print(img_teste_cinza.shape)

from matplotlib import pyplot as plt

print('Original: ', img_teste_cinza.shape)
img_redimensionada = cv2.resize(img_teste_cinza, (360,360), interpolation=cv2.INTER_CUBIC)
print('Redimensionada', img_redimensionada.shape)

plt.subplot(121)
plt.title('Original')
plt.imshow(img_teste_cinza, cmap='gray', interpolation='bicubic')
plt.subplot(122)
plt.title('Redimensionada')
plt.imshow(img_redimensionada, cmap='gray', interpolation='bicubic')
plt.show()

cv2_imshow(img_redimensionada)

histograma = cv2.calcHist([img_redimensionada], [0], None, [256], [0,256])
print(histograma.astype(np.int))

plt.plot(histograma)
plt.show()

img_teste_equalizada = cv2.equalizeHist(img_redimensionada)
histograma_equalizado = cv2.calcHist([img_teste_equalizada], [0], None, [256], [0,256])

plt.figure(figsize=(10,5))
plt.subplot(121)
plt.title('Inicial')
plt.plot(histograma)
plt.subplot(122)
plt.title('equalizado')
plt.plot(histograma_equalizado)

plt.figure(figsize = (10,10))
plt.subplot(121)
plt.imshow(img_redimensionada, cmap= 'gray', interpolation='bicubic')
plt.subplot(122)
plt.imshow(img_teste_equalizada, cmap= 'gray', interpolation='bicubic')
plt.show()

img_suavizada = cv2.GaussianBlur(img_teste_equalizada, (9,9), 1)

valor_retorno, img_binarizada = cv2.threshold(img_teste_equalizada, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
valor_retorno_otsu, img_binarizada_otsu = cv2.threshold(img_suavizada, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

plt.figure(figsize = (10,10))
plt.subplot(121)
plt.title('Binarizada - Equalizada')
plt.imshow(img_binarizada, cmap = 'gray', interpolation='bicubic')

plt.subplot(122)
plt.title('Binarizada - Suavizada')
plt.imshow(img_binarizada_otsu, cmap = 'gray', interpolation='bicubic')

plt.show()

print("Limiar escolhido: ", valor_retorno, "Limiar OTSU:", valor_retorno_otsu)

"""- algura e largura: Sepala e petala"""

print(img_suavizada.size)

img_canny = cv2.Canny(img_suavizada, 100, 255)
cv2_imshow(img_canny)

def get_descritores(img_caminho):
    
    LARGURA = 360
    ALTURA = 360
    
    # Ler a imgem
    img_teste = cv2.imread(img_caminho, 0)
    
    #Redimensionar
    img_redimensionada = cv2.resize(img_teste, (LARGURA, ALTURA), interpolation=cv2.INTER_CUBIC)
    
    # Remover ruídos
    img_equalizada = cv2.equalizeHist(img_redimensionada)
    img_suavizada = cv2.GaussianBlur(img_equalizada, (9,9), 1)
    
    #Detectar pontos chaves
    orb = cv2.ORB_create(nfeatures=512)
    pontos_chave = orb.detect(img_suavizada, None)
    
    pontos_chave, descritores = orb.compute(img_suavizada, pontos_chave)
    
    return descritores

"""- ORB - Oriented FAST and Ratated BRIEF

- SURF - Speeded up robust features

- SIFT - Scale-invariant feature transform
"""

descritor = get_descritores(img_caminho)

print("Tipo: ", type(descritor))
print("Formato descritor : ", descritor.shape)
print("\n descritor[0]: ", descritor[0])

img_pontos = cv2.drawKeypoints(img_suavizada, pontos_chave, outImage = np.array([]), flags=0)
cv2_imshow(img_pontos)

#Video 5.1
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import os

QUANTIDADE_PALAVRAS_VIRTUAIS = 512

class PacoteDePalavras:
    
    def gerar_dicionario(self, lista_descritores):
        kmeans = KMeans(n_clusters = QUANTIDADE_PALAVRAS_VIRTUAIS)
        kmenas = kmeans.fit(lista_descritores)
        self.dicionario = kmeans.cluster_centers_
        
    def histograma_de_frequencia(self, descritor):

        try:
            algoritmo_knn = NearestNeighbors(n_neighbors = 1)
            algoritmo_knn.fit(self.dicionario)
            mais_proximos = algoritmo_knn.kneighbors(descritor, return_distance = False).flatten()

            histograma_caracteristica = np.histogram(mais_proximos, bins=np.arange(self.dicionario.shape[0]+1))[0]
        
            return histograma_caracteristica
        except AttributeError:
            print("O atributo dicionario nao foi definido")

    def salvar_dicionario(self, caminho='', nome_dicionario = 'dicionario.csv'):
        try:
            np.savetxt(os.path.join(caminho, nome_dicionario), self.dicionario, delimiter=',', fmt='%f')
            print("Dicionario salvo")
            
        except AttributeError:
            print("Dicionario Vazio")
        
    def carregar_dicionario(self, caminho='', nome_dicionario = 'dicionario.csv'):
        
        self.dicionario = np.loadtxt(os.path.join(caminho,nome_dicionario), delimiter=',')

teste_palavras_virtuais = PacoteDePalavras()
teste_palavras_virtuais.gerar_dicionario(descritor)
histograma_caracteristica = teste_palavras_virtuais.histograma_de_frequencia(descritor)
print(histograma_caracteristica)

#Video 5.1 parte 4
DICIONARIO_NOME = 'dicionario.csv'
dados_treinamento = ['Aula/Treinamento/positivos/', 'Aula/Treinamento/negativos']

# Rotina para criação do dicionario de palavras virtuais

descritores = np.empty((0,32), dtype=np.uint8)

for caminho in dados_treinamento:

    for raiz,diretorios,arquivos in os.walk(caminho):
    
        for arquivo in arquivos:
            if arquivo.endswith('.png'):
                orb_descritor = get_descritores(os.path.join(caminho,arquivo))
                descritores = np.append(descritores, orb_descritor, axis=0)
                
img_representacao = PacoteDePalavras()
img_representacao.gerar_dicionario(descritores)
img_representacao.salvar_dicionario('Aula/', DICIONARIO_NOME)

#Inicio video 5.2
def salvar_descritor(descritor, caminho, nome_arquivo):
    descritor = descritor.reshape((1,descritor.size))
    arquivo = open(os.path.join(caminho, nome_arquivo), 'a')
    np.savetxt(arquivo, descritor, delimiter=',', fmt='%i')
    arquivo.close()

# computar descritores gerando histograma de cada imagem separadamente

NOME_DESCRITOR = 'orb_descritor.csv'

for caminho in dados_treinamento:
    
    for raiz, diretorios, arquivos in os.walk(caminho):
        
        for arquivo in arquivos:
            if arquivo.endswith('.png'):
                descritor = get_descritores(os.path.join(caminho, arquivo))
                histograma_descritor = img_representacao.histograma_de_frequencia(descritor)
                salvar_descritor(histograma_descritor, caminho, NOME_DESCRITOR)
                
print("extração de caracteriscas finalizada e descritores salvos!")

''' Inicio video 5.3 - Classificação Parte 1'''
def carregar_descritores(caminho, nome_arquivo='orb_descritor.csv'):
    descritores = np.loadtxt(os.path.join(caminho, nome_arquivo), delimiter=',')
    print('formato do array de descritores: ', descritores.shape)
    return descritores

# Carregar descritores salvos

descritores = np.empty((0,QUANTIDADE_PALAVRAS_VIRTUAIS))
for caminho in dados_treinamento:
    descritores = np.append(descritores, carregar_descritores(caminho, NOME_DESCRITOR), axis=0)

'''Inicio video 5.3 - Classificação Parte 2'''

from sklearn.neighbors import KNeighborsClassifier

# KNN para classificar as imagens

QUANTIDADE_DE_DADOS_TREINAMENTO = 400
QUANTIDADE_DE_DADOS_TESTE = 100

rotulos_treinamento = np.ones(QUANTIDADE_DE_DADOS_TREINAMENTO, dtype=np.uint8)
rotulos_treinamento = np.append(rotulos_treinamento,np.zeros(QUANTIDADE_DE_DADOS_TREINAMENTO, dtype=np.uint8))

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(descritores,rotulos_treinamento)

dados_teste = ['Aula/Teste/positivos/', 'Aula/Teste/negativos/']


img_teste_descritores = np.empty((0,QUANTIDADE_PALAVRAS_VIRTUAIS), dtype=np.uint8)

for caminho in dados_teste:
    for raiz,diretorios, arquivos in os.walk(caminho):
        for arquivo in arquivos:
            if arquivo.endswith('.png'):
                img_descritor = get_descritores(os.path.join(caminho,arquivo))
                img_descritor = img_representacao.histograma_de_frequencia(img_descritor)
                img_dim_expandida = np.expand_dims(img_descritor, axis=0)
                img_teste_descritores = np.append(img_teste_descritores, img_dim_expandida, axis=0)

rotulos_teste = np.concatenate((np.ones(QUANTIDADE_DE_DADOS_TESTE, dtype=np.uint8), np.zeros(QUANTIDADE_DE_DADOS_TESTE, dtype=np.uint8)))
print('Acurácia: ',knn.score(img_teste_descritores, rotulos_teste))

from sklearn.metrics import confusion_matrix

rotulos_previstos = knn.predict(img_teste_descritores)
matriz = confusion_matrix(rotulos_teste, rotulos_previstos)

plt.imshow(matriz, cmap=plt.cm.Blues, interpolation='nearest')
plt.title("Matriz de confusão")

labels = ['positivos', 'negativos']

marcador_escalas = range(len(labels))

plt.yticks(marcador_escalas, labels)
plt.xticks(marcador_escalas, labels)

for linha in range(matriz.shape[0]):
    for coluna in range(matriz.shape[1]):
        plt.text(coluna, linha, format(matriz[linha,coluna]), horizontalalignment='center', color='black')
plt.show()