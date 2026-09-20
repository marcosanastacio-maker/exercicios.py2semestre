"""
Exercicio 9 - Metricas honestas (scikit-learn)

Calcula acuracia, precisao, recall, F1 e matriz de confusao para um
conjunto de teste desbalanceado, e mostra por que a acuracia sozinha
engana nesse cenario.
"""

from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)


def calcular_metricas(y_true, y_pred):
    matriz = confusion_matrix(y_true, y_pred)
    acuracia = accuracy_score(y_true, y_pred)
    precisao = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    return matriz, acuracia, precisao, recall, f1


if __name__ == "__main__":
    y_true = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # 8 normais, 2 ataques
    y_pred = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]  # perdeu 1 ataque

    matriz, acuracia, precisao, recall, f1 = calcular_metricas(y_true, y_pred)

    print(f"Matriz: {matriz.tolist()}")
    print(f"Acurácia: {acuracia:.2f} | Precisão: {precisao:.2f} | Recall: {recall:.2f} | F1: {f1:.2f}")
    print(
        f"Comentário: acurácia {acuracia:.2f} mascara que METADE dos ataques "
        f"passou (recall {recall:.2f})."
    )
