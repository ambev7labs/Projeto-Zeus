import numpy as np
from joblib import load
from tensorflow.keras.models import load_model


def prever(basePath: str, entrada: list):
    # Carrega os modelos
    ann = load_model(f"{basePath}/models/ann.h5")
    sc = load(f"{basePath}/models/scaler.joblib")
    
    # Executa a previsão
    entrada = np.array([entrada])
    consumoPrevisto = ann.predict(sc.transform(entrada))[0][0]

    return int(consumoPrevisto)