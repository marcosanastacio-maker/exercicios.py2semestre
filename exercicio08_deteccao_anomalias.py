"""
Exercicio 8 - Deteccao de anomalias (scikit-learn)

Usa IsolationForest para sinalizar comportamentos anomalos em
metricas de acesso: [requisicoes_min, conexoes_simultaneas].
"""

import numpy as np
from sklearn.ensemble import IsolationForest


def detectar_anomalias(dados, contamination=0.25):
    modelo = IsolationForest(contamination=contamination, random_state=42)
    predicoes = modelo.fit_predict(dados)  # -1 = anomalia, 1 = normal
    return predicoes


if __name__ == "__main__":
    # [requisicoes_min, conexoes_simultaneas]
    trafego = np.array([
        [100, 5], [120, 6], [110, 5], [105, 4],
        [50000, 500], [109, 5], [111, 6], [45000, 450],
    ])

    predicoes = detectar_anomalias(trafego, contamination=0.25)

    for i, (amostra, predicao) in enumerate(zip(trafego, predicoes)):
        status = "ANOMALIA" if predicao == -1 else "Normal"
        if status == "ANOMALIA":
            valores = [int(v) for v in amostra]
            print(f"Amostra {i}: {valores} -> {status}")

    print("Demais -> Normal")
