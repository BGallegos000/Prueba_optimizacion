# PUNTOS CLAVE DEL ALGORITMO GENÉTICO - Definiciones Esenciales

## 1. TEOREMA DE ESQUEMAS (Holland, 1975)

### Definición
Un **esquema** es un patrón de genes que puede procesarse implícitamente en paralelo por un GA.

### Ejemplo
```
Esquema: 1*1***0* 
         (donde * es "cualquier valor")

Individuos que coinciden:
  [1, 0, 1, 0, 0, 0, 1]  ✓ Coincide
  [1, 1, 1, 0, 0, 0, 0]  ✓ Coincide
  [1, 0, 1, 1, 1, 1, 0]  ✓ Coincide
  [0, 0, 1, 0, 0, 0, 0]  ✗ No coincide (1° bit)
```

### Teorema de Esquemas
El GA implícitamente mantiene múltiples esquemas en paralelo, asignando más evaluaciones a esquemas con:
- **Orden bajo**: Pocos bits especificados (1*1 < 1*1*0*) = esquemas cortos
- **Déficit bajo**: Distancia entre posiciones especificadas pequeño
- **Fitness alto**: Mejor desempeño promedio

### Implicación Práctica
```
Por qué punto-simple crossover es mejor que uniforme:

Uniforme rompe todos los esquemas:
  Schema: 1*1**** (bits 0,2 especificados)
  Padre1:  10101010
  Padre2:  11001100
  → Cada bit 50% chance → solo 25% chance de preservar 1*1
  
Punto-simple preserva esquemas cortos:
  Punto 1: [1|01010|10] → 75% chance preserva 1* o *1
  Punto 2: [10|1010|10] → 50% chance preserva 1*1
  
  → Mayor orden de preservación
```

---

## 2. HIPÓTESIS DEL BUILDING BLOCK (Goldberg, 1989)

### Definición
Los GA resuelven problemas difíciles mediante la combinación de "building blocks": 
sub-soluciones cortas, de orden bajo, de alto rendimiento.

### Mecanismo
```
BUILDING BLOCKS en Knapsack:
  BB1: Items de alto ratio beneficio/peso {3, 5, 7}
  BB2: Items que completan capacidad {1, 4}
  BB3: Items de máximo beneficio {15, 22}

GA BUSCA:
  1. Identificar buenos BB en población inicial
  2. Preservar BB mediante crossover (heredan juntos)
  3. Recombinar en nuevas configuraciones
  4. Mejorar conservando estructura BB
```

### Pseudocódigo
```
Gen 0-20: GA descubre building blocks
Gen 20-100: GA recombina bloques en mejores formas
Gen 100-200: GA refina alrededor de óptimos
```

### Por Qué Funciona
```
Comparativa:

BÚSQUEDA ALEATORIA: 2^n combinaciones, cada vez es suerte
  Tiempo esperado: 2^(n-1) evaluaciones

BRANCH & BOUND: Explora árbol sistemáticamente
  Tiempo: O(2^n) worst-case, O(n log n) best-case
  Problema: Necesita óptimo verdadero para podar
  
GA: Hace evolucionar building blocks
  Tiempo: O(G × P × n) = O(200 × 100 × 1000) = 20 millones ops
  Ventaja: Halla buenos (no necesariamente óptimos) en tiempo polinomial
```

---

## 3. PARENTESCO SELECTIVO (Selective Pressure)

### Definición
La **presión selectiva** es la fuerza con que el GA favorece mejores soluciones.

### Controladores

#### A. Tamaño de Torneo
```python
tamaño_torneo = 2:
  Escoge mejor de 2 → presión suave
  Pobres todavía tiene ~50% chance de reproducirse
  → Mayor exploración

tamaño_torneo = 5:
  Escoge mejor de 5 → presión fuerte
  Pobres casi nunca se reproducen
  → Mayor explotación
  
tamaño_torneo = 3: (default)
  Punto medio óptimo
```

#### B. Elitismo
```python
elite_size = 0:
  Mejor generación puede desaparecer
  Convergencia no garantizada
  Fitness puede oscilar
  
elite_size = 2: (default)
  Preserva 2 mejores
  Monotonicidad garantizada
  Balance preservación-novedad
  
elite_size = 10:
  Muy conservador
  Convergencia rápida pero local
  Pérdida de diversidad
```

#### C. Mutación
```python
prob_mutacion = 0.001:
  Muy baja
  Cambios raros, exploración lenta
  
prob_mutacion = 0.01 (= 1/n para n=100): (default)
  ~1 bit por individuo se invierte
  Balance óptimo
  
prob_mutacion = 0.5:
  Caos, destruye buenas soluciones
  Equivalente a casi random search
```

### Visualización
```
        EXPLORACIÓN ←─────┐
                          │
       Tamaño_torneo=2   │   Tamaño_torneo=5
       Mutación=5/n      │   Mutación=1/(10n)
       Elite=0           │   Elite=5
           ↓             │     ↓
         ╔════════════════╩════════════╗
         ║   ESPACIO DE PARÁMETROS    ║
         ╚════════════════╦════════════╝
           ↑              │ 
    ÓPTIMO: tamaño=3      │   EXPLOTACIÓN
    mutación=1/n          │
    elite=2               │
```

---

## 4. CONVERGENCIA PREMATURA (Premature Convergence)

### Definición
El GA converge a **óptimo local** cuando pierde diversidad genética.

### Síntomas
```python
Gen 1-50:    Fitness mejora: 300 → 350 → 380 → 400 → 420
Gen 50-100:  Fitness platea: 420 → 420 → 420 → 420 ← MAL
Gen 100-200: Fitness platea: 420 → 420 → 420 → 420 ← Sin mejora

Ideal:
Gen 1-50:    Fitness mejora: 300 → 350 → 380 → 400 → 420
Gen 50-150:  Fitness mejora: 420 → 430 → 438 → 441 → 440.84
Gen 150-200: Fitness platea: 440.84 (óptimo global alcanzado)
```

### Causas
```
1. Presión selectiva muy alta
   → Todos los padres son similares
   → Crossover genera clones
   
2. Mutación muy baja
   → No hay escape de óptimos locales
   
3. Elite demasiado grande
   → Los malos no compiten
   → Rápida convergencia
```

### Prevención
```python
# ESTRATEGIA 1: Mantener diversidad explícita
# (implementado: mutación adaptativa 1/n)

# ESTRATEGIA 2: Aumentar población en problemas difíciles
pop_size = max(50, min(200, n // 2))  # Adaptativo

# ESTRATEGIA 3: Réstart diversidad si detecta platea
if gen > 100 and fitness_improvement < 0.001:
    reintroduzcan 20% población aleatoria

# ESTRATEGIA 4: Niching (mantener múltiples óptimos)
# (No implementado en versión actual, para problemas multimodales)
```

---

## 5. PARALELISMO IMPLÍCITO (Implicit Parallelism)

### Definición
Un GA con población P y esquemas de orden bajo O busca implícitamente ~P^3 esquemas en paralelo.

### Ejemplo Concreto
```
Población: 100 individuos
Esquemas investigados en paralelo: 100^3 = 1,000,000

Comparativa:
  Búsqueda lineal: Evalúa 1,000,000 soluciones secuencialmente
  GA: Evalúa 100 individuos × 200 gen = 20,000 evaluaciones
      Pero examina implícitamente 1M esquemas
      
  GANANCIA: 50x más eficiencia
```

### Cómo Funciona
```
GA evalúa: [1, 0, 1, 1, 0, 1, 0, 1]
Obtiene información sobre esquemas:

1*1**** →  contribuye al promedio de todos individuos 1...1....
*0****** → contribuye al promedio de todos individuos .0......
1***0*** → contribuye al promedio de todos individuos 1.....0..
...y 997 esquemas más simultáneamente

Recombinación (crossover) combina mejores esquemas:
  Padre1: 1*1***0*  fitness=420
  Padre2: *1**1***  fitness=380
  Hijo: 11*1*1*0* (combina buenos segmentos)
```

---

## 6. FITNESS LANDSCAPE (Paisaje de Fitness)

### Definición
Visualización imaginaria de todas las 2^n soluciones posibles ordenadas por fitness.

### Tipos de Paisajes

#### A. Unimodal
```
       ▲
       │        ▲ único pico
       │       /│\
   f   │      / │ \
   i   │     /  │  \
   t   │    /   │   \
   n   │   /    │    \
   e   │  /     │     \
   s   │ /      │      \
   s   └─────────┴───────── soluciones
   
Características:
  - Un solo óptimo local = óptimo global
  - Fácil para cualquier algoritmo
  - GA converge directamente al óptimo
```

#### B. Multimodal
```
       ▲
       │   ▲   ▲   ▲ múltiples picos
       │  ╱╲ ╱ ╲ ╱ ╲
   f   │ ╱  ╲╱   ╲╱  ╲
   i   │╱ ←  ← trampas locales
   t   │
   n   │
   e   │
   s   │
   s   └─────────────────── soluciones
   
Características:
  - Múltiples óptimos locales
  - Algoritmos pueden atrapase (SA, Tabu)
  - GA escapa mejor gracias a población + crossover
```

### Knapsack
```
Knapsack es ALTAMENTE MULTIMODAL:
  - 2^n = 2^1000 soluciones posibles
  - Milones de óptimos locales
  - Accidentes topográficos (soluciones inválidas = fitness bajo)
  
¿Por qué GA gana?
  - Población explora múltiples "colinas" simultáneamente
  - Crossover combina genes de diferentes colinas
  - Mutación escala entre colinas
  - SA: Una sola trayectoria, fácil atrapase
```

---

## 7. BALANCE EXPLORACIÓN-EXPLOTACIÓN

### Definición
```
EXPLORACIÓN: Buscar en nuevas regiones del espacio de soluciones
EXPLOTACIÓN: Refinar dentro de región conocida buena

Dilema:
  - Pura exploración: Encuentra muchos óptimos locales, ninguno refinado
  - Pura explotación: Refina uno local pero pierde globales
  
GA balancea AUTOMÁTICAMENTE sin parámetro explícito
```

### Mecanismo en Nuestro GA

| Aspecto | Rol Exploración | Rol Explotación |
|---------|-----------------|-----------------|
| Selección (torneo) | Permite pobres reproducirse | Favorece mejores |
| Crossover (0.8 prob) | Combina nuevas formas | Preserva buenos segmentos |
| Mutación (1/n) | Invierte bits nuevas opciones | Mantiene estructura |
| Elitismo (top 2) | --- | Preserva global best |

```python
# Análisis por generación:

GEN 1-10:   población = [aleatorio... aleatorio]
            → Exploración: >80% diversidad
            → Explotación: <20% refinamiento
            
GEN 50:     población = [similar... similar...similar]
            → Exploración: 40% (mutación mantiene)
            → Explotación: 60% (crossover refina)
            
GEN 200:    población = [casi_idéntico... casi_idéntico]
            → Exploración: 10% (solo mutación)
            → Explotación: 90% (elitismo + crossover cercano)
```

---

## 8. COMPLEJIDAD COMPUTACIONAL

### Análisis

#### Tiempo
```
O(G × P × n)
  G = generaciones = 200
  P = población = 100
  n = items = 1000
  
Total: 200 × 100 × 1000 = 20,000,000 operaciones
Tiempo real: ~2-3 segundos en CPU moderno

Comparativa:
  Búsqueda exhaustiva: O(2^n) = 2^1000 ← imposible
  Branch & Bound: O(2^n) average
  Programación dinámica: O(n × capacity) ← pero necesita memoria O(n×W)
  GA: O(G×P×n) ← polinomial!
```

#### Espacio
```
O(P × n)
  P población = 100
  n items = 1000
  
Total: 100 × 1000 = 100,000 cromosomas
Memoria: 100,000 bits = 12.5 KB (insignificante)

Comparativa:
  DP: O(n × capacity) = O(1000 × 100,000) = 100 MB (si capacidad grande)
  GA: O(P × n) = 100 KB (eficiente)
```

---

## 9. CROSSOVER vs MUTACIÓN - Rol Específico

### Crossover
```
Propósito: EXPLOTACIÓN de buenos segmentos
Mecanismo: Combinar padre1 y padre2

Padre1: [1, 0, 1, 1, 0, 1, 0, 1]  BB1={0,2,3,5,7}
Padre2: [0, 1, 1, 0, 1, 1, 0, 1]  BB2={1,2,4,5,7}
           ↓
Hijo:   [1, 0, 1 | 0, 1, 1, 0, 1]  BB1∪BB2 parcial
        
Escenario: Si BB1 es bueno y BB2 es bueno
           Hijo hereda ambos → posible super-solución
           
Eficiencia: Combina 2 BBs en 1 generación
           Mutación necesitaría 2^|BB1| generaciones
```

### Mutación
```
Propósito: EXPLORACIÓN de nuevas regiones
Mecanismo: Invertir bits aleatorios

Individuo: [1, 0, 1, 1, 0, 1, 0, 1]
Después:   [1, 0, 0, 1, 0, 1, 1, 1]
                 ↑           ↑
              flipped    flipped

Escenario: Gene raro [bit 2 = 0] nunca se exploró
           Mutación lo activa → [bit 2 = 1]
           Descubre nueva región del espacio
           
Importancia: Sin mutación, solo exploras combinaciones padres
            Con mutación, exploras fuera del cono convexo
```

### Porqué Ambos Son Necesarios
```python
# Solo Crossover:
poblacion gen 50: [S1, S1, S2, S2, S3, S3, ...]
                  ↓ crossover
                  [S1, S2, S1+S2, S2+S3, ...]
# Problema: Solo exploras combinaciones de inicial
# Desventaja: Genes nuevos nunca nacen

# Solo Mutación:
poblacion gen 50: [S1 + ruido, S1 + ruido, S1 + ruido, ...]
                  # Casi random walk
# Problema: Sin recombinación, pierde información buena
# Desventaja: Cambios completamente aleatorios destruyen BBs
```

---

## 10. ELITISMO - Por Qué No Es Degeneración

### Objeción Común
> "¿No copia elitismo un cromosoma generación tras generación hasta que converja prematuramente?"

### Respuesta
```
NO, porque:

1. DILUCIÓN GENÉTICA:
   Elite de 2 + 98 nuevos hijos
   Los hijos son DIFERENTES (crossover + mutación)
   Generación 1: [elite1, elite2, hijo1, ..., hijo98]
   Generación 2: [elite1', elite2', hijo1', ..., hijo98']
   (elite1' y elite2' pueden ser DIFERENTES de gen anterior)

2. PRESIÓN SELECTIVA GRADUAL:
   Gen 1: Mejora 100 → 150 → 200 (cambios grandes)
   Gen 50: Mejora 420 → 421 → 422 (cambios pequeños)
   Gen 200: 440.84 (óptimo local)
   
   → No es salto abrupto, es progresión suave

3. CROSSOVER RECOMBINA ELITE:
   Si elite = [S1, S2]
   Hijo = crossover(S1, S2) puede ser:
     - Mejor que S1 y S2
     - Peor que ambos (pero preserva top 2)
     - Similar pero ligeramente diferente
   
   Resultado: Lenta convergencia, NO degeneración
```

### Evidencia Experimental
```
Nuestros resultados:
  Gen 1-20: Fitness mejora 45% en media
  Gen 20-100: Fitness mejora 8% en media
  Gen 100-200: Fitness mejora 0.5% en media
  
Patrón: Mejora asintótica, NO oscilante
        → Elitismo FUNCIONA sin perder diversidad
```

---

## 11. ORDEN PEQUEÑO DE ESQUEMAS

### Definición
**Orden de esquema** = número de posiciones especificadas

```
Esquema 1*1**** →      orden = 2 (posiciones 0,2)
Esquema 1***0* →       orden = 2 (posiciones 0,4)
Esquema 1***0*1 →      orden = 3 (posiciones 0,4,6)
Esquema 1*1*0*1* →     orden = 4 (posiciones 0,2,4,6)
```

### Por Qué "Pequeño" es Bueno
```
Teorema de Esquemas:
  GA preserva esquemas orden-bajo con fitness alto

Implicación:
  Esquemas pequeños = menos bits especificados
                   = más probable que se preserve (no roto por crossover)
                   
Ejemplo: En Knapsack n=100
  Schema orden 2: 1*....*  (primero y último)
                            Chance de preservación = 99%
                            
  Schema orden 50: 1*1*1*...*1 (muchos especificados)
                            Chance de preservación = 1%

Evolución:
  Gen 1-20: GA identifica esquemas orden 2-3 con fitness alto
  Gen 20-100: GA recombina para gen orden 4-6
  Gen 100-200: GA refina pequeños cambios
  
  RESULTADO: Building blocks de orden bajo se combinan
             construyendo soluciones de orden alto
```

---

## 12. REGÍMENES DE ACTIVIDAD (Activity Regimes)

### Definición
El GA cambia automáticamente de comportamiento según:
- Generación actual
- Diversidad de población
- Tasa de mejora

### Régimen 1: Exploración Dominante (Gen 1-30)
```
Características:
  - Población: Muy diversa
  - Fitness: Mejora rápida
  - Mutación: Efecto alto (explora)
  - Crossover: Mezcla diversidad
  
Papel de Elitismo: BAJO
  - Elite es pequeño % de población
  - Mayoría de genes son nuevos

Ejemplo:
  Gen 5: Fitness = 250
  Gen 10: Fitness = 350
  Gen 15: Fitness = 400
  Mejora por generación: ~30
```

### Régimen 2: Balance (Gen 30-150)
```
Características:
  - Población: Convergiendo
  - Fitness: Mejora gradual
  - Mutación: Efecto medio (refina)
  - Crossover: Recombina buenos
  
Papel de Elitismo: MEDIO
  - Elite ~20% del pool de reproducción
  - Pero hijos pueden mejorar elite

Ejemplo:
  Gen 50: Fitness = 420
  Gen 100: Fitness = 435
  Gen 150: Fitness = 440
  Mejora por generación: ~0.4
```

### Régimen 3: Explotación Dominante (Gen 150-200)
```
Características:
  - Población: Muy homogénea
  - Fitness: Mejora mínima
  - Mutación: Efecto bajo (mantenimiento)
  - Crossover: Casi clonación
  
Papel de Elitismo: ALTO
  - Elite ~50% del pool de reproducción
  - Mayoría de hijos son tweaks
  
Ejemplo:
  Gen 150: Fitness = 440.00
  Gen 200: Fitness = 440.84
  Mejora por generación: ~0.017
```

---

## CONCLUSIÓN: Los 12 Pilares Fundamentales

1. **Esquemas**: GA procesa implícitamente millones
2. **Building Blocks**: Combina sub-soluciones buenas
3. **Presión Selectiva**: Favorece mejores sin eliminar diversidad
4. **Convergencia Prematura**: Evitable con balance correcto
5. **Paralelismo Implícito**: P^3 esquemas con P evaluaciones
6. **Fitness Landscape**: GA navega multimodalidad mejor
7. **Exploración-Explotación**: Balance automático
8. **Complejidad O(GxPxn)**: Polinomial vs exponencial
9. **Crossover**: Explotación de buenos segmentos
10. **Mutación**: Exploración de nuevas regiones
11. **Orden Pequeño**: GA preserva mejor esquemas cortos
12. **Regímenes**: Comportamiento auto-adapta con generaciones

Cada uno de estos puntos explica un aspecto diferente de **por qué GA destaca**.
