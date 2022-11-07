import streamlit as st 
import pandas as pd
import numpy as np
import random
import time
#import seaborn as sns
#import matplotlib.pyplot as plt
from scipy.stats import poisson

dados_variaveis = pd.read_excel('dados_previsao_esportiva.xlsx', sheet_name ='grupos')
fifa = dados_variaveis['Ranking Point']
fifa.index = dados_variaveis['Seleção']

a, b = min(fifa), max(fifa) 
fa, fb = 0.2, 1 
b1 = (fb - fa)/(b-a) 
b0 = fb - b*b1
fatorRanking = b0 + b1*fifa

fatorRanking.sort_values(ascending = False)

k = 0.1
fatorMercado = k*dados_variaveis['Market Value']/max(dados_variaveis['Market Value']) + (1 - k)
fatorConf = k*dados_variaveis['Factor_COF']/max(dados_variaveis['Factor_COF']) + (1 - k)
fatorCopa = k*dados_variaveis['Copas']/max(dados_variaveis['Copas']) + (1 - k)
fatorMercado.index = dados_variaveis['Seleção']
fatorConf.index = dados_variaveis['Seleção']
fatorCopa.index = dados_variaveis['Seleção']

forca = fatorRanking * fatorMercado * fatorConf * fatorCopa
forca.sort_values(ascending = False)

lista07 = ['0', '1', '2', '3', '4', '5', '6', '7+']

def Resultado(gols1, gols2):
	if gols1 > gols2:
		res = 'V'
	if gols1 < gols2:
		res = 'D' 
	if gols1 == gols2:
		res = 'E'       
	return res

def MediasPoisson(sele1, sele2):
	forca1 = forca[sele1]
	forca2 = forca[sele2]
	fator = forca1/(forca1 + forca2)
	mgols = 2.5
	l1 = mgols*fator
	l2 = mgols - l1
	return [fator, l1, l2]
	
def Distribuicao(media, tamanho = 7):
	probs = []
	for i in range(tamanho):
		probs.append(poisson.pmf(i,media))
	probs.append(1-sum(probs))
	return pd.Series(probs, index = lista07)

def ProbabilidadesPartida(sele1, sele2):
	fator, l1, l2 = MediasPoisson(sele1, sele2)
	d1, d2 = Distribuicao(l1), Distribuicao(l2)  
	matriz = np.outer(d1, d2)    #   Monta a matriz de probabilidades

	vitoria = np.tril(matriz).sum()-np.trace(matriz)    #Soma a triangulo inferior
	derrota = np.triu(matriz).sum()-np.trace(matriz)    #Soma a triangulo superior
	probs = np.around([vitoria, 1-(vitoria+derrota), derrota], 3)
	probsp = [f'{100*i:.1f}%' for i in probs]

	nomes = ['0', '1', '2', '3', '4', '5', '6', '7+']
	matriz = pd.DataFrame(matriz, columns = nomes, index = nomes)
	matriz.index = pd.MultiIndex.from_product([[sele1], matriz.index])
	matriz.columns = pd.MultiIndex.from_product([[sele2], matriz.columns]) 
	output = {'seleção1': sele1, 'seleção2': sele2, 
			 'f1': forca[sele1], 'f2': forca[sele2], 'fator': fator, 
			 'media1': l1, 'media2': l2, 
			 'probabilidades': probsp, 'matriz': matriz}
	return output

def Pontos(gols1, gols2):
	rst = Resultado(gols1, gols2)
	if rst == 'V':
		pontos1, pontos2 = 3, 0
	if rst == 'E':
		pontos1, pontos2 = 1, 1
	if rst == 'D':
		pontos1, pontos2 = 0, 3
	return pontos1, pontos2, rst


def Jogo(sele1, sele2):
	fator, l1, l2 = MediasPoisson(sele1, sele2)
	gols1 = int(np.random.poisson(lam = l1, size = 1))
	gols2 = int(np.random.poisson(lam = l2, size = 1))
	saldo1 = gols1 - gols2
	saldo2 = -saldo1
	pontos1, pontos2, result = Pontos(gols1, gols2)
	placar = '{}x{}'.format(gols1, gols2)
	return [gols1, gols2, saldo1, saldo2, pontos1, pontos2, result, placar]


listaselecoes = dados_variaveis['Seleção'].tolist()


######## COMEÇO DO APP
a1, a2 = st.columns([1,4])
a1.image('previsaoesportivalogo.png', width = 200)
a2.markdown("<h2 style='text-align: right; color: #5C061E; font-size: 32px;'>Copa do Mundo Qatar 2022 🏆  </h1>", unsafe_allow_html=True)
st.markdown('---')
st.markdown("<h2 style='text-align: center; color: #0f54c9; font-size: 40px;'>Probabilidades dos Jogos ⚽<br>  </h1>", unsafe_allow_html=True)

st.markdown('---')
j1, j2 = st.columns (2)
selecao1 = j1.selectbox('--- Escolha a primeira Seleção ---', listaselecoes) 
selecao2 = j2.selectbox('--- Escolha a segunda Seleção ---', listaselecoes, index = 1)
 
st.markdown('---')
 
if True:

	jogo = ProbabilidadesPartida(selecao1, selecao2)
	prob = jogo['probabilidades']
	matriz = jogo['matriz']
 
	col1, col2, col3, col4, col5 = st.columns(5)
	col1.image(dados_variaveis[dados_variaveis['Seleção'] == selecao1]['LinkBandeira2'].iloc[0]) 
	col2.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao1}<br>  </h1>", unsafe_allow_html=True)
	col2.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{prob[0]}<br>  </h1>", unsafe_allow_html=True)
	col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b; font-weight: 100; font-size: 15px;'>Empate<br>  </h1>", unsafe_allow_html=True)
	col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b;                    font-size: 30px;'>{prob[1]}<br>  </h1>", unsafe_allow_html=True)
	col4.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao2}<br>  </h1>", unsafe_allow_html=True) 
	col4.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{prob[2]}<br>  </h1>", unsafe_allow_html=True) 
	col5.image(dados_variaveis[dados_variaveis['Seleção'] == selecao2]['LinkBandeira2'].iloc[0])

	st.markdown('---')
 


	def aux(x):
		return f'{str(round(100*x,2))}%'

	st.table(matriz.applymap(aux))
 
	
	st.markdown('---')

	placar = np.unravel_index(np.argmax(matriz, axis=None), matriz.shape) 

	st.markdown("<h2 style='text-align: center; color: #0f54c9; font-size: 40px;'> Placar Mais Provável ⚽<br>  </h1>", unsafe_allow_html=True)
	
	st.markdown(' ')

	col1, col2, col3 = st.columns([1,5,1])
	col1.image(dados_variaveis[dados_variaveis['Seleção'] == selecao1]['LinkBandeira2'].iloc[0]) 
	#col2.header(selecao1) 
	col2.markdown(f"<h2 style='text-align: center; color: #1a1a1a; font-size: 40px;'>{selecao1} {placar[0]}x{placar[1]} {selecao2}<br>  </h1>", unsafe_allow_html=True)
	#col4.header(selecao2)
	col3.image(dados_variaveis[dados_variaveis['Seleção'] == selecao2]['LinkBandeira2'].iloc[0]) 



	st.markdown('---')

	st.markdown('Trabalho desenvolvido pela Equipe Previsão Esportiva - acesse www.previsaoesportiva.com.br 🔗')

	#bandeira1, nome1, prob, empate, prob, nome2, bandeira2
	#matriz de probabilidades do jogo
	#placar mais provável