import numpy as np
import pandas as pd
from joblib import dump
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


def treinar(path, varObjetivo, varEntrada, splitTreino=0.8, otimizador="RMSprop", custo="mean_squared_logarithmic_error", iteracoes=350):
    # Carrega os dados de treino
    basePath = "/".join(path.split("/")[:-2])
    dados = pd.read_excel(path)

    # Define critério de limpeza da variável de controle
    primeiroQuartil = np.percentile(dados[varObjetivo].values, 25)
    terceiroQuartil = np.percentile(dados[varObjetivo].values, 75)
    passo = 1.5 * (terceiroQuartil - primeiroQuartil)

    df = []
    for i in range(0, len(dados)):
        consumo = dados[varObjetivo].values[i]
        if consumo > primeiroQuartil - passo and consumo < terceiroQuartil + passo:
            df.append(dados.values[i])
            
    dados = pd.DataFrame(df, columns=dados.columns)

    # Faz a limpeza das variáveis de entrada
    entrada = dados[varEntrada].values
    remove = IsolationForest(random_state=0).fit(entrada)
    out = remove.predict(entrada)

    df = []
    for i in range(0, len(out)):
        if out[i] == 1:
            df.append(dados.values[i])
            
    dados = pd.DataFrame(df, columns=dados.columns)

    # Separa o dataframe de teste e de treino
    iCorte = int(len(dados) * splitTreino)
    dfTreino = dados.loc[:iCorte, :]
    dfTeste = dados.loc[iCorte:, :]

    # Separa variáveis dependentes e independentes
    xTreino = dfTreino[varEntrada].values
    yTreino = dfTreino[varObjetivo].values

    xTeste = dfTeste[varEntrada].values
    yTeste = dfTeste[varObjetivo].values

    # Executa a padronização
    sc = StandardScaler()
    xTreino = sc.fit_transform(xTreino)
    xTeste = sc.transform(xTeste)

    # Cria a rede neural
    ann = Sequential()
    ann.add(Dense(100, activation="relu"))
    ann.add(Dense(100, activation="relu"))
    ann.add(Dense(100, activation="relu"))
    ann.add(Dense(1, activation="linear"))
        
    # Compila e treina
    ann.compile(optimizer=otimizador, loss=custo)
    hist = ann.fit(xTreino, yTreino, batch_size=32, epochs=iteracoes, verbose=0)
    finalLoss = hist.history["loss"][-1]

    # Calcula resíduos
    yPred = ann.predict(xTeste).reshape(1, -1)[0]
    residuos = []
    for i in range(0, len(yPred)):
        if yTeste[i] == 0:
            continue
            
        residuos.append((abs(yPred[i] - yTeste[i]) * 100 / yTeste[i]))

    # Calcula métricas
    erroMin = np.min(residuos)
    erroMax = np.max(residuos)
    erroMedio = np.mean(residuos)
    erro50 = np.quantile(residuos, 0.5)
    erro75 = np.quantile(residuos, 0.75)

    # Salva o modelo
    ann.save(f"{basePath}/models/ann.h5")
    dump(sc, f"{basePath}/models/scaler.joblib")

    return erroMin, erroMax, erroMedio, erro50, erro75