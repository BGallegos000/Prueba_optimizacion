"""
Genera ENTREGA_FINAL.pdf.

Flujo:
1. Si existe un motor LaTeX local (pdflatex/xelatex/lualatex), compila ENTREGA_FINAL.tex.
2. Si no existe, crea un PDF equivalente con ReportLab para dejar la entrega lista.

El respaldo ReportLab existe porque este entorno no trae compilador LaTeX en PATH.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent
TEX_PATH = BASE_DIR / "ENTREGA_FINAL.tex"
PDF_PATH = BASE_DIR / "ENTREGA_FINAL.pdf"


def try_compile_latex() -> bool:
    """Compila con LaTeX si hay un motor instalado."""
    engine = next((cmd for cmd in ("pdflatex", "xelatex", "lualatex") if shutil.which(cmd)), None)
    if engine is None:
        return False

    cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", TEX_PATH.name]
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    return PDF_PATH.exists()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            alignment=TA_CENTER,
            spaceAfter=18,
            textColor=colors.HexColor("#1F4E79"),
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.3,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.0,
            leading=9.7,
            alignment=TA_LEFT,
        ),
        "table": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=8.7,
            alignment=TA_LEFT,
        ),
        "formula": ParagraphStyle(
            "Formula",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.3,
            leading=10.2,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=4,
            spaceAfter=7,
            textColor=colors.HexColor("#243447"),
        ),
    }


S = styles()


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def H1(text: str) -> Paragraph:
    return P(text, "h1")


def H2(text: str) -> Paragraph:
    return P(text, "h2")


def F(text: str) -> Preformatted:
    return Preformatted(text, S["formula"])


def cell(value) -> Paragraph:
    return Paragraph(str(value), S["table"])


def make_table(data, widths=None, font_size=7.2):
    rows = [[cell(v) for v in row] for row in data]
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("LEADING", (0, 0), (-1, -1), font_size + 1.2),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B7C7D4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def add_table(story, data, widths=None, font_size=7.2):
    story.append(make_table(data, widths, font_size))
    story.append(Spacer(1, 0.22 * cm))


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(2.0 * cm, 1.0 * cm, "Solemne IA Optimización 2026 - Algoritmo Genético")
    canvas.drawRightString(19.5 * cm, 1.0 * cm, f"Página {doc.page}")
    canvas.restoreState()


def build_story():
    story = []

    story.append(Spacer(1, 1.1 * cm))
    story.append(P("SOLEMNE IA", "title"))
    story.append(P("Ruteo y scheduling de camiones cisterna", "subtitle"))
    story.append(P("Solución autosuficiente mediante Algoritmo Genético", "subtitle"))
    story.append(Spacer(1, 2.2 * cm))
    add_table(
        story,
        [
            ["Campo", "Detalle"],
            ["Curso", "CINF105 Optimización"],
            ["Nombre", "______________________________"],
            ["NRC", "______________________________"],
            ["RUT", "______________________________"],
            ["Periodo", "Junio 2026"],
        ],
        widths=[4 * cm, 10 * cm],
        font_size=9,
    )
    story.append(PageBreak())

    story.append(H1("Resumen metodológico"))
    story.append(
        P(
            "Este informe responde directamente los cuatro puntos de la evaluación y usa un único enfoque: "
            "Algoritmo Genético (GA). La formulación matemática se presenta como el sistema de costos, "
            "restricciones y penalizaciones que evalúa el GA. No se usan métodos comparativos ni archivos "
            "externos para justificar la solución."
        )
    )
    story.append(
        F(
            "Cromosoma chi = (rutas por camión, producto por compartimento,\n"
            "                 volúmenes cargados, orden de carga en depósito)"
        )
    )

    story.append(H1("1. Modelamiento determinista"))
    story.append(P("Se considera el escenario normal s=1. El depósito es el nodo 0 y las estaciones son J={1,2,3,4}."))

    story.append(H2("a) Conjuntos y parámetros"))
    add_table(
        story,
        [
            ["Símbolo", "Descripción"],
            ["K={T1,T2}", "Conjunto de camiones."],
            ["C_k={C0,C1}", "Compartimentos del camión k."],
            ["P={R,D}", "Productos: Regular y Diésel."],
            ["N={0,1,2,3,4}", "Depósito y estaciones."],
            ["d_jp", "Demanda de estación j para producto p."],
            ["D_ij", "Distancia entre nodos i y j."],
            ["cap_kc", "Capacidad del compartimento c del camión k."],
            ["F_k", "Costo fijo por usar camión k."],
            ["[a_j,b_j]", "Ventana de tiempo de la estación j."],
            ["tau_ij=D_ij/60", "Tiempo de viaje en horas a 60 km/h."],
            ["h=30 min", "Tiempo de servicio en estación."],
            ["Delta=0.30", "Máxima diferencia entre fill ratios."],
            ["alpha=2, beta=10", "Costo por km y penalización por litro no entregado."],
        ],
        widths=[4.2 * cm, 12.0 * cm],
    )

    story.append(H2("b) Variables de decisión"))
    add_table(
        story,
        [
            ["Variable", "Tipo", "Interpretación"],
            ["x_kij", "Binaria", "1 si camión k viaja directamente de i a j."],
            ["r_k", "Binaria", "1 si camión k se utiliza."],
            ["z_kj", "Binaria", "1 si camión k visita estación j."],
            ["y_kcp", "Binaria", "1 si compartimento c transporta producto p."],
            ["L_kc", "Continua", "Litros cargados inicialmente en compartimento c."],
            ["q_kjp", "Continua", "Litros de p entregados por k en j."],
            ["u_jp", "Continua", "Shortage: litros no entregados de p en j."],
            ["t_kj", "Continua", "Hora de inicio de servicio en estación j."],
            ["rho_kcm", "Continua", "Fill ratio después del evento m de la ruta."],
        ],
        widths=[3.0 * cm, 2.4 * cm, 10.8 * cm],
    )

    story.append(H2("c) Función objetivo"))
    story.append(P("El costo real de una solución factible incluye distancia, costos fijos y shortage:"))
    story.append(
        F(
            "C(chi) = 2 * sum_k sum_i sum_j D_ij x_kij\n"
            "       + sum_k F_k r_k\n"
            "       + 10 * sum_j sum_p u_jp"
        )
    )
    story.append(P("Como el GA puede generar soluciones intermedias infactibles, se minimiza un costo penalizado:"))
    story.append(
        F(
            "Phi(chi) = C(chi) + lambda1 V_flujo + lambda2 V_demanda\n"
            "         + lambda3 V_capacidad + lambda4 V_estabilidad\n"
            "         + lambda5 V_tiempo + lambda6 V_scheduling\n\n"
            "fitness(chi) = 1 / (1 + Phi(chi))"
        )
    )

    story.append(H2("d) Restricciones"))
    story.append(P("<b>Conservación de flujo en routing.</b> Si un camión visita una estación, debe entrar y salir una vez."))
    story.append(F("sum_{i != j} x_kij = z_kj,    sum_{i != j} x_kji = z_kj"))
    story.append(F("sum_j x_k0j = r_k,            sum_i x_ki0 = r_k"))
    story.append(P("<b>Satisfaccion de demanda con shortage.</b>"))
    story.append(F("sum_k q_kjp + u_jp = d_jp,    q_kjp <= d_jp z_kj,    u_jp >= 0"))
    story.append(P("<b>Compatibilidad compartimento-producto.</b>"))
    story.append(F("sum_p y_kcp <= 1,             q_kjp <= d_jp * sum_c y_kcp"))
    story.append(P("<b>Capacidad de cada compartimento.</b>"))
    story.append(F("0 <= L_kc <= cap_kc * sum_p y_kcp\nsum_j q_kjp <= sum_c L_kc y_kcp"))
    story.append(P("<b>Estabilidad de carga.</b>"))
    story.append(F("rho_kcm = V_kcm / cap_kc\n|rho_kC0m - rho_kC1m| <= 0.30"))
    story.append(P("<b>Ventanas de tiempo.</b>"))
    story.append(F("t_ki + h + tau_ij <= t_kj + M(1 - x_kij)\na_j z_kj <= t_kj <= b_j + M(1 - z_kj)"))

    story.append(H1("2. Scheduling de carga en el depósito"))
    story.append(H2("a) Cálculo de tiempos de carga"))
    add_table(
        story,
        [
            ["Operación", "Producto", "Volumen (L)", "Tasa (L/min)", "Tiempo total"],
            ["T1-C0", "Regular", "5000", "500", "5000/500 + 5 = 15.0 min"],
            ["T1-C1", "Diésel", "5000", "400", "5000/400 + 5 = 17.5 min"],
            ["T2-C0", "Diésel", "4000", "400", "4000/400 + 5 = 15.0 min"],
            ["T2-C1", "Regular", "3500", "500", "3500/500 + 5 = 12.0 min"],
        ],
        widths=[2.8 * cm, 2.8 * cm, 2.7 * cm, 3.0 * cm, 4.9 * cm],
    )
    story.append(F("p_T1,C0=15; p_T1,C1=17.5; p_T2,C0=15; p_T2,C1=12"))

    story.append(H2("b) Formulacion del scheduling"))
    story.append(P("Variables: s_i inicio de operación, p_i duración, B_i bahía requerida, Cmax makespan."))
    story.append(F("min Cmax\ns_i + p_i <= Cmax\ns_T1,C1 >= s_T1,C0 + 15\ns_T2,C1 >= s_T2,C0 + 15"))
    story.append(P("No solapamiento en la misma bahía para operaciones i y j:"))
    story.append(F("s_i + p_i <= s_j + M(1-y_ij)\ns_j + p_j <= s_i + M y_ij"))

    story.append(H2("c) Secuencia óptima y Gantt"))
    add_table(
        story,
        [
            ["Bahía", "Operación", "Inicio relativo", "Fin relativo"],
            ["Regular", "T1-C0", "0.0", "15.0"],
            ["Regular", "T2-C1", "15.0", "27.0"],
            ["Diésel", "T2-C0", "0.0", "15.0"],
            ["Diésel", "T1-C1", "15.0", "32.5"],
        ],
        widths=[3.2 * cm, 3.2 * cm, 4.0 * cm, 4.0 * cm],
    )
    story.append(P("El makespan mínimo es Cmax=32.5 minutos. Para que T1 salga a las 05:00, la carga debe comenzar a más tardar a las 04:27:30. T2 queda listo a las 04:54:30 y puede salir a las 05:30."))

    story.append(H1("3. Análisis de la solución propuesta"))
    add_table(
        story,
        [
            ["Camión", "Ruta", "C0", "C1", "Fill C0", "Fill C1"],
            ["T1", "D->1->3->D", "Regular", "Diésel", "62.5%", "71.4%"],
            ["T2", "D->2->4->D", "Diésel", "Regular", "66.7%", "38.9%"],
        ],
        widths=[2.0 * cm, 3.4 * cm, 2.4 * cm, 2.4 * cm, 2.5 * cm, 2.5 * cm],
    )

    story.append(H2("a) Verificación de factibilidad"))
    story.append(P("<b>Capacidad de compartimentos.</b> Los fill ratios declarados implican cargas de 5000 L Regular y 5000 L Diésel en T1; 4000 L Diésel y 3500 L Regular en T2."))
    add_table(
        story,
        [
            ["Camión", "Producto", "Carga", "Demanda ruta", "Shortage mínimo"],
            ["T1", "Regular", "5000", "3000+2500=5500", "500"],
            ["T1", "Diésel", "5000", "2000+3000=5000", "0"],
            ["T2", "Diésel", "4000", "1500+2500=4000", "0"],
            ["T2", "Regular", "3500", "4000+1000=5000", "1500"],
        ],
        widths=[2.1 * cm, 2.5 * cm, 2.4 * cm, 5.0 * cm, 3.2 * cm],
    )
    story.append(P("La afirmación shortage=0 es falsa: faltan al menos 2000 litros."))

    story.append(P("<b>Estabilidad de carga.</b>"))
    add_table(
        story,
        [
            ["T1 instante", "rho C0 Regular", "rho C1 Diésel", "Diferencia"],
            ["Salida depósito", "5000/8000=0.625", "5000/7000=0.714", "0.089"],
            ["Después estación 1", "2000/8000=0.250", "3000/7000=0.429", "0.179"],
            ["Después estación 3", "0.000", "0.000", "0.000"],
        ],
        widths=[4.2 * cm, 4.0 * cm, 4.0 * cm, 2.6 * cm],
    )
    add_table(
        story,
        [
            ["T2 instante", "rho C0 Diésel", "rho C1 Regular", "Diferencia"],
            ["Salida depósito", "4000/6000=0.667", "3500/9000=0.389", "0.278"],
            ["Después estación 2", "2500/6000=0.417", "0/9000=0.000", "0.417"],
            ["Después estación 4", "0.000", "0.000", "0.000"],
        ],
        widths=[4.2 * cm, 4.0 * cm, 4.0 * cm, 2.6 * cm],
    )
    story.append(P("T2 viola estabilidad porque 0.417 > 0.30 después de estación 2."))

    story.append(P("<b>Ventanas de tiempo.</b> A 60 km/h, 1 km equivale a 1 minuto."))
    add_table(
        story,
        [
            ["Camión", "Tramo", "Llegada sin espera", "Ventana"],
            ["T1", "Depósito -> 1", "05:20", "[06:00, 10:00]"],
            ["T1", "1 -> 3", "06:15", "[08:00, 14:00]"],
            ["T2", "Deposito -> 2", "06:05", "[07:00, 12:00]"],
            ["T2", "2 -> 4", "06:50", "[06:00, 11:00]"],
        ],
        widths=[2.4 * cm, 4.2 * cm, 4.2 * cm, 4.0 * cm],
    )
    story.append(P("Con espera, el servicio puede iniciar dentro de las ventanas; sin espera, hay llegadas tempranas. La solución ya es infactible por capacidad y estabilidad."))

    story.append(H2("b) Verificación del costo declarado"))
    story.append(F("T1: 20 + 25 + 15 = 60 km\nT2: 35 + 15 + 40 = 90 km\nDistancia total = 150 km; costo distancia = 2*150 = 300"))
    add_table(
        story,
        [
            ["Componente", "Cálculo", "Costo"],
            ["Distancia", "150*2", "300"],
            ["Costos fijos", "500+400", "900"],
            ["Shortage mínimo", "2000*10", "20000"],
            ["Total real mínimo", "", "21200"],
        ],
        widths=[5.5 * cm, 5.0 * cm, 3.0 * cm],
    )
    story.append(P("El costo declarado de 260 es incorrecto: omite costos fijos, subestima distancia y declara shortage cero."))

    story.append(H2("c) Mejora inicial y solución final encontrada por GA"))
    story.append(P("Como primer acercamiento, se mantiene T1 en D->1->3->D, se corrigen cargas y se cambia T2 a D->4->2->D. Esta solución es factible y reduce el costo, pero no es la mejor encontrada por el modelo."))
    add_table(
        story,
        [
            ["Camión", "Ruta inicial", "C0", "C1", "Carga C0", "Carga C1"],
            ["T1", "D->1->3->D", "Regular", "Diésel", "5500", "5000"],
            ["T2", "D->4->2->D", "Diésel", "Regular", "4000", "5000"],
        ],
        widths=[2.0 * cm, 3.4 * cm, 2.4 * cm, 2.4 * cm, 2.5 * cm, 2.5 * cm],
    )
    story.append(F("Primer acercamiento: distancia = 150 km\nCosto = 2*150 + 500 + 400 + 10*0 = 1200"))
    story.append(P("Luego se ejecuta el Algoritmo Genético. Al explorar particiones y órdenes de visita, el GA encuentra una solución factible de menor costo:"))
    add_table(
        story,
        [
            ["Camión", "Ruta GA", "C0", "C1", "Carga C0", "Carga C1"],
            ["T1", "D->1->2->4->D", "Regular", "Diésel", "8000", "6000"],
            ["T2", "D->3->D", "Diésel", "Regular", "3000", "2500"],
        ],
        widths=[2.0 * cm, 3.8 * cm, 2.2 * cm, 2.2 * cm, 2.5 * cm, 2.5 * cm],
    )
    add_table(
        story,
        [
            ["Camión e instante", "rho C0", "rho C1", "Diferencia"],
            ["T1 salida", "8000/8000=1.000", "6000/7000=0.857", "0.143"],
            ["T1 después estación 1", "5000/8000=0.625", "4000/7000=0.571", "0.054"],
            ["T1 después estación 2", "1000/8000=0.125", "2500/7000=0.357", "0.232"],
            ["T1 después estación 4", "0.000", "0.000", "0.000"],
            ["T2 salida", "3000/6000=0.500", "2500/9000=0.278", "0.222"],
            ["T2 después estación 3", "0.000", "0.000", "0.000"],
        ],
        widths=[5.0 * cm, 4.0 * cm, 4.0 * cm, 2.6 * cm],
    )
    add_table(
        story,
        [
            ["Camión", "Estación", "Llegada / servicio", "Cumple"],
            ["T1", "1", "llega 05:20, espera, sirve 06:00-06:30", "Sí"],
            ["T1", "2", "llega 06:40, espera, sirve 07:00-07:30", "Sí"],
            ["T1", "4", "llega 07:45, sirve 07:45-08:15", "Sí"],
            ["T2", "3", "llega 05:45, espera, sirve 08:00-08:30", "Sí"],
        ],
        widths=[2.2 * cm, 2.0 * cm, 8.0 * cm, 2.0 * cm],
    )
    story.append(F("Solución GA: distancia = 20 + 10 + 15 + 40 + 15 + 15 = 115 km\nCosto total = 2*115 + 500 + 400 + 10*0 = 1130"))
    story.append(P("La solución final adoptada es la del GA: mejora el primer acercamiento de 1200, elimina shortage y mantiene factibilidad de capacidad, estabilidad y ventanas de tiempo."))

    story.append(H1("4. Extensión estocástica"))
    story.append(P("La demanda real se modela con tres escenarios. Cuando el enunciado no modifica el Diésel de estación 3, se conserva el valor normal de 3000 L."))
    add_table(
        story,
        [
            ["Esc.", "Prob.", "E1 R", "E1 D", "E2 R", "E2 D", "E3 R", "E3 D", "E4 R/D"],
            ["s=1", "0.5", "3000", "2000", "4000", "1500", "2500", "3000", "1000/2500"],
            ["s=2", "0.3", "4500", "2800", "5500", "2000", "3500", "3000", "1000/2500"],
            ["s=3", "0.2", "2000", "1200", "3000", "1000", "1800", "3000", "1000/2500"],
        ],
        widths=[1.4 * cm, 1.5 * cm, 1.55 * cm, 1.55 * cm, 1.55 * cm, 1.55 * cm, 1.55 * cm, 1.55 * cm, 2.0 * cm],
        font_size=6.6,
    )

    story.append(H2("a) Modelo de dos etapas"))
    story.append(P("<b>Primera etapa:</b> activar camiones r_k, asignar productos a compartimentos y_kcp, definir estructura de rutas x_kij y programar el scheduling de carga s_i. Estas decisiones no dependen del escenario."))
    story.append(P("<b>Segunda etapa:</b> una vez observado s, ajustar volúmenes entregados q_kjp^s, shortage u_jp^s, tiempos de servicio/espera t_kj^s y fill ratios rho_kcm^s."))
    story.append(P("<b>Función objetivo estocástica:</b>"))
    story.append(
        F(
            "min_chi C^(1)(chi) + sum_s pi_s Q_s(chi)\n\n"
            "C^(1)(chi) = sum_k F_k r_k + V_scheduling(chi)\n\n"
            "Q_s(chi) = 2*sum_kij D_ij x_kij + 10*sum_jp u_jp^s\n"
            "         + lambda1 V_demanda^s + lambda2 V_capacidad^s\n"
            "         + lambda3 V_estabilidad^s + lambda4 V_tiempo^s"
        )
    )
    story.append(P("<b>Restricciones:</b> primera etapa mantiene no anticipatividad; segunda etapa impone demanda, capacidad, estabilidad y ventanas por escenario."))
    story.append(F("sum_k q_kjp^s + u_jp^s = d_jp^s\n|rho_kC0m^s - rho_kC1m^s| <= 0.30\na_j z_kj <= t_kj^s <= b_j + M(1-z_kj)"))
    story.append(P("En GA, cada cromosoma se evalúa contra los tres escenarios y su aptitud final es el costo esperado penalizado."))

    story.append(H1("Conclusión"))
    story.append(P("La solución del operador no es factible: las cargas declaradas no alcanzan para satisfacer demanda, T2 viola estabilidad después de estación 2 y el costo declarado omite componentes obligatorios."))
    story.append(P("La ruta D->4->2->D para T2 sirve como primer acercamiento factible de costo 1200. El Algoritmo Genético mejora ese resultado: T1 atiende 1->2->4, T2 atiende 3, no hay shortage y el costo total baja a 1130."))
    story.append(P("El Algoritmo Genético permite abordar el problema completo codificando rutas, asignación de productos, volúmenes y scheduling en un cromosoma único, con una función de aptitud basada en costo real y penalizaciones."))

    return story


def build_reportlab_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="ENTREGA_FINAL",
        author="Codex",
    )
    doc.build(build_story(), onFirstPage=header_footer, onLaterPages=header_footer)


def main():
    if try_compile_latex():
        print(f"PDF generado con LaTeX: {PDF_PATH}")
        return
    build_reportlab_pdf()
    print(f"PDF generado con respaldo ReportLab: {PDF_PATH}")
    print(f"Fuente LaTeX disponible en: {TEX_PATH}")


if __name__ == "__main__":
    main()
