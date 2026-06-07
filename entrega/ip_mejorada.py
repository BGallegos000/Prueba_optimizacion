import time
import random

class IPMejorada:
    def __init__(self, pesos, beneficios, capacidad):
        self.capacidad = capacidad
        # Ordenar por densidad beneficio/peso
        self.items = sorted(zip(pesos, beneficios), key=lambda x: x[1]/x[0], reverse=True)
        self.n = len(pesos)
        self.mejor_beneficio = 0.0

    def cota(self, nivel, peso_actual, beneficio_actual):
        if peso_actual >= self.capacidad: return 0
        res = beneficio_actual
        p_acc = peso_actual
        for i in range(nivel, self.n):
            if p_acc + self.items[i][0] <= self.capacidad:
                p_acc += self.items[i][0]
                res += self.items[i][1]
            else:
                res += self.items[i][1] * ((self.capacidad - p_acc) / self.items[i][0])
                break
        return res

    def bnb(self, nivel, peso_actual, beneficio_actual):
        if beneficio_actual > self.mejor_beneficio:
            self.mejor_beneficio = beneficio_actual
        
        if nivel == self.n or self.cota(nivel, peso_actual, beneficio_actual) <= self.mejor_beneficio:
            return

        # Rama incluir
        if peso_actual + self.items[nivel][0] <= self.capacidad:
            self.bnb(nivel + 1, peso_actual + self.items[nivel][0], beneficio_actual + self.items[nivel][1])
        # Rama excluir
        self.bnb(nivel + 1, peso_actual, beneficio_actual)
        
def generar_instancia(n):
    random.seed(42) # Semilla fija para reproducibilidad
    pesos = [random.uniform(5, 25) for _ in range(n)]
    beneficios = [random.uniform(10, 50) for _ in range(n)]
    capacidad = sum(pesos) * 0.5 # Punto crítico de dificultad
    return pesos, beneficios, capacidad

if __name__ == "__main__":
    for n_test in [20, 40, 60, 100]:
        w, p, cap = generar_instancia(n_test) # Usa la misma funcion de arriba
        solucionador = IPMejorada(w, p, cap)
        inicio = time.perf_counter()
        solucionador.bnb(0, 0.0, 0.0)
        fin = time.perf_counter()
        print(f"N: {n_test} | B&B Beneficio: {solucionador.mejor_beneficio:.2f} | Tiempo: {fin - inicio:.6f}s")