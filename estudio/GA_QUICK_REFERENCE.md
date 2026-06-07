# GA QUICK REFERENCE - Cheat Sheet

## 🚀 GA en 2 Minutos

### Definición
**Algoritmo Genético**: Metaheurística que simula evolución natural para resolver problemas de optimización.

### Estructura Básica
```python
población = generar_aleatoria(100)
for gen in range(200):
    # 1. Seleccionar mejores
    elite = top_2(población)
    
    # 2. Crear nuevos hijos
    while len(población) < 100:
        padre1 = torneo(población)
        padre2 = torneo(población)
        hijo = crossover(padre1, padre2)
        hijo = mutar(hijo)
        población.append(hijo)
    
    # 3. Reemplazar población
    población = elite + nuevos_hijos

return mejor_solución_encontrada
```

---

## 📊 GA Cheat Sheet

### Parámetros Clave

| Parámetro | Valor | Rango Típico | Sensibilidad |
|-----------|-------|--------------|--------------|
| Tamaño Población | 100 | 30-300 | MEDIA |
| Generaciones | 200 | 50-500 | BAJA |
| Prob. Crossover | 0.85 | 0.6-0.95 | BAJA |
| Prob. Mutación | 1/n | 1/(2n)-5/n | ALTA |
| Elite Size | 2 | 1-5 | MEDIA |
| Torneo | 3 | 2-10 | MEDIA |

### Operadores

```
SELECCIÓN (Presión)
├─ Torneo: k aleatorios → mejor gana
│  ├─ k=2: Presión suave (exploración)
│  ├─ k=3: Balance (recomendado)
│  └─ k=5: Presión fuerte (explotación)
└─ Alternativa: Ruleta (fitness proporcional) ✗

CROSSOVER (Recombinación)
├─ Punto simple: 80% chance
│  └─ Divide: padre1[:c] + padre2[c:]
├─ Uniforme: cada bit 50% de cada padre ✗
└─ Dos puntos: raro, poco ganancia

MUTACIÓN (Exploración)
├─ Bit-flip: invierte cada bit con prob 1/n
└─ NUNCA: tasa 0.5+ (caos), tasa <0.001 (estancamiento)

ELITISMO (Preservación)
└─ Copia top-2 a siguiente generación
   └─ Garantiza: fitness nunca decrece
```

---

## 🧬 Conceptos Clave

### Esquema (Schema)
Patrón de genes: `1*1**0*` (donde `*` = cualquier)
- **Orden**: Bits especificados (ejemplo: 3)
- **Déficit**: Distancia entre bits
- **GA preserva** orden-pequeño + fitness-alto

### Building Blocks
Sub-soluciones buenas que se heredan
- Crossover **combina** building blocks
- Población múltiple **explora** combinaciones
- GA **escala** hacia mejores soluciones

### Paralelismo Implícito
Población P examina implícitamente P^3 esquemas
- Ejemplo: P=100 → 1,000,000 esquemas en paralelo
- Más eficiente que búsqueda exhaustiva

### Fitness Landscape
Visualización de todas 2^n soluciones por fitness
- **Unimodal**: Un pico (fácil)
- **Multimodal**: Múltiples picos (difícil, GA destaca)

---

## 🎯 Cuándo Usar GA

### ✅ GA es IDEAL para:
- Problemas combinatorios (2^n soluciones)
- Multimodal extremo (muchos óptimos locales)
- Sin estructura especial exploitable
- Knapsack, TSP, Scheduling, Diseño
- Cuando no necesitas solución ÓPTIMA, solo buena

### ⚠️ GA NO es ideal para:
- Funciones unimodales (Hill climbing mejor)
- Espacios continuos puros (PSO, ES mejor)
- TSP grande (ACO mejor)
- Problemas con estructura fuerte (Tabu específico)
- Cuando necesitas GARANTÍA de óptimo (B&B)

---

## 🔧 Implementación Rápida

### Pseudocódigo
```
INICIALIZAR: población aleatoria
LOOP generaciones:
  1. EVALUAR: calcular fitness cada individuo
  2. SELECCIONAR: torneo → padres
  3. CROSSOVER: 80% → combinar padres
  4. MUTAR: 1/n → invertir bits
  5. EVALUAR: nuevo hijo
  6. ELITISMO: preservar top-2
  7. REEMPLAZAR: mantener tamaño población
RETORNAR: mejor solución encontrada
```

### Línea Clave Explicada
```python
genes_mutados[i] = 1 - genes_mutados[i]  # Flip bit
# ¿Por qué esto?
# - Invierte: 0→1, 1→0
# - Simple de entender
# - Fácil de paralelizar
```

---

## 📈 Convergencia

### Típico
```
Gen 1-30:    Mejora rápida (30+ por gen) ← Exploración
Gen 30-100:  Mejora gradual (1-5 por gen) ← Balance
Gen 100-200: Mejora mínima (0.1 per gen) ← Explotación
```

### Patrones Malos
- **Platea** desde gen 50: Convergencia prematura
- **Oscilante**: Sin elitismo (fitness baja a veces)
- **Sin cambio gen 1-20**: Mutación muy alta

### Soluciones
```
Convergencia prematura:
  ├─ Reducir torneo size (menos presión)
  ├─ Aumentar mutación
  └─ Aumentar población

Sin mejora inicial:
  ├─ Aumentar torneo size
  ├─ Reducir mutación
  └─ Verificar fitness calcula bien
```

---

## 🏆 GA vs Alternativas

| Aspecto | GA | SA | Tabu | ACO | B&B |
|---------|-----|-----|------|-----|-----|
| **Teoría** | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Velocidad** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| **Calidad** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Generalidad** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Facilidad** | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ |
| **Escalabilidad** | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ✗ |

---

## 🧠 Errores Comunes

### ❌ Error 1: Mutación Muy Alta
```python
prob_mutacion = 0.1  # MALO
# Resultado: Random search casi puro
# Mejor: 0.01 (= 1/100 para n=100)
```

### ❌ Error 2: Sin Elitismo
```python
nueva_poblacion = hijos_solo  # MALO
# Resultado: Fitness puede bajar, sin garantía convergencia
# Mejor: nueva_poblacion = elite + hijos
```

### ❌ Error 3: Población Muy Pequeña
```python
tamaño_poblacion = 10  # MALO para n>30
# Resultado: Poco parallelismo, convergencia prematura
# Mejor: max(50, min(150, n//2))
```

### ❌ Error 4: Evaluación Múltiple
```python
hijo.evaluar()  # después crossover
hijo = mutar(hijo)
# hijo.fitness está OBSOLETO ahora
# Mejor: evaluar al final, después mutar
```

### ❌ Error 5: Problema en Penalización
```python
if peso > capacidad:
    fitness = 0  # MALO
# Resultado: SA/Tabu se atascan (todo tiene fitness=0)
# Mejor: fitness = beneficio - penalización × exceso²
```

---

## 💻 Código Mínimo (20 líneas)

```python
import numpy as np
import random

def ga_knapsack(pesos, beneficios, capacidad, pop_size=100, gens=200):
    n = len(pesos)
    pop = [np.random.randint(0, 2, n) for _ in range(pop_size)]
    
    for gen in range(gens):
        # Evaluar
        fitness = []
        for genes in pop:
            peso = np.sum(genes * pesos)
            beneficio = np.sum(genes * beneficios)
            if peso > capacidad:
                fit = beneficio - 1000 * (peso - capacidad)**2
            else:
                fit = beneficio
            fitness.append(fit)
        
        # Seleccionar elite
        elite_idx = sorted(range(pop_size), key=lambda i: fitness[i])[-2:]
        elite = [pop[i].copy() for i in elite_idx]
        
        # Crear nuevos
        nueva_pop = elite
        while len(nueva_pop) < pop_size:
            # Torneo
            idx1, idx2 = random.sample(range(pop_size), 2)
            p1 = pop[idx1 if fitness[idx1] > fitness[idx2] else idx2]
            idx1, idx2 = random.sample(range(pop_size), 2)
            p2 = pop[idx1 if fitness[idx1] > fitness[idx2] else idx2]
            
            # Crossover
            if random.random() < 0.85:
                c = random.randint(1, n-1)
                hijo = np.concatenate([p1[:c], p2[c:]])
            else:
                hijo = p1.copy()
            
            # Mutación
            for i in range(n):
                if random.random() < 1/n:
                    hijo[i] = 1 - hijo[i]
            
            nueva_pop.append(hijo)
        
        pop = nueva_pop[:pop_size]
    
    # Retornar mejor
    fitness_final = []
    for genes in pop:
        peso = np.sum(genes * pesos)
        beneficio = np.sum(genes * beneficios)
        if peso > capacidad:
            fit = beneficio - 1000 * (peso - capacidad)**2
        else:
            fit = beneficio
        fitness_final.append(fit)
    
    best_idx = np.argmax(fitness_final)
    return pop[best_idx], fitness_final[best_idx]
```

---

## 📚 Lectura Recomendada

| Documento | Páginas | Tiempo | Para Quién |
|-----------|---------|--------|-----------|
| INDICE_DOCUMENTACION_PEDAGOGICA | 1 | 5 min | Todos |
| 03_PUNTOS_CLAVE_GA_DEFINICIONES | 15 | 45 min | Principiantes |
| 02_EXPLICACION_CODIGO_LINEA_POR_LINEA | 20 | 1h | Programadores |
| 01_ANALISIS_POR_QUE_GA_DESTACA | 12 | 45 min | Comparativas |
| 04_CONTEXTO_HISTORICO_GA_DOMINA | 15 | 1h | Académicos |

---

## ✅ Checklist: "Mi GA Funciona Bien Si..."

- ✓ Fitness mejora consistentemente gen 1-50
- ✓ Fitness platea después gen 100 (convergencia normal)
- ✓ Std dev de múltiples runs es bajo
- ✓ Fitness nunca baja (elitismo funciona)
- ✓ Con n=20 puede encontrar óptimo conocido
- ✓ Escala a n=1000 en <2 segundos
- ✓ Poblaciones diferentes convergen a similar solución

---

## 🎓 Preguntas de Examen

1. ¿Qué es un esquema?
2. ¿Cuál es el rol de crossover vs mutación?
3. ¿Por qué GA gana contra SA en multimodal?
4. ¿Qué es convergencia prematura y cómo evitarla?
5. ¿Por qué mutación = 1/n?
6. ¿Cómo GA examina P^3 esquemas con P evaluaciones?
7. ¿Por qué punto-simple crossover > uniforme?
8. ¿Cuál es el costo computacional de GA?

---

**Tip Final**: Si GA no funciona bien, 9/10 veces es:
1. Penalización mal calibrada
2. Mutación muy baja o muy alta
3. Población muy pequeña
4. Evaluación de fitness incorrecta

Revisa esos primero antes de cambiar algoritmo.

---

**Versión**: Quick Reference v1.0
**Para**: Solemne_optimizacion - Knapsack Genético
**Creado por**: GitHub Copilot
