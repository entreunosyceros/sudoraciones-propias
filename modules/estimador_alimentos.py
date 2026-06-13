"""
Estimador de macronutrientes a partir de descripciones de comida en español.
Usa base de datos local y, opcionalmente, Open Food Facts como respaldo.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DetalleIngrediente:
    """Desglose de un ingrediente reconocido."""
    texto: str
    alimento: str
    gramos: float
    calorias: float
    proteinas_g: float
    carbohidratos_g: float
    grasas_g: float
    fuente: str
    confianza: str


@dataclass
class ResultadoEstimacion:
    """Resultado agregado de la estimación nutricional."""
    nombre: str
    calorias: float
    proteinas_g: float
    carbohidratos_g: float
    grasas_g: float
    detalles: list[DetalleIngrediente] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    ingredientes_no_reconocidos: list[str] = field(default_factory=list)

    def a_dict(self) -> dict[str, Any]:
        return {
            'nombre': self.nombre,
            'calories': round(self.calorias),
            'protein_g': round(self.proteinas_g, 1),
            'carbs_g': round(self.carbohidratos_g, 1),
            'fat_g': round(self.grasas_g, 1),
            'detalles': [
                {
                    'texto': d.texto,
                    'alimento': d.alimento,
                    'gramos': round(d.gramos, 1),
                    'calorias': round(d.calorias),
                    'proteinas_g': round(d.proteinas_g, 1),
                    'carbohidratos_g': round(d.carbohidratos_g, 1),
                    'grasas_g': round(d.grasas_g, 1),
                    'fuente': d.fuente,
                    'confianza': d.confianza,
                }
                for d in self.detalles
            ],
            'avisos': self.avisos,
            'ingredientes_no_reconocidos': self.ingredientes_no_reconocidos,
        }


class EstimadorAlimentos:
    """Estima macros a partir de texto libre en español."""

    RUTA_BD = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'alimentos_es.json')

    PATRON_GRAMOS = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:g|gr|gramos?)\b',
        re.IGNORECASE,
    )
    PATRON_UNIDADES = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:unidad(?:es)?|ud?s?|huevos?|rebanadas?|lonchas?|cucharadas?)\b',
        re.IGNORECASE,
    )
    PATRON_LATAS = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:latas?|lat(?:as)?)\b',
        re.IGNORECASE,
    )
    PATRON_LITROS = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:l|litros?)\b',
        re.IGNORECASE,
    )
    PATRON_ML_CL = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:ml|cl)\b',
        re.IGNORECASE,
    )

    GRAMOS_POR_CUCHARADA = {
        'azúcar': 12,
        'sirope de agave': 21,
        'miel': 15,
        'aceite de oliva': 10,
    }
    GRAMOS_POR_LATA = 330  # 33 cl

    def __init__(self, usar_open_food_facts: bool = True):
        self.usar_open_food_facts = usar_open_food_facts
        self.alimentos = self._cargar_alimentos()
        self._indice_busqueda = self._construir_indice()

    def _cargar_alimentos(self) -> list[dict]:
        if not os.path.exists(self.RUTA_BD):
            return []
        with open(self.RUTA_BD, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('alimentos', [])

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = texto.lower().strip()
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'\s+', ' ', texto)
        return texto

    def _construir_indice(self) -> list[tuple[str, dict]]:
        indice: list[tuple[str, dict]] = []
        for alimento in self.alimentos:
            nombres = [alimento['nombre']] + alimento.get('aliases', [])
            for nombre in nombres:
                indice.append((self._normalizar(nombre), alimento))
        indice.sort(key=lambda x: len(x[0]), reverse=True)
        return indice

    def _extraer_segmentos(self, descripcion: str) -> list[tuple[str, float | None]]:
        """Divide la descripción en ingredientes con gramos opcionales."""
        descripcion = descripcion.strip()
        if not descripcion:
            return []

        segmentos_crudos = re.split(
            r'\s*\+\s*|(?<!\d),\s*(?!\d)|\s+y\s+',
            descripcion,
            flags=re.IGNORECASE,
        )
        resultado: list[tuple[str, float | None]] = []

        for segmento in segmentos_crudos:
            segmento = segmento.strip()
            if not segmento:
                continue

            subsegmentos = self._dividir_segmento_compuesto(segmento)
            for sub in subsegmentos:
                parsed = self._parsear_subsegmento(sub)
                resultado.extend(parsed)

        return resultado

    def _dividir_segmento_compuesto(self, segmento: str) -> list[str]:
        """Separar «pollo con arroz» en ingredientes si no hay gramos."""
        if (
            self.PATRON_GRAMOS.search(segmento)
            or self.PATRON_LATAS.search(segmento)
            or self.PATRON_LITROS.search(segmento)
            or self.PATRON_ML_CL.search(segmento)
        ):
            return [segmento]

        partes = re.split(r'\s+con\s+', segmento, flags=re.IGNORECASE)
        if len(partes) <= 1:
            return [segmento]

        return [p.strip() for p in partes if p.strip()]

    @staticmethod
    def _inferir_alimento_cucharada(nombre: str, segmento: str) -> str:
        """Deducir el alimento cuando solo se indica «N cucharadas de …»."""
        texto = EstimadorAlimentos._normalizar(nombre or segmento)
        if 'agave' in texto or 'sirope' in texto:
            return 'sirope de agave'
        if 'azucar' in texto:
            return 'azúcar'
        if 'miel' in texto:
            return 'miel'
        if 'aceite' in texto:
            return 'aceite de oliva'
        return nombre.strip() if nombre.strip() else segmento

    def _gramos_por_cucharada(self, nombre: str) -> float:
        normalizado = self._normalizar(nombre)
        for clave, gramos in self.GRAMOS_POR_CUCHARADA.items():
            if self._normalizar(clave) in normalizado or normalizado in self._normalizar(clave):
                return gramos
        alimento, _ = self._buscar_local(nombre)
        if alimento:
            return float(alimento.get('racion_tipica_g', 10))
        return 10

    def _parsear_cantidad_volumen(self, segmento: str) -> tuple[str, float] | None:
        """Parsear latas, litros, ml o cl en gramos (bebidas ≈ 1 g/ml)."""
        for patron, factor in (
            (self.PATRON_LATAS, self.GRAMOS_POR_LATA),
            (self.PATRON_LITROS, 1000),
            (self.PATRON_ML_CL, 1),
        ):
            match = patron.search(segmento)
            if not match:
                continue
            cantidad = float(match.group(1).replace(',', '.'))
            nombre = patron.sub('', segmento).strip()
            nombre = re.sub(r'^(?:de\s+)', '', nombre, flags=re.IGNORECASE).strip()
            if patron is self.PATRON_ML_CL:
                unidad = match.group(0).lower()
                gramos = cantidad if 'ml' in unidad else cantidad * 10
            else:
                gramos = cantidad * factor
            return (nombre or segmento, gramos)
        return None

    def _parsear_subsegmento(self, segmento: str) -> list[tuple[str, float | None]]:
        resultado: list[tuple[str, float | None]] = []
        matches = list(self.PATRON_GRAMOS.finditer(segmento))

        if matches:
            for idx, match in enumerate(matches):
                gramos = float(match.group(1).replace(',', '.'))
                inicio = match.end()
                fin = matches[idx + 1].start() if idx + 1 < len(matches) else len(segmento)
                nombre = segmento[inicio:fin]
                nombre = re.sub(r'^(?:de\s+)', '', nombre.strip(), flags=re.IGNORECASE)
                nombre = re.sub(r'\s+con\s+$', '', nombre, flags=re.IGNORECASE).strip()
                if nombre:
                    resultado.append((nombre, gramos))
            return resultado

        volumen = self._parsear_cantidad_volumen(segmento)
        if volumen:
            nombre, gramos = volumen
            resultado.append((nombre, gramos))
            return resultado

        match_unidad = self.PATRON_UNIDADES.search(segmento)
        if match_unidad:
            cantidad = float(match_unidad.group(1).replace(',', '.'))
            unidad_texto = match_unidad.group(0).lower()
            nombre = self.PATRON_UNIDADES.sub('', segmento).strip()
            nombre = re.sub(r'^(?:de\s+)', '', nombre, flags=re.IGNORECASE)

            if not nombre.strip():
                if 'huevo' in unidad_texto:
                    nombre = 'huevo'
                elif 'rebanada' in unidad_texto or 'loncha' in unidad_texto:
                    nombre = 'pan integral'
                elif 'cucharada' in unidad_texto:
                    nombre = self._inferir_alimento_cucharada('', segmento)
                else:
                    nombre = segmento
            elif 'cucharada' in unidad_texto:
                nombre = self._inferir_alimento_cucharada(nombre, segmento)

            if 'huevo' in unidad_texto:
                gramos = cantidad * 60
            elif 'rebanada' in unidad_texto or 'loncha' in unidad_texto:
                gramos = cantidad * 40
            elif 'cucharada' in unidad_texto:
                gramos = cantidad * self._gramos_por_cucharada(nombre)
            else:
                gramos = cantidad * 100

            resultado.append((nombre, gramos))
            return resultado

        resultado.append((segmento, None))
        return resultado

    def _buscar_local(self, texto: str) -> tuple[dict | None, str]:
        normalizado = self._normalizar(texto)
        if not normalizado:
            return None, 'baja'

        mejor: dict | None = None
        mejor_longitud = 0
        for clave, alimento in self._indice_busqueda:
            if clave in normalizado:
                if len(clave) > mejor_longitud:
                    mejor = alimento
                    mejor_longitud = len(clave)

        confianza = 'alta' if mejor and mejor_longitud >= 4 else 'media' if mejor else 'baja'
        return mejor, confianza

    def _buscar_open_food_facts(self, texto: str) -> dict | None:
        if not self.usar_open_food_facts or not texto.strip():
            return None

        params = urllib.parse.urlencode({
            'search_terms': texto,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': 3,
            'lc': 'es',
            'fields': 'product_name,nutriments',
        })
        url = f'https://world.openfoodfacts.org/cgi/search.pl?{params}'

        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None

        for producto in data.get('products', []):
            nut = producto.get('nutriments', {})
            calorias = nut.get('energy-kcal_100g') or nut.get('energy_100g')
            proteinas = nut.get('proteins_100g')
            carbos = nut.get('carbohydrates_100g')
            grasas = nut.get('fat_100g')
            if calorias is None:
                continue
            return {
                'nombre': producto.get('product_name', texto),
                'por_100g': {
                    'calorias': float(calorias),
                    'proteinas_g': float(proteinas or 0),
                    'carbohidratos_g': float(carbos or 0),
                    'grasas_g': float(grasas or 0),
                },
                'racion_tipica_g': 100,
            }
        return None

    @staticmethod
    def _escalar(alimento: dict, gramos: float) -> DetalleIngrediente:
        por_100g = alimento['por_100g']
        factor = gramos / 100.0
        calorias = por_100g['calorias'] * factor
        proteinas = por_100g['proteinas_g'] * factor
        carbos = por_100g['carbohidratos_g'] * factor
        grasas = por_100g['grasas_g'] * factor

        if calorias <= 0:
            calorias = (proteinas * 4) + (carbos * 4) + (grasas * 9)

        return DetalleIngrediente(
            texto=alimento.get('nombre', ''),
            alimento=alimento.get('nombre', ''),
            gramos=gramos,
            calorias=calorias,
            proteinas_g=proteinas,
            carbohidratos_g=carbos,
            grasas_g=grasas,
            fuente=alimento.get('_fuente', 'base local'),
            confianza=alimento.get('_confianza', 'media'),
        )

    def estimar(self, descripcion: str) -> ResultadoEstimacion:
        """Estimar macronutrientes de una descripción de comida."""
        descripcion = descripcion.strip()
        if not descripcion:
            return ResultadoEstimacion(
                nombre='',
                calorias=0,
                proteinas_g=0,
                carbohidratos_g=0,
                grasas_g=0,
                avisos=['Escribe qué has comido para poder estimar los macros.'],
            )

        segmentos = self._extraer_segmentos(descripcion)
        if not segmentos:
            segmentos = [(descripcion, None)]

        detalles: list[DetalleIngrediente] = []
        no_reconocidos: list[str] = []
        avisos = [
            'Estimación orientativa. Revisa y ajusta los valores antes de guardar.',
        ]

        for texto_segmento, gramos in segmentos:
            alimento, confianza = self._buscar_local(texto_segmento)
            fuente = 'base local'

            if alimento is None and self.usar_open_food_facts:
                alimento_off = self._buscar_open_food_facts(texto_segmento)
                if alimento_off:
                    alimento = alimento_off
                    fuente = 'Open Food Facts'
                    confianza = 'media'

            if alimento is None:
                no_reconocidos.append(texto_segmento)
                continue

            alimento = dict(alimento)
            alimento['_fuente'] = fuente
            alimento['_confianza'] = confianza
            gramos_finales = gramos if gramos is not None else float(alimento.get('racion_tipica_g', 100))

            detalle = self._escalar(alimento, gramos_finales)
            detalle.texto = texto_segmento
            detalle.fuente = fuente
            detalle.confianza = confianza
            detalles.append(detalle)

        if not detalles:
            avisos.append('No se reconoció ningún alimento. Prueba a ser más específico o indica gramos (ej: "200 g pechuga de pollo").')
            return ResultadoEstimacion(
                nombre=descripcion,
                calorias=0,
                proteinas_g=0,
                carbohidratos_g=0,
                grasas_g=0,
                avisos=avisos,
                ingredientes_no_reconocidos=no_reconocidos,
            )

        if no_reconocidos:
            avisos.append(
                f'No reconocido: {", ".join(no_reconocidos)}. '
                'Se estimó solo lo identificado; puedes completar el resto a mano.'
            )

        if any(gramos is None for _, gramos in segmentos):
            avisos.append('Sin cantidades en gramos: se usó la ración típica de cada alimento.')

        total_cal = sum(d.calorias for d in detalles)
        total_p = sum(d.proteinas_g for d in detalles)
        total_c = sum(d.carbohidratos_g for d in detalles)
        total_g = sum(d.grasas_g for d in detalles)

        return ResultadoEstimacion(
            nombre=descripcion,
            calorias=total_cal,
            proteinas_g=total_p,
            carbohidratos_g=total_c,
            grasas_g=total_g,
            detalles=detalles,
            avisos=avisos,
            ingredientes_no_reconocidos=no_reconocidos,
        )
