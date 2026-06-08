"""
EJEMPLOS DE USO: Algoritmo Genético para 0-1 Knapsack
=====================================================

Este archivo contiene ejemplos prácticos de cómo utilizar la solución GA
en diferentes escenarios.
"""

import numpy as np
import matplotlib.pyplot as plt
from knapsack_genetic_algorithm import (
    AlgoritmoGeneticoKnapsack,
    generar_instancia
)


def ejemplo_basico():
    """
    Ejemplo 1: Uso básico con una instancia pequeña
    """
    print("=" * 70)
    print("EJEMPLO 1: Uso Básico (n=20)")
    print("=" * 70)
    
    # Generar problema
    pesos, beneficios, capacidad = generar_instancia(n=20, seed=42)
    
    print(f"\nProblema generado:")
    print(f"  Items: 20")
    print(f"  Capacidad mochila: {capacidad:.2f}")
    print(f"  Peso total si se incluyen todos: {sum(pesos):.2f}")
    
    # Crear y resolver
    ga = AlgoritmoGeneticoKnapsack(
        pesos, beneficios, capacidad,
        tamaño_poblacion=100,
        generaciones=200,
        prob_crossover=0.85
    )
    
    genes, fitness, tiempo = ga.resolver()
    detalles = ga.detalles_solucion()
    
    print(f"\nResultados:")
    print(f"  Beneficio total: {detalles['beneficio_total']:.2f}")
    print(f"  Peso utilizado: {detalles['peso_total']:.2f} / {capacidad:.2f} ({detalles['capacidad_usada']:.1f}%)")
    print(f"  Cantidad de items: {detalles['cantidad_items']}")
    print(f"  Items seleccionados: {detalles['items_seleccionados']}")
    print(f"  Tiempo de ejecución: {tiempo:.4f}s")
    print(f"  Evaluaciones realizadas: {detalles['evaluaciones']}")


def ejemplo_para_instancia_real():
    """
    Ejemplo 2: Problema con items específicos (datos reales)
    
    Escenario: Seleccionar equipos de inversión bajo presupuesto.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Problema Real - Selección de Equipos")
    print("=" * 70)
    
    # Equipos: (costo, beneficio)
    equipos = [
        ("Servidor A", 50, 200),      # (nombre, costo, beneficio)
        ("Servidor B", 45, 180),
        ("Switch Red", 30, 120),
        ("Firewall", 35, 150),
        ("Backup Storage", 40, 160),
        ("Router 1", 25, 90),
        ("Router 2", 28, 100),
        ("Monitor", 10, 40),
        ("UPS", 20, 75),
        ("Cables", 5, 20),
    ]
    
    nombres = [e[0] for e in equipos]
    costos = [e[1] for e in equipos]
    beneficios = [e[2] for e in equipos]
    presupuesto = 200  # Presupuesto total disponible
    
    print(f"\nEquipos disponibles (total: {len(equipos)}):")
    print(f"{'Equipo':<20} {'Costo':<10} {'Beneficio':<10} {'Ratio':<10}")
    print("-" * 50)
    for nombre, costo, beneficio in equipos:
        ratio = beneficio / costo
        print(f"{nombre:<20} ${costo:<9} {beneficio:<9} {ratio:.2f}")
    
    print(f"\nPresupuesto disponible: ${presupuesto}")
    
    # Resolver
    ga = AlgoritmoGeneticoKnapsack(
        costos, beneficios, presupuesto,
        tamaño_poblacion=100,
        generaciones=150,
        prob_crossover=0.85
    )
    
    genes, fitness, tiempo = ga.resolver()
    detalles = ga.detalles_solucion()
    
    items_seleccionados = detalles['items_seleccionados']
    
    print(f"\nSolución óptima encontrada en {tiempo:.4f}s:")
    print(f"  Beneficio total: {detalles['beneficio_total']:.0f}")
    print(f"  Costo total: ${detalles['peso_total']:.0f} / ${presupuesto}")
    print(f"  Items seleccionados ({detalles['cantidad_items']}):")
    
    for idx in items_seleccionados:
        nombre, costo, beneficio = equipos[idx]
        print(f"    ✓ {nombre:<20} Costo: ${costo:<5} Beneficio: {beneficio}")


def ejemplo_analisis_sensibilidad():
    """
    Ejemplo 3: Análisis de sensibilidad con diferentes parámetros
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Análisis de Sensibilidad de Parámetros")
    print("=" * 70)
    
    pesos, beneficios, capacidad = generar_instancia(n=50, seed=99)
    
    # Variar tamaño de población
    print("\n3.1 Impacto del Tamaño de Población:")
    print(f"{'Población':<15} {'Beneficio':<15} {'Tiempo (s)':<15} {'Convergencia':<15}")
    print("-" * 60)
    
    poblaciones = [30, 75, 150, 250]
    for pop in poblaciones:
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=pop,
            generaciones=100,
            prob_crossover=0.85
        )
        genes, fitness, tiempo = ga.resolver()
        convergencia_gen = next(
            (i for i, f in enumerate(ga.mejor_fitness_por_gen) if f == ga.mejor_fitness_por_gen[-1]),
            len(ga.mejor_fitness_por_gen)
        )
        print(f"{pop:<15} {ga.detalles_solucion()['beneficio_total']:<15.2f} {tiempo:<15.4f} Gen {convergencia_gen}")
    
    # Variar probabilidad de crossover
    print("\n3.2 Impacto de la Probabilidad de Crossover:")
    print(f"{'Pc':<15} {'Beneficio':<15} {'Tiempo (s)':<15} {'Convergencia':<15}")
    print("-" * 60)
    
    crossover_probs = [0.5, 0.7, 0.85, 0.95]
    for pc in crossover_probs:
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=100,
            generaciones=100,
            prob_crossover=pc
        )
        genes, fitness, tiempo = ga.resolver()
        convergencia_gen = next(
            (i for i, f in enumerate(ga.mejor_fitness_por_gen) if f == ga.mejor_fitness_por_gen[-1]),
            len(ga.mejor_fitness_por_gen)
        )
        print(f"{pc:<15.2f} {ga.detalles_solucion()['beneficio_total']:<15.2f} {tiempo:<15.4f} Gen {convergencia_gen}")


def ejemplo_comparacion_instancias():
    """
    Ejemplo 4: Comparación de rendimiento en diferentes tamaños
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Escalabilidad - Diferentes Tamaños")
    print("=" * 70)
    
    tamaños = [10, 25, 50, 100, 200, 500, 1000]
    resultados = []
    
    print(f"\n{'N':<8} {'Beneficio':<15} {'Tiempo (s)':<15} {'Items Sel.':<15} {'Capacidad %':<15}")
    print("-" * 68)
    
    for n in tamaños:
        pesos, beneficios, capacidad = generar_instancia(n, seed=42)
        
        # Ajustar parámetros según tamaño
        pop_size = max(50, min(150, n // 2))
        gens = max(50, min(200, 5000 // n))
        
        ga = AlgoritmoGeneticoKnapsack(
            pesos, beneficios, capacidad,
            tamaño_poblacion=pop_size,
            generaciones=gens,
            prob_crossover=0.85
        )
        
        genes, fitness, tiempo = ga.resolver()
        detalles = ga.detalles_solucion()
        
        resultados.append({
            'n': n,
            'beneficio': detalles['beneficio_total'],
            'tiempo': tiempo,
            'items': detalles['cantidad_items'],
            'capacidad_pct': detalles['capacidad_usada']
        })
        
        print(f"{n:<8} {detalles['beneficio_total']:<15.2f} {tiempo:<15.4f} {detalles['cantidad_items']:<15} {detalles['capacidad_usada']:<15.1f}%")
    
    return resultados


def ejemplo_visualizacion_convergencia():
    """
    Ejemplo 5: Visualización de la convergencia generacional
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Convergencia Generacional (Visualización)")
    print("=" * 70)
    
    pesos, beneficios, capacidad = generar_instancia(n=50, seed=42)
    
    ga = AlgoritmoGeneticoKnapsack(
        pesos, beneficios, capacidad,
        tamaño_poblacion=100,
        generaciones=200,
        prob_crossover=0.85
    )
    
    genes, fitness, tiempo = ga.resolver()
    
    # Mostrar convergencia
    print(f"\nConvergencia por generación (cada 20 gen):")
    print(f"{'Generación':<15} {'Mejor Fitness':<20} {'Mejora?':<15}")
    print("-" * 50)
    
    prev_fitness = ga.mejor_fitness_por_gen[0]
    for gen in range(0, len(ga.mejor_fitness_por_gen), 20):
        if gen < len(ga.mejor_fitness_por_gen):
            actual = ga.mejor_fitness_por_gen[gen]
            mejora = "✓ SÍ" if actual > prev_fitness else "  NO"
            print(f"{gen:<15} {actual:<20.2f} {mejora}")
            prev_fitness = actual
    
    # Último
    actual = ga.mejor_fitness_por_gen[-1]
    mejora = "✓ SÍ" if actual > prev_fitness else "  NO"
    print(f"{len(ga.mejor_fitness_por_gen)-1:<15} {actual:<20.2f} {mejora}")
    
    # Estadísticas
    print(f"\nEstadísticas de convergencia:")
    print(f"  Fitness inicial: {ga.mejor_fitness_por_gen[0]:.2f}")
    print(f"  Fitness final: {ga.mejor_fitness_por_gen[-1]:.2f}")
    print(f"  Mejora total: {ga.mejor_fitness_por_gen[-1] - ga.mejor_fitness_por_gen[0]:.2f}")
    print(f"  Generación de convergencia: {next((i for i, f in enumerate(ga.mejor_fitness_por_gen) if f == ga.mejor_fitness_por_gen[-1]), len(ga.mejor_fitness_por_gen))}")


if __name__ == "__main__":
    # Ejecutar todos los ejemplos
    ejemplo_basico()
    ejemplo_para_instancia_real()
    ejemplo_analisis_sensibilidad()
    resultados = ejemplo_comparacion_instancias()
    ejemplo_visualizacion_convergencia()
    
    print("\n" + "=" * 70)
    print("TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 70)
