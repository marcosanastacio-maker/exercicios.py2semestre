"""
Exercicio 7 - Classificador de trafego (scikit-learn)

Treina um RandomForestClassifier para distinguir trafego normal (0)
de malicioso (1), com base em [bytes, porta, duracao].
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def treinar_modelo(X, y):
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X_treino, y_treino)

    y_pred = modelo.predict(X_teste)
    acuracia = accuracy_score(y_teste, y_pred)

    return modelo, acuracia


def classificar_caso(modelo, caso):
    predicao = modelo.predict(caso)[0]
    return "Malicioso (1)" if predicao == 1 else "Normal (0)"


if __name__ == "__main__":
    # Features: [bytes, porta, duracao]
    X = np.array([
        [500, 80, 0.1],    [1200, 80, 0.5],  [64, 22, 0.02],   [64000, 4444, 10.0],
        [45000, 8080, 15.0], [60000, 31337, 20.0], [800, 443, 0.3], [300, 53, 0.05],
        [55000, 9999, 18.0], [200, 25, 0.2],
    ])
    y = np.array([0, 0, 0, 1, 1, 1, 0, 0, 1, 0])

    caso_novo = [[58000, 4444, 16.0]]

    modelo, acuracia = treinar_modelo(X, y)

    print(f"Acurácia no teste: {acuracia:.2f}")
    resultado = classificar_caso(modelo, caso_novo)
    print(f"Caso novo {caso_novo[0]} -> {resultado}")
