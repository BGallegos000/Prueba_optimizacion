"""
Algoritmo Genético para Problema 0-1 Knapsack
===============================================
Solución metaheurística que combina selección natural, crossover y mutación
para encontrar soluciones de alta calidad en tiempo razonable.

Comparación con Branch and Bound:
- GA: O(generaciones * población * n) → escalable a instancias grandes
- B&B: O(n!) peor caso → solo para instancias pequeñas
"""

import time
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Individuo:
    """Representa un cromosoma (solución) en la población."""
    genes: np.ndarray  # Vector binario [0,1,0,1,...]
    fitness: float = None
    
    def evaluar(self, pesos: np.ndarray, beneficios: np.ndarray, 
                capacidad: float, penalizacion: float = 1000.0) -> float:
        """
        Calcula el fitness de este individuo.
        Penaliza soluciones que exceden la capacidad.
        """
        peso_total = np.sum(self.genes * pesos)
        beneficio_total = np.sum(self.genes * beneficios)
        
        if peso_total > capacidad:
            # Penalización cuadrática por exceso de peso
            exceso = peso_total - capacidad
            self.fitness = beneficio_total - penalizacion * (exceso ** 2)
        else:
            self.fitness = beneficio_total
        
        return self.fitness


class AlgoritmoGeneticoKnapsack:
    """
    Resolvedor del Knapsack usando Algoritmo Genético.
    
    Parámetros:
    -----------
    pesos : list
        Pesos de los items
    beneficios : list
        Beneficios de los items
    capacidad : float
        Capacidad máxima de la mochila
    tamaño_poblacion : int
        Número de individuos en cada generación (default: 100)
    generaciones : int
        Número de generaciones a evolucionar (default: 200)
    prob_crossover : float
        Probabilidad de crossover (default: 0.8)
    prob_mutacion : float
        Probabilidad de mutación por gen (default: 1/n)
    """
    
    def __init__(self, pesos: List[float], beneficios: List[float],
                 capacidad: float, tamaño_poblacion: int = 100,
                 generaciones: int = 200, prob_crossover: float = 0.8):
        self.pesos = np.array(pesos, dtype=float)
        self.beneficios = np.array(beneficios, dtype=float)
        self.capacidad = capacidad
        self.n = len(pesos)
        
        self.tamaño_poblacion = tamaño_poblacion
        self.generaciones = generaciones
        self.prob_crossover = prob_crossover
        self.prob_mutacion = 1.0 / self.n  # Adaptive mutation rate
        
        self.mejor_fitness_por_gen = []
        self.mejor_individuo = None
        self.evaluaciones = 0
        
    def _inicializar_poblacion(self) -> List[Individuo]:
        """Crea una población inicial aleatoria."""
        poblacion = []
        for _ in range(self.tamaño_poblacion):
            genes = np.random.randint(0, 2, size=self.n)
            ind = Individuo(genes)
            ind.evaluar(self.pesos, self.beneficios, self.capacidad)
            self.evaluaciones += 1
            poblacion.append(ind)
        return poblacion
    
    def _seleccion_torneo(self, poblacion: List[Individuo], 
                          tamaño_torneo: int = 3) -> Individuo:
        """Selecciona un individuo mediante torneo."""
        candidatos = random.sample(poblacion, k=tamaño_torneo)
        return max(candidatos, key=lambda x: x.fitness)
    
    def _crossover(self, padre1: Individuo, padre2: Individuo) -> Individuo:
        """
        Realiza crossover de punto simple.
        Punto de corte aleatorio entre genes de ambos padres.
        """
        if random.random() > self.prob_crossover:
            return Individuo(padre1.genes.copy())
        
        punto_corte = random.randint(1, self.n - 1)
        genes_hijo = np.concatenate([
            padre1.genes[:punto_corte],
            padre2.genes[punto_corte:]
        ])
        return Individuo(genes_hijo)
    
    def _mutar(self, individuo: Individuo) -> Individuo:
        """
        Mutación: invierte bits con probabilidad prob_mutacion.
        """
        genes_mutados = individuo.genes.copy()
        for i in range(self.n):
            if random.random() < self.prob_mutacion:
                genes_mutados[i] = 1 - genes_mutados[i]
        return Individuo(genes_mutados)
    
    def _aplicar_elitismo(self, poblacion: List[Individuo], 
                          elite_size: int = 2) -> List[Individuo]:
        """Conserva los mejores individuos para la siguiente generación."""
        poblacion_ordenada = sorted(poblacion, 
                                    key=lambda x: x.fitness, 
                                    reverse=True)
        return poblacion_ordenada[:elite_size]
    
    def resolver(self) -> Tuple[np.ndarray, float, float]:
        """
        Ejecuta el algoritmo genético y retorna la mejor solución encontrada.
        
        Retorna:
        --------
        (mejor_cromosoma, mejor_beneficio, tiempo_ejecucion)
        """
        inicio = time.time()
        
        poblacion = self._inicializar_poblacion()
        self.mejor_individuo = max(poblacion, key=lambda x: x.fitness)
        
        for gen in range(self.generaciones):
            # Guardar el mejor fitness de esta generación
            mejor_gen = max(poblacion, key=lambda x: x.fitness)
            self.mejor_fitness_por_gen.append(mejor_gen.fitness)
            
            # Actualizar mejor global
            if mejor_gen.fitness > self.mejor_individuo.fitness:
                self.mejor_individuo = Individuo(mejor_gen.genes.copy())
                self.mejor_individuo.fitness = mejor_gen.fitness
            
            # Crear nueva población
            nueva_poblacion = self._aplicar_elitismo(poblacion, elite_size=2)
            
            # Generar offspring
            while len(nueva_poblacion) < self.tamaño_poblacion:
                padre1 = self._seleccion_torneo(poblacion)
                padre2 = self._seleccion_torneo(poblacion)
                hijo = self._crossover(padre1, padre2)
                hijo = self._mutar(hijo)
                hijo.evaluar(self.pesos, self.beneficios, self.capacidad)
                self.evaluaciones += 1
                nueva_poblacion.append(hijo)
            
            poblacion = nueva_poblacion[:self.tamaño_poblacion]
        
        tiempo_ejecucion = time.time() - inicio
        return self.mejor_individuo.genes, self.mejor_individuo.fitness, tiempo_ejecucion
    
    def detalles_solucion(self) -> dict:
        """Retorna detalles de la mejor solución encontrada."""
        items_seleccionados = np.where(self.mejor_individuo.genes == 1)[0]
        peso_total = np.sum(self.mejor_individuo.genes * self.pesos)
        beneficio_total = np.sum(self.mejor_individuo.genes * self.beneficios)
        
        return {
            'items_seleccionados': items_seleccionados.tolist(),
            'cantidad_items': len(items_seleccionados),
            'peso_total': float(peso_total),
            'beneficio_total': float(beneficio_total),
            'capacidad_usada': float(peso_total / self.capacidad * 100),
            'fitness': float(self.mejor_individuo.fitness),
            'evaluaciones': self.evaluaciones
        }


def generar_instancia(n: int, seed: int = 42) -> Tuple[List[float], List[float], float]:
    """
    Genera una instancia de Knapsack aleatorio.
    
    La capacidad se fija al 50% del peso total para crear instancias 
    moderadamente difíciles (punto crítico).
    """
    rng = np.random.RandomState(seed)
    pesos = [rng.uniform(5, 25) for _ in range(n)]
    beneficios = [rng.uniform(10, 50) for _ in range(n)]
    capacidad = sum(pesos) * 0.5
    return pesos, beneficios, capacidad


def comparar_con_branch_and_bound(pesos, beneficios, capacidad):
    """
    Compara GA contra Branch and Bound (para instancias pequeñas).
    B&B garantiza optimalidad, GA es aproximado pero más rápido.
    """
    try:
        from ip_mejorada import IPMejorada
        
        w, p, cap = pesos, beneficios, capacidad
        solver_bb = IPMejorada(w, p, cap)
        
        inicio_bb = time.time()
        solver_bb.bnb(0, 0.0, 0.0)
        tiempo_bb = time.time() - inicio_bb
        
        return {
            'bb_beneficio': solver_bb.mejor_beneficio,
            'bb_tiempo': tiempo_bb,
            'bb_encontrado': True
        }
    except (ImportError, Exception):
        return {
            'bb_beneficio': None,
            'bb_tiempo': None,
            'bb_encontrado': False
        }


if __name__ == "__main__":
    print("=" * 80)
    print("ALGORITMO GENÉTICO PARA 0-1 KNAPSACK")
    print("=" * 80)
    print()
    
    # Pruebas con diferentes tamaños
    tamaños = [20, 50, 100, 200, 500]
    
    print(f"{'N':>4} | {'GA Beneficio':>12} | {'GA Tiempo':>10} | {'Capacidad %':>10} | {'Items':>6}")
    print("-" * 70)
    
    for n in tamaños:
        pesos, beneficios, capacidad = generar_instancia(n, seed=42)
        
        # Ejecutar GA
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=max(50, min(150, n // 2)),
            generaciones=max(50, min(300, 1000 // (n // 20 + 1))),
            prob_crossover=0.85
        )
        
        genes, fitness, tiempo = ga.resolver()
        detalles = ga.detalles_solucion()
        
        print(f"{n:4d} | {detalles['beneficio_total']:12.2f} | "
              f"{tiempo:10.4f}s | {detalles['capacidad_usada']:10.1f}% | "
              f"{detalles['cantidad_items']:6d}")
    
    print()
    print("=" * 80)
    print("COMPARACIÓN DETALLADA: INSTANCIA PEQUEÑA (n=20)")
    print("=" * 80)
    print()
    
    # Instancia pequeña para comparación con B&B
    pesos_20, beneficios_20, capacidad_20 = generar_instancia(20, seed=42)
    
    # GA
    ga_20 = AlgoritmoGeneticoKnapsack(
        pesos_20, beneficios_20, capacidad_20,
        tamaño_poblacion=100,
        generaciones=200,
        prob_crossover=0.85
    )
    genes_ga, fitness_ga, tiempo_ga = ga_20.resolver()
    detalles_ga = ga_20.detalles_solucion()
    
    print(f"Algoritmo Genético (n=20)")
    print(f"  Beneficio:        {detalles_ga['beneficio_total']:.2f}")
    print(f"  Peso total:       {detalles_ga['peso_total']:.2f} / {capacidad_20:.2f}")
    print(f"  Items:            {detalles_ga['cantidad_items']}")
    print(f"  Tiempo:           {tiempo_ga:.4f}s")
    print(f"  Evaluaciones:     {detalles_ga['evaluaciones']}")
    print()
    
    # Intentar comparar con B&B si está disponible
    resultado_bb = comparar_con_branch_and_bound(pesos_20, beneficios_20, capacidad_20)
    if resultado_bb['bb_encontrado']:
        print(f"Branch and Bound (n=20)")
        print(f"  Beneficio:        {resultado_bb['bb_beneficio']:.2f}")
        print(f"  Tiempo:           {resultado_bb['bb_tiempo']:.4f}s")
        print()
        
        gap = ((resultado_bb['bb_beneficio'] - detalles_ga['beneficio_total']) 
               / resultado_bb['bb_beneficio'] * 100)
        print(f"GAP entre GA y B&B: {gap:.2f}%")
        print(f"  (Negativo = GA mejor; Positivo = B&B mejor)")
    else:
        print("Branch and Bound no disponible para comparación")
    
    print()
    print("=" * 80)
    print("CONVERGENCIA: Mejor fitness por generación (n=20)")
    print("=" * 80)
    print()
    
    # Mostrar convergencia cada 20 generaciones
    for gen in range(0, len(ga_20.mejor_fitness_por_gen), 20):
        if gen < len(ga_20.mejor_fitness_por_gen):
            print(f"Gen {gen:3d}: {ga_20.mejor_fitness_por_gen[gen]:10.2f}")
    print(f"Gen {len(ga_20.mejor_fitness_por_gen)-1:3d}: "
          f"{ga_20.mejor_fitness_por_gen[-1]:10.2f}")
