# EXPLICACIÓN PROFUNDA DEL CÓDIGO GA: Línea por Línea

## Introducción

Este documento explica cada sección crítica del código GA implementado, con énfasis en **por qué** cada decisión de diseño fue hecha de esa manera.

---

## 1. CLASE INDIVIDUO - Representación del Cromosoma

### 1.1 Definición

```python
@dataclass
class Individuo:
    """Representa un cromosoma (solución) en la población."""
    genes: np.ndarray  # Vector binario [0,1,0,1,...]
    fitness: float = None
```

**¿Por qué `@dataclass`?**
- Reduce boilerplate (no necesita `__init__`)
- Genera automáticamente `__repr__` para debugging
- Mejora legibilidad del código

**¿Por qué `genes` es `np.ndarray`?**
- NumPy es 100x más rápido que listas Python para operaciones vectoriales
- Optimización crítica porque evaluamos población completa ~20,000 veces

### 1.2 Método Evaluar - La Función de Fitness

```python
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
```

#### Análisis Línea a Línea

**Línea 1-2: Cálculo de Peso y Beneficio**
```python
peso_total = np.sum(self.genes * pesos)       # Vector multiplication
beneficio_total = np.sum(self.genes * beneficios)
```

**Operación en detalle:**
```
genes:       [1, 0, 1, 1, 0]
pesos:       [5, 10, 3, 8, 2]
             ↓ Multiplicación elemento a elemento
producto:    [5, 0, 3, 8, 0]
             ↓ Suma
peso_total:  16
```

**¿Por qué vectorización?**
- Operación: O(n) con NumPy = 1 microsegundo
- Con Python puro: 100 microsegundos
- En 20,000 evaluaciones: diferencia de 2 segundos

**Línea 3-6: Penalización Cuadrática**
```python
if peso_total > capacidad:
    exceso = peso_total - capacidad
    self.fitness = beneficio_total - penalizacion * (exceso ** 2)
```

**¿Por qué penalización cuadrática y NO lineal?**

Comparativa:
```
Penalización lineal (λ × exceso):
  Exceso = 1: Penalidad = 1000
  Exceso = 10: Penalidad = 10,000
  Ratio: 10x

Penalización cuadrática (λ × exceso²):
  Exceso = 1: Penalidad = 1,000
  Exceso = 10: Penalidad = 100,000
  Ratio: 100x
  
  → Desalienta FUERTEMENTE soluciones inválidas
  → Pero no prohibe exploración inicial
```

**¿Cuál es el valor λ = 1000?**
```
Beneficio máximo típico: ~500
Penalización máxima por violación pequeña: 1000 × 1² = 1000

Efecto: 1 kg de exceso = perder TODA la solución
        Esto fuerza al GA a respetar capacidad
```

**Línea 7: Fitness válido**
```python
else:
    self.fitness = beneficio_total  # Si es válido, no hay penalización
```

---

## 2. CLASE AlgoritmoGeneticoKnapsack - El Motor GA

### 2.1 Constructor - Configuración

```python
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
```

#### ¿Por qué estos valores por defecto?

| Parámetro | Default | Rango Típico | Justificación |
|-----------|---------|--------------|---------------|
| `tamaño_poblacion` | 100 | 30-200 | Balance exploración/explotación |
| `generaciones` | 200 | 50-500 | Converge típicamente en gen 20-70 |
| `prob_crossover` | 0.8 | 0.6-0.95 | Alta recombinación recomendada |
| `prob_mutacion` | 1/n | 1/(2n)-5/n | Baja tasa previene desorden |

**¿Por qué `prob_mutacion = 1/n` (adaptativa)?**

```python
n = 100 items
prob_mutacion = 1/100 = 0.01 = 1%

Interpretación:
- En cada individuo, ~1 bit se invierte (en promedio)
- Mantiene "recambio genético" bajo pero constante
- Cuando n crece, tasa decrece → menos caos en problemas grandes

Comparativa:
  Tasa fija (0.01): Funciona bien para n=50, malo para n=1000
  Tasa adaptativa (1/n): Óptima para cualquier n
```

### 2.2 Inicializar Población

```python
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
```

**¿Por qué aleatoria?**
```
Alternativa 1: Todos iguales
  → Mismo fitness para todos
  → Sin diversidad para seleccionar
  → GA falla

Alternativa 2: Greedy (items con mejor ratio)
  → Podría dejar fuera buenas soluciones
  → Pierde capacidad de exploración
  
Solución: Aleatorio
  → Distribuye soluciones en el espacio
  → Algunos buenos, algunos malos
  → GA mejora progresivamente
```

**Generación aleatoria:**
```python
genes = np.random.randint(0, 2, size=self.n)
# Produce: [0, 1, 0, 0, 1, 1, 0, ...] ← cada bit 50% probabilidad
```

### 2.3 Selección por Torneo

```python
def _seleccion_torneo(self, poblacion: List[Individuo], 
                      tamaño_torneo: int = 3) -> Individuo:
    """Selecciona un individuo mediante torneo."""
    candidatos = random.sample(poblacion, k=tamaño_torneo)
    return max(candidatos, key=lambda x: x.fitness)
```

#### ¿Por qué Torneo y no Ruleta (Roulette Wheel)?

**Ruleta (idea alternativa):**
```python
# Fitness proporcional
probabilidades = [ind.fitness / sum(fitness) for ind in poblacion]
seleccionado = random.choices(poblacion, weights=probabilidades)
```

**Problemas con Ruleta:**
```
Si fitness range = [100, 101, 102, 103, 104]:
  - Diferencias pequeñas
  - Selección casi aleatoria
  - Baja presión selectiva

Si fitness range = [100, 1000]:
  - Un individuo domina
  - Convergencia prematura
  - Pérdida de diversidad
```

**Ventajas de Torneo:**
```python
# Tamaño torneo = 3
3 individuos: [fitness=440, fitness=350, fitness=380]
              ↓
Ganador: 440 ✓

3 individuos: [fitness=350, fitness=340, fitness=345]
              ↓
Ganador: 350 ✓

Presión selectiva: Controlada por tamaño_torneo
  - Tamaño pequeño (2): Presión baja, exploración
  - Tamaño grande (10): Presión alta, explotación
```

**Pseudocódigo:**
```
1. Muestrear 3 individuos al azar (sin reemplazo)
2. Retornar el con mayor fitness
3. Ese individuo puede reproducirse

Efecto: Mejores individuos tienen MÁS oportunidades
        Pero aún hay algo de chance para mediocres
        → Balance exploración-explotación
```

### 2.4 Crossover - Recombinación de Padres

```python
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
```

#### Explicación Detallada

**Línea 1: Probabilidad de NO hacer crossover**
```python
if random.random() > self.prob_crossover:
    return Individuo(padre1.genes.copy())
    
# Si prob_crossover = 0.8:
#   random() genera [0, 1)
#   random() > 0.8  →  Ocurre 20% de veces
#   → 80% de veces hace crossover, 20% copia padre

# ¿Por qué?
# Algunos hijos buenos pueden preservarse sin cambiar
# Previene destruir soluciones excelentes
```

**Línea 2-6: Crossover de Punto Simple**

```python
punto_corte = random.randint(1, self.n - 1)
# Genera número entre 1 e n-1 (nunca 0 ni n)

# Ejemplo: n=8, punto_corte=3
genes_hijo = np.concatenate([
    padre1.genes[:3],      # [1, 0, 1] + índices 0,1,2
    padre2.genes[3:]       # [0, 1, 0, 1, 1] + índices 3,4,5,6,7
])
# Resultado: [1, 0, 1 | 0, 1, 0, 1, 1]
```

#### ¿Por qué Punto Simple y no Otros Tipos?

**Alternativa 1: Crossover Uniforme**
```python
# Cada bit 50% padre1, 50% padre2
for i in range(n):
    if random() < 0.5:
        hijo[i] = padre1[i]
    else:
        hijo[i] = padre2[i]

Ventaja: Mayor exploración
Desventaja: Puede destruir buenos esquemas
```

**Alternativa 2: Crossover de Dos Puntos**
```python
# Dos puntos de corte
punto1 = randint(1, n-2)
punto2 = randint(punto1+1, n-1)

hijo = padre1[:punto1] + padre2[punto1:punto2] + padre1[punto2:]

Ventaja: Mayor segmentación
Desventaja: Más complejo, no es necesario para Knapsack
```

**¿Por qué Punto Simple es mejor para Knapsack?**

```
Teoría de Esquemas (Holland):
  Schema de alta calidad (bajo orden) se preserva mejor
  con punto simple que uniforme.
  
Ejemplo:
  Schema: 1*1***** (primeros 3 bits importantes)
  
  Con punto simple:
    Punto 1-2: 90% chance de preservar 1*1
    
  Con uniforme:
    Cada bit 50% chance: solo 12.5% chance de preservar 1*1
    
  → Punto simple preserva mejores patrones
```

### 2.5 Mutación - Introducir Diversidad

```python
def _mutar(self, individuo: Individuo) -> Individuo:
    """
    Mutación: invierte bits con probabilidad prob_mutacion.
    """
    genes_mutados = individuo.genes.copy()
    for i in range(self.n):
        if random.random() < self.prob_mutacion:
            genes_mutados[i] = 1 - genes_mutados[i]
    return Individuo(genes_mutados)
```

#### Análisis Línea por Línea

**Línea 1: Por qué copiar?**
```python
genes_mutados = individuo.genes.copy()
# NO modificar in-place:
#   - El padre podría volver a usarse
#   - Cambios globales inesperados
#   - Bug potencial

# Con copy: nuevo objeto independiente
```

**Línea 2-3: Flip Bits**
```python
if random.random() < self.prob_mutacion:
    genes_mutados[i] = 1 - genes_mutados[i]
    # 1 - 1 = 0
    # 1 - 0 = 1
    # Invierte el bit
```

**¿Por qué `1 - bit` en lugar de `bit XOR 1`?**
```python
# Ambos funcionan igual:
bit_new = 1 - bit        # 1 - 0 = 1, 1 - 1 = 0
bit_new = bit ^ 1        # 0 ^ 1 = 1, 1 ^ 1 = 0

# 1 - bit es más legible
```

#### ¿Por qué Mutación es Crítica?

```
Sin mutación:
  Población converge a pequeña región
  Genes útiles pero raros desaparecen
  
Con mutación baja (prob_mutacion = 0.001):
  Lenta exploración de nuevas soluciones
  Podría perder optimales
  
Con mutación alta (prob_mutacion = 0.5):
  Caos total
  Destroza soluciones buenas
  
Con prob_mutacion = 1/n:
  ~1 bit por individuo se invierte
  Balance óptimo: pequeños cambios exploran
  Pero mantiene estructura buena
```

**Analogía biológica:**
```
Crossover = reproducción (combina genes existentes)
Mutación = cambios genéticos (crea genes nuevos)

Sin ambos:
  - Solo crossover: se combinan genes pero no hay nuevos → estancamiento
  - Solo mutación: puro azar → no hay evolución direccional

Con ambos:
  - Crossover explota lo bueno conocido
  - Mutación explora lo desconocido
  - Balance → convergencia a óptimo
```

### 2.6 Elitismo - Preservar lo Mejor

```python
def _aplicar_elitismo(self, poblacion: List[Individuo], 
                      elite_size: int = 2) -> List[Individuo]:
    """Conserva los mejores individuos para la siguiente generación."""
    poblacion_ordenada = sorted(poblacion, 
                                key=lambda x: x.fitness, 
                                reverse=True)
    return poblacion_ordenada[:elite_size]
```

#### ¿Por Qué Elitismo?

**Sin elitismo:**
```
Generación t:
  Mejor fitness: 440.84
  
Generación t+1:
  Mejor fitness: 438.00  ← Regresión!
  
Explicación:
  - Todos los hijos son nuevos
  - El mejor cromosoma de t desaparece por azar
  - GA "olvida" soluciones buenas
```

**Con elitismo (elite_size=2):**
```
Generación t:
  Top 2: [440.84, 439.50]
  
Generación t+1:
  nueva_pop = [440.84, 439.50] + 98 hijos nuevos
  Mejor fitness: ≥ 440.84  ← Garantizado no empeora
  
Efecto:
  - Monotonicidad: mejor fitness nunca decrece
  - Convergencia garantizada (hacia un óptimo local)
```

**Línea 1: Ordenar por Fitness**
```python
sorted(poblacion, key=lambda x: x.fitness, reverse=True)
# reverse=True: orden descendente (mejores primero)
```

**Línea 2: Tomar Top-2**
```python
return poblacion_ordenada[:elite_size]  # elite_size = 2
# Retorna: [población[0], población[1]] = los 2 mejores
```

**¿Por qué elite_size=2 y no 1 o 5?**

```
elite_size = 1:
  - Solo 1 mejor se copia
  - Poco "patrimonio genético" se transmite
  - Pérdida de diversidad

elite_size = 2:
  - 2 mejores se copian
  - Diversidad en elite
  - Recombinación potencial de 2 buenos
  - Recomendado para poblaciones ~100

elite_size = 5:
  - Demasiado alto
  - Poco espacio para nuevos individuos (95 hijos vs 105 elite+hijos)
  - Convergencia prematura
```

### 2.7 Algoritmo Principal - `resolver()`

```python
def resolver(self) -> Tuple[np.ndarray, float, float]:
    """Ejecuta el algoritmo genético."""
    inicio = time.time()
    
    poblacion = self._inicializar_poblacion()
    self.mejor_individuo = max(poblacion, key=lambda x: x.fitness)
    
    for gen in range(self.generaciones):
        # 1. Evaluar y actualizar mejor
        mejor_gen = max(poblacion, key=lambda x: x.fitness)
        self.mejor_fitness_por_gen.append(mejor_gen.fitness)
        
        if mejor_gen.fitness > self.mejor_individuo.fitness:
            self.mejor_individuo = Individuo(mejor_gen.genes.copy())
            self.mejor_individuo.fitness = mejor_gen.fitness
        
        # 2. Aplicar elitismo
        nueva_poblacion = self._aplicar_elitismo(poblacion, elite_size=2)
        
        # 3. Generar offspring
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
```

#### Flujo Paso a Paso

**Paso 1: Inicialización**
```python
poblacion = self._inicializar_poblacion()  # 100 individuos aleatorios
self.mejor_individuo = max(poblacion, ...)  # Track global best
```

**Paso 2: Loop Generacional**
```python
for gen in range(self.generaciones):  # 200 veces
    # Cada iteración = 1 generación
```

**Paso 3: Evaluación y Tracking**
```python
mejor_gen = max(poblacion, key=lambda x: x.fitness)
self.mejor_fitness_por_gen.append(mejor_gen.fitness)  # Historial
```

**Paso 4: Actualizar Mejor Global**
```python
if mejor_gen.fitness > self.mejor_individuo.fitness:
    self.mejor_individuo = Individuo(mejor_gen.genes.copy())
    # ¿Por qué copiar?
    # - El individuo podría cambiar en próximas generaciones
    # - Necesitamos snapshot inmutable del mejor encontrado
```

**Paso 5: Elitismo**
```python
nueva_poblacion = self._aplicar_elitismo(poblacion, elite_size=2)
# nueva_poblacion = [mejor, segundo_mejor]
# Largo: 2
```

**Paso 6: Generar Offspring hasta llenar población**
```python
while len(nueva_poblacion) < self.tamaño_poblacion:  # Mientras < 100
    padre1 = self._seleccion_torneo(poblacion)       # Seleccionar
    padre2 = self._seleccion_torneo(poblacion)       # Seleccionar
    hijo = self._crossover(padre1, padre2)           # Combinar
    hijo = self._mutar(hijo)                         # Variar
    hijo.evaluar(...)                                # Evaluar
    nueva_poblacion.append(hijo)                     # Agregar
```

**Paso 7: Reemplazar Población**
```python
poblacion = nueva_poblacion[:self.tamaño_poblacion]
# Usa [:] por seguridad (aunque should be igual)
# Pasa a próxima generación
```

#### Diagrama de Flujo

```
GEN 1:
  Población: 100 aleatorios
  Evaluar
  Mejores 2 preservados
  98 hijos generados
  Nueva población: 100
    ↓
GEN 2:
  Población: (2 anteriores + 98 nuevos)
  Evaluar
  Mejores 2 preservados
  98 hijos generados
  Nueva población: 100
    ↓
GEN 3:
  ...
    ↓
GEN 200:
  Terminar, retornar mejor
```

---

## 3. CÓMO CREAR HIJOS - ESPECIFICACIÓN DETALLADA

### 3.1 Proceso Completo

```
CREAR HIJO = Seleccionar → Combinar → Mutar → Evaluar

PASO 1: SELECCIONAR 2 PADRES
  padre1 = torneo(población) ← Better chance to reproduce
  padre2 = torneo(población)

  Ejemplo:
  padre1: [1, 0, 1, 1, 0, 1, 0, 1]  fitness=440
  padre2: [0, 1, 1, 0, 1, 1, 0, 1]  fitness=420

PASO 2: CROSSOVER (80% probabilidad)
  if random() < 0.8:
    punto_corte = randint(1, n-1) = 3
    hijo = padre1[:3] + padre2[3:]
         = [1, 0, 1] + [0, 1, 1, 0, 1]
         = [1, 0, 1, 0, 1, 1, 0, 1]
  else:
    hijo = padre1.copy() = [1, 0, 1, 1, 0, 1, 0, 1]

PASO 3: MUTACIÓN (1% probabilidad por bit)
  for each bit:
    if random() < 0.01:
      flip bit
  
  Ejemplo (suerte: bits 2 y 6 se invierten):
  Antes: [1, 0, 1, 0, 1, 1, 0, 1]
  Después: [1, 0, 0, 0, 1, 1, 1, 1]
                ↑        ↑
             flipped  flipped

PASO 4: EVALUAR HIJO
  peso_total = 5+3+8+1+10+15 = ... (solo bits=1)
  beneficio = 20+15+25+...
  if peso > capacidad:
    fitness = beneficio - 1000*(peso-cap)²
  else:
    fitness = beneficio
```

### 3.2 ¿Por Qué Este Orden Exacto?

**Orden: Seleccionar → Combinar → Mutar → Evaluar**

```
NO hacer:
  Seleccionar → Evaluar → Combinar → Mutar → Evaluar
  
Problema:
  - Padres evaluados antes de crossover (innecesario)
  - Hijo evaluado 2 veces
  - Costo computacional 2x
  
HACER:
  Seleccionar → Combinar → Mutar → Evaluar
  
Ventaja:
  - Evaluamos solo una vez (eficiente)
  - Selección requiere fitness ya calculado (población vieja)
  - Hijo nuevo solo se evalúa después de creado
```

### 3.3 ¿Por Qué Fitness Después de Mutación?

**Pregunta**: ¿No deberías evaluar antes de mutar?

**Respuesta**: NO, por esto:

```python
# WRONG:
hijo = crossover(padre1, padre2)
hijo.evaluar()  # Evalúa versión pre-mutación
hijo = mutar(hijo)
# Ahora fitness es obsoleto! Debe re-evaluar

# RIGHT:
hijo = crossover(padre1, padre2)
hijo = mutar(hijo)
hijo.evaluar()  # Evalúa versión final
# Fitness es correcto, sin re-trabajo
```

---

## 4. PUNTOS CLAVE DEL ALGORITMO

### 4.1 Los 3 Pilares

#### 1. Selección (Presión)
```python
def _seleccion_torneo(self, poblacion, tamaño_torneo=3):
    candidatos = random.sample(poblacion, k=3)
    return max(candidatos, key=lambda x: x.fitness)
```

**Propósito**: Favorece individuos buenos
**Mecanismo**: Torneo → mejor gana
**Efecto**: Población converge lentamente hacia mejores regiones

#### 2. Crossover (Recombinación)
```python
punto_corte = random.randint(1, self.n - 1)
genes_hijo = np.concatenate([
    padre1.genes[:punto_corte],
    padre2.genes[punto_corte:]
])
```

**Propósito**: Combinar genes útiles
**Mecanismo**: Intercambiar segmentos
**Efecto**: Explotación de buenas soluciones encontradas

#### 3. Mutación (Exploración)
```python
if random.random() < self.prob_mutacion:
    genes_mutados[i] = 1 - genes_mutados[i]
```

**Propósito**: Introducir variación
**Mecanismo**: Flip bits aleatorios
**Efecto**: Exploración de nuevas regiones del espacio

### 4.2 Balance Automático

```python
# En GA NO hay parámetro "exploración vs explotación" explícito
# Se equilibran automáticamente:

GENERACIÓN 1-10:
  - Población diversa (100 aleatorios)
  - Mutación explora mucho
  - Crossover encuentra primeros buenos (presión suave)
  - → EXPLORACIÓN dominante

GENERACIÓN 10-50:
  - Población converge en región buena
  - Mutación mantiene diversidad
  - Crossover refina soluciones
  - → BALANCE

GENERACIÓN 50-200:
  - Población muy homogénea
  - Mutación explora periferia
  - Crossover refina minúsculas mejoras
  - Elitismo preserva global best
  - → EXPLOTACIÓN dominante

TODO AUTOMÁTICO SIN CAMBIAR PARÁMETROS
```

---

## 5. COMPARATIVA DE DISEÑOS ALTERNATIVOS

### 5.1 Población Inicial: Aleatoria vs Greedy vs Hibrida

```python
# OPCIÓN 1: ALEATORIA (actual)
genes = np.random.randint(0, 2, size=self.n)
# Ventaja: Diverso, sin sesgo
# Desventaja: Algunos muy malos

# OPCIÓN 2: GREEDY (items con mejor ratio)
ratios = beneficios / pesos
top_indices = argsort(ratios)[-tamaño_poblacion//2:]
for i in top_indices:
    genes[i] = 1
# Ventaja: Inicio prometedor
# Desventaja: Sesgo de convergencia prematura

# OPCIÓN 3: HIBRIDA
# 50% aleatorio + 50% greedy
# Ventaja: Balance
# Desventaja: Más complejo, sin ganancia significativa en GA

# RECOMENDACIÓN: ALEATORIA (simple, robusto, equilibrado)
```

### 5.2 Manejo de Capacidad: Penalización vs Reparación

```python
# OPCIÓN 1: PENALIZACIÓN (actual)
if peso_total > capacidad:
    fitness = beneficio - 1000 * (peso_total - capacidad)**2

# OPCIÓN 2: REPARACIÓN
def reparar(genes):
    while peso_total > capacidad:
        remover item con peor ratio beneficio/peso
    return genes_reparado

# OPCIÓN 3: RESTRICCIÓN DURA
def generar_vecino():
    while True:
        nuevo = mutar(individuo)
        if peso(nuevo) <= capacidad:
            return nuevo

# COMPARATIVA:
# Penalización: Explora soluciones inválidas (permite escape)
# Reparación: Garantiza factibilidad (pero limita exploración)
# Restricción: Nunca inválido (pero exploración severamente limitada)

# RECOMENDACIÓN: PENALIZACIÓN (balance exploración-explotación)
```

---

## 6. NÚMERO DE EVALUACIONES

```python
# Pregunta: ¿Cuántas evaluaciones en total?

poblacion = 100
generaciones = 200

Evaluación inicial: 100
Generación 1-200: 200 × 98 = 19,600 (98 hijos nuevos/gen, elite no se re-evalúan)
                         
TOTAL: 100 + 19,600 = 19,700 evaluaciones

Comparativa:
  Tabu Search: 500 iteraciones × 100 candidatos = 50,000 evaluaciones
  GA: 19,700 evaluaciones
  
GA es 2.5x más eficiente en evaluaciones
```

---

## CONCLUSIÓN

El código GA está diseñado con cada línea pensada estratégicamente para:

1. **Eficiencia**: NumPy vectorización, evaluación única por hijo
2. **Robustez**: Elitismo monótono, mutación adaptativa
3. **Balance**: Selección + Crossover + Mutación equilibrados
4. **Escalabilidad**: O(G×P×n), paralelizable
5. **Simplicidad**: Fácil de entender e implementar

Cada decisión tiene justificación teórica y experimental.
