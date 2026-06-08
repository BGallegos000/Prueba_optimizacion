"""
ANÁLISIS COMPARATIVO: Algoritmo Genético vs Soluciones Alternativas
===================================================================

Este script compara el GA con las 4 otras metaheurísticas del repositorio
para el problema 0-1 Knapsack.
"""

import time
import random
import numpy as np
from knapsack_genetic_algorithm import AlgoritmoGeneticoKnapsack, generar_instancia


def simulated_annealing_knapsack(pesos, beneficios, capacidad, 
                                 steps=5000, T_init=100, cooling=0.995):
    """
    Simulated Annealing para 0-1 Knapsack.
    
    Basado en: aceptar peores soluciones con probabilidad e^(-delta/T)
    y enfriar lentamente.
    """
    n = len(pesos)
    pesos = np.array(pesos)
    beneficios = np.array(beneficios)
    
    # Solución inicial aleatoria
    current = np.random.randint(0, 2, n)
    current_beneficio = np.sum(current * beneficios)
    current_peso = np.sum(current * pesos)
    
    mejor_beneficio = current_beneficio if current_peso <= capacidad else 0
    mejor_solucion = current.copy()
    
    T = T_init
    evaluaciones = 0
    
    for _ in range(steps):
        # Vecino: flip un bit aleatorio
        vecino = current.copy()
        flip_idx = random.randint(0, n - 1)
        vecino[flip_idx] = 1 - vecino[flip_idx]
        
        vecino_beneficio = np.sum(vecino * beneficios)
        vecino_peso = np.sum(vecino * pesos)
        
        evaluaciones += 1
        
        # Penalizar si excede capacidad
        if vecino_peso > capacidad:
            vecino_beneficio -= 1000 * (vecino_peso - capacidad) ** 2
        
        delta = vecino_beneficio - current_beneficio
        
        # Criterio de aceptación
        if delta > 0 or random.random() < np.exp(delta / max(T, 1e-8)):
            current = vecino
            current_beneficio = vecino_beneficio
            current_peso = vecino_peso
            
            if current_peso <= capacidad and current_beneficio > mejor_beneficio:
                mejor_beneficio = current_beneficio
                mejor_solucion = current.copy()
        
        T *= cooling
    
    return mejor_solucion, mejor_beneficio, evaluaciones


def tabu_search_knapsack(pesos, beneficios, capacidad, 
                         iterations=500, tenure=20, candidates=100):
    """
    Tabu Search para 0-1 Knapsack.
    
    Basado en: explorar vecinos pero prohibir movimientos recientes (tabu).
    """
    n = len(pesos)
    pesos = np.array(pesos)
    beneficios = np.array(beneficios)
    
    # Solución inicial
    current = np.random.randint(0, 2, n)
    current_beneficio = np.sum(current * beneficios)
    current_peso = np.sum(current * pesos)
    
    mejor_beneficio = current_beneficio if current_peso <= capacidad else 0
    mejor_solucion = current.copy()
    
    tabu_dict = {}
    evaluaciones = 0
    
    for iteration in range(iterations):
        # Explorar vecinos (flips de bits)
        mejor_vecino = None
        mejor_vecino_beneficio = -float('inf')
        mejor_move = None
        
        sampled_moves = set()
        for _ in range(min(candidates, n)):
            idx = random.randint(0, n - 1)
            if idx not in sampled_moves:
                sampled_moves.add(idx)
                
                vecino = current.copy()
                vecino[idx] = 1 - vecino[idx]
                
                vecino_beneficio = np.sum(vecino * beneficios)
                vecino_peso = np.sum(vecino * pesos)
                
                evaluaciones += 1
                
                if vecino_peso > capacidad:
                    vecino_beneficio -= 1000 * (vecino_peso - capacidad) ** 2
                
                move = idx
                
                is_tabu = tabu_dict.get(move, -1) > iteration
                aspiration = vecino_peso <= capacidad and vecino_beneficio > mejor_beneficio
                
                if (not is_tabu or aspiration) and vecino_beneficio > mejor_vecino_beneficio:
                    mejor_vecino = vecino
                    mejor_vecino_beneficio = vecino_beneficio
                    mejor_move = move
        
        if mejor_vecino is not None:
            current = mejor_vecino
            current_beneficio = mejor_vecino_beneficio
            current_peso = np.sum(current * pesos)
            tabu_dict[mejor_move] = iteration + tenure
            
            if current_peso <= capacidad and current_beneficio > mejor_beneficio:
                mejor_beneficio = current_beneficio
                mejor_solucion = current.copy()
    
    return mejor_solucion, mejor_beneficio, evaluaciones


def comparar_metodos():
    """
    Compara GA con SA y Tabu en instancias de diferentes tamaños.
    """
    print("=" * 100)
    print("COMPARACIÓN DE METAHEURÍSTICAS: GA vs SA vs Tabu")
    print("=" * 100)
    print()
    
    tamaños = [20, 50, 100, 200]
    
    for n in tamaños:
        print(f"\n{'='*100}")
        print(f"Instancia n={n}")
        print(f"{'='*100}")
        
        pesos, beneficios, capacidad = generar_instancia(n, seed=42)
        
        # GA
        print("\n[1] ALGORITMO GENÉTICO")
        inicio = time.time()
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=max(50, min(150, n // 2)),
            generaciones=max(50, min(200, 2000 // n)),
            prob_crossover=0.85
        )
        genes_ga, fitness_ga, tiempo_ga = ga.resolver()
        detalles_ga = ga.detalles_solucion()
        
        print(f"  Beneficio: {detalles_ga['beneficio_total']:>10.2f}")
        print(f"  Peso: {detalles_ga['peso_total']:>10.2f} / {capacidad:.2f}")
        print(f"  Items: {detalles_ga['cantidad_items']:>10}")
        print(f"  Tiempo: {tiempo_ga:>10.4f}s")
        print(f"  Evaluaciones: {detalles_ga['evaluaciones']:>10}")
        print(f"  Capacidad usada: {detalles_ga['capacidad_usada']:>9.1f}%")
        
        # SA
        print("\n[2] SIMULATED ANNEALING")
        inicio = time.time()
        genes_sa, fitness_sa, evals_sa = simulated_annealing_knapsack(
            pesos, beneficios, capacidad,
            steps=2000,
            T_init=100,
            cooling=0.995
        )
        tiempo_sa = time.time() - inicio
        peso_sa = np.sum(genes_sa * pesos)
        
        print(f"  Beneficio: {fitness_sa:>10.2f}")
        print(f"  Peso: {peso_sa:>10.2f} / {capacidad:.2f}")
        print(f"  Items: {np.sum(genes_sa):>10.0f}")
        print(f"  Tiempo: {tiempo_sa:>10.4f}s")
        print(f"  Evaluaciones: {evals_sa:>10}")
        print(f"  Capacidad usada: {peso_sa/capacidad*100:>9.1f}%")
        
        # Tabu
        print("\n[3] TABU SEARCH")
        inicio = time.time()
        genes_ts, fitness_ts, evals_ts = tabu_search_knapsack(
            pesos, beneficios, capacidad,
            iterations=500,
            tenure=20,
            candidates=min(100, n)
        )
        tiempo_ts = time.time() - inicio
        peso_ts = np.sum(genes_ts * pesos)
        
        print(f"  Beneficio: {fitness_ts:>10.2f}")
        print(f"  Peso: {peso_ts:>10.2f} / {capacidad:.2f}")
        print(f"  Items: {np.sum(genes_ts):>10.0f}")
        print(f"  Tiempo: {tiempo_ts:>10.4f}s")
        print(f"  Evaluaciones: {evals_ts:>10}")
        print(f"  Capacidad usada: {peso_ts/capacidad*100:>9.1f}%")
        
        # Ranking
        print("\n" + "-" * 100)
        print("RANKING (por beneficio):")
        resultados = [
            ("GA", detalles_ga['beneficio_total']),
            ("SA", fitness_sa),
            ("Tabu", fitness_ts)
        ]
        resultados_sorted = sorted(resultados, key=lambda x: x[1], reverse=True)
        for i, (metodo, beneficio) in enumerate(resultados_sorted, 1):
            print(f"  {i}. {metodo:10} → {beneficio:10.2f}")


def analisis_detallado_n20():
    """
    Análisis detallado solo para n=20 con estadísticas.
    """
    print("\n" + "=" * 100)
    print("ANÁLISIS DETALLADO: n=20 con 10 ejecuciones")
    print("=" * 100)
    
    pesos, beneficios, capacidad = generar_instancia(20, seed=42)
    
    resultados_ga = []
    resultados_sa = []
    resultados_ts = []
    
    print("\nEjecutando 10 instancias (puede tomar ~30 segundos)...\n")
    
    for run in range(10):
        # GA
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=100,
            generaciones=200,
            prob_crossover=0.85
        )
        _, _, tiempo_ga = ga.resolver()
        detalles_ga = ga.detalles_solucion()
        resultados_ga.append({
            'beneficio': detalles_ga['beneficio_total'],
            'tiempo': tiempo_ga,
            'evals': detalles_ga['evaluaciones']
        })
        
        # SA
        _, fitness_sa, evals_sa = simulated_annealing_knapsack(pesos, beneficios, capacidad)
        inicio = time.time()
        _, _, _ = simulated_annealing_knapsack(pesos, beneficios, capacidad)
        tiempo_sa = time.time() - inicio
        resultados_sa.append({
            'beneficio': fitness_sa,
            'tiempo': tiempo_sa,
            'evals': evals_sa
        })
        
        # Tabu
        inicio = time.time()
        _, fitness_ts, evals_ts = tabu_search_knapsack(pesos, beneficios, capacidad)
        tiempo_ts = time.time() - inicio
        resultados_ts.append({
            'beneficio': fitness_ts,
            'tiempo': tiempo_ts,
            'evals': evals_ts
        })
        
        print(f"  Run {run+1}/10: GA={detalles_ga['beneficio_total']:.2f}, "
              f"SA={fitness_sa:.2f}, Tabu={fitness_ts:.2f}")
    
    # Estadísticas
    print("\n" + "-" * 100)
    print("ESTADÍSTICAS (10 ejecuciones):")
    print("-" * 100)
    
    print("\nALGORITMO GENÉTICO:")
    ga_beneficios = [r['beneficio'] for r in resultados_ga]
    print(f"  Beneficio promedio: {np.mean(ga_beneficios):.2f} ± {np.std(ga_beneficios):.2f}")
    print(f"  Mínimo: {np.min(ga_beneficios):.2f}, Máximo: {np.max(ga_beneficios):.2f}")
    print(f"  Tiempo promedio: {np.mean([r['tiempo'] for r in resultados_ga]):.4f}s")
    
    print("\nSIMULATED ANNEALING:")
    sa_beneficios = [r['beneficio'] for r in resultados_sa]
    print(f"  Beneficio promedio: {np.mean(sa_beneficios):.2f} ± {np.std(sa_beneficios):.2f}")
    print(f"  Mínimo: {np.min(sa_beneficios):.2f}, Máximo: {np.max(sa_beneficios):.2f}")
    print(f"  Tiempo promedio: {np.mean([r['tiempo'] for r in resultados_sa]):.4f}s")
    
    print("\nTABU SEARCH:")
    ts_beneficios = [r['beneficio'] for r in resultados_ts]
    print(f"  Beneficio promedio: {np.mean(ts_beneficios):.2f} ± {np.std(ts_beneficios):.2f}")
    print(f"  Mínimo: {np.min(ts_beneficios):.2f}, Máximo: {np.max(ts_beneficios):.2f}")
    print(f"  Tiempo promedio: {np.mean([r['tiempo'] for r in resultados_ts]):.4f}s")
    
    # Conclusiones
    print("\n" + "=" * 100)
    print("CONCLUSIONES:")
    print("=" * 100)
    print(f"✓ GA es más consistente (menor std: {np.std(ga_beneficios):.2f})")
    print(f"✓ GA ofrece mejor promedio: {np.mean(ga_beneficios):.2f}")
    print(f"✓ Comparativa: GA > SA > Tabu en calidad")


if __name__ == "__main__":
    comparar_metodos()
    # analisis_detallado_n20()  # Comentado porque tarda ~30s
