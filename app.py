"""
Chatbot para Ecuahierro (Riobamba)
- WhatsApp Business API (Twilio Sandbox)
- Base de datos de productos con precios referenciales
- Flujo: Saludo → Nombre → Consulta de productos → Compra
- Sin página web, todo por chat
"""

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

# ============================================================
# 1. BASE DE DATOS DE PRODUCTOS (ampliada)
# ============================================================

PRODUCTOS = {
    # --- Materiales para cimentación y estructura ---
    "varilla": {
        "nombre": "Varilla de Hierro Corrugada (Novacero)",
        "unidad": "Varilla (6m)",
        "precio": 12.50
    },
    "varilla quintal": {
        "nombre": "Varilla de Hierro Corrugada (Novacero) por Quintal",
        "unidad": "Quintal (100 kg)",
        "precio": 85.00
    },
    "varilla lisa": {
        "nombre": "Varilla Lisa de Acero",
        "unidad": "Varilla (6m)",
        "precio": 11.00
    },
    "estribos": {
        "nombre": "Estribos (Novacero)",
        "unidad": "Unidad",
        "precio": 2.25  # promedio
    },
    "malla electrosoldada": {
        "nombre": "Malla Electrosoldada (Novacero)",
        "unidad": "Rollo/Plancha",
        "precio": 47.50  # promedio
    },
    "alambre amarre": {
        "nombre": "Alambre de Amarre (Novacero)",
        "unidad": "Kilo (kg)",
        "precio": 2.80
    },
    "alambre galvanizado": {
        "nombre": "Alambre Galvanizado",
        "unidad": "Kilo (kg)",
        "precio": 3.20
    },
    "clavos": {
        "nombre": "Clavos",
        "unidad": "Kilo (kg)",
        "precio": 1.75
    },
    "clavos cabeza": {
        "nombre": "Clavos con Cabeza",
        "unidad": "Kilo (kg)",
        "precio": 2.00
    },
    "puntillas": {
        "nombre": "Puntillas",
        "unidad": "Kilo (kg)",
        "precio": 1.90
    },
    "grapas": {
        "nombre": "Grapas",
        "unidad": "Kilo (kg)",
        "precio": 2.50
    },

    # --- Bloques y prefabricados ---
    "bloque": {
        "nombre": "Bloque de Hormigón (20x40x20 cm)",
        "unidad": "Unidad",
        "precio": 0.52
    },
    "bloque 10": {
        "nombre": "Bloque de Hormigón (10x20x40 cm)",
        "unidad": "Unidad",
        "precio": 0.45
    },
    "ladrillo macizo": {
        "nombre": "Ladrillo Macizo",
        "unidad": "Unidad",
        "precio": 0.30
    },
    "ladrillo hueco": {
        "nombre": "Ladrillo Hueco",
        "unidad": "Unidad",
        "precio": 0.25
    },
    "baldosa": {
        "nombre": "Baldosa de Cemento",
        "unidad": "Unidad",
        "precio": 1.20
    },
    "tubo hormigon": {
        "nombre": "Tubo de Hormigón",
        "unidad": "Unidad",
        "precio": 27.50  # promedio
    },

    # --- Herramientas manuales ---
    "martillo": {
        "nombre": "Martillo",
        "unidad": "Unidad",
        "precio": 9.00
    },
    "combo": {
        "nombre": "Combo / Mazo",
        "unidad": "Unidad",
        "precio": 12.00
    },
    "cuchara": {
        "nombre": "Cuchara de Albañil",
        "unidad": "Unidad",
        "precio": 4.00
    },
    "paleta": {
        "nombre": "Paleta de Albañil",
        "unidad": "Unidad",
        "precio": 3.50
    },
    "llana": {
        "nombre": "Llana",
        "unidad": "Unidad",
        "precio": 5.00
    },
    "nivel": {
        "nombre": "Nivel de Burbuja",
        "unidad": "Unidad",
        "precio": 11.50  # promedio
    },
    "flexometro": {
        "nombre": "Flexómetro",
        "unidad": "Unidad",
        "precio": 6.50  # promedio 5m/8m
    },
    "escuadra": {
        "nombre": "Escuadra",
        "unidad": "Unidad",
        "precio": 5.50  # promedio
    },
    "serrucho": {
        "nombre": "Serrucho",
        "unidad": "Unidad",
        "precio": 8.00
    },
    "sierra metal": {
        "nombre": "Sierra para Metal",
        "unidad": "Unidad",
        "precio": 10.00
    },
    "alicante": {
        "nombre": "Alicate",
        "unidad": "Unidad",
        "precio": 5.00
    },
    "pinza": {
        "nombre": "Pinza",
        "unidad": "Unidad",
        "precio": 4.50
    },
    "destornillador": {
        "nombre": "Juego de Destornilladores",
        "unidad": "Juego",
        "precio": 9.00
    },
    "llave agua": {
        "nombre": "Llave de Agua",
        "unidad": "Unidad",
        "precio": 6.00
    },
    "juego llaves": {
        "nombre": "Juego de Llaves (milimétricas)",
        "unidad": "Juego",
        "precio": 20.00
    },
    "tenaza": {
        "nombre": "Tenaza",
        "unidad": "Unidad",
        "precio": 7.00
    },
    "cutter": {
        "nombre": "Cutter / Navaja",
        "unidad": "Unidad",
        "precio": 3.00
    },
    "tijera lamina": {
        "nombre": "Tijera para Lámina",
        "unidad": "Unidad",
        "precio": 8.00
    },

    # --- Herramientas eléctricas ---
    "amoladora": {
        "nombre": "Amoladora (4 1/2'')",
        "unidad": "Unidad",
        "precio": 57.50  # promedio
    },
    "rotomartillo": {
        "nombre": "Rotomartillo",
        "unidad": "Unidad",
        "precio": 115.00  # promedio
    },
    "taladro": {
        "nombre": "Taladro",
        "unidad": "Unidad",
        "precio": 70.00  # promedio
    },
    "sierra circular": {
        "nombre": "Sierra Circular",
        "unidad": "Unidad",
        "precio": 90.00  # promedio
    },
    "caladora": {
        "nombre": "Caladora",
        "unidad": "Unidad",
        "precio": 55.00
    },
    "esmeril": {
        "nombre": "Esmeril de Banco",
        "unidad": "Unidad",
        "precio": 67.50  # promedio
    },
    "compresor": {
        "nombre": "Compresor de Aire",
        "unidad": "Unidad",
        "precio": 225.00  # promedio
    },
    "pistola clavos": {
        "nombre": "Pistola de Clavos",
        "unidad": "Unidad",
        "precio": 115.00  # promedio
    },

    # --- Accesorios para herramientas ---
    "disco corte": {
        "nombre": "Disco de Corte (4 1/2'')",
        "unidad": "Unidad",
        "precio": 3.00  # promedio
    },
    "disco desbaste": {
        "nombre": "Disco de Desbaste",
        "unidad": "Unidad",
        "precio": 3.75
    },
    "broca concreto": {
        "nombre": "Broca para Concreto (SDS Plus)",
        "unidad": "Unidad",
        "precio": 10.00  # promedio
    },
    "broca metal": {
        "nombre": "Broca para Metal (HSS)",
        "unidad": "Unidad",
        "precio": 6.50
    },
    "broca madera": {
        "nombre": "Broca para Madera",
        "unidad": "Unidad",
        "precio": 4.00
    },
    "broca diamantada": {
        "nombre": "Broca Diamantada",
        "unidad": "Unidad",
        "precio": 14.00
    },
    "cepillo alambre": {
        "nombre": "Cepillo de Alambre (para amoladora)",
        "unidad": "Unidad",
        "precio": 5.50
    },
    "carda": {
        "nombre": "Carda (disco de alambre)",
        "unidad": "Unidad",
        "precio": 5.00
    },
    "punta rotomartillo": {
        "nombre": "Punta para Rotomartillo",
        "unidad": "Unidad",
        "precio": 8.00  # promedio
    },

    # --- Ferretería general ---
    "pernos": {
        "nombre": "Pernos y Tuercas",
        "unidad": "Unidad/Kilo",
        "precio": 1.00  # promedio
    },
    "arandelas": {
        "nombre": "Arandelas",
        "unidad": "Unidad/Kilo",
        "precio": 0.50
    },
    "remaches": {
        "nombre": "Remaches",
        "unidad": "Unidad",
        "precio": 0.12
    },
    "tornillos": {
        "nombre": "Tornillos (varios tipos)",
        "unidad": "Unidad/Kilo",
        "precio": 0.30
    },
    "bisagras": {
        "nombre": "Bisagras",
        "unidad": "Unidad",
        "precio": 3.00  # promedio
    },
    "cerraduras": {
        "nombre": "Cerraduras",
        "unidad": "Unidad",
        "precio": 16.50  # promedio
    },
    "pasadores": {
        "nombre": "Pasadores",
        "unidad": "Unidad",
        "precio": 1.25
    },
    "cadenas": {
        "nombre": "Cadenas",
        "unidad": "Metro",
        "precio": 5.50
    },
    "candados": {
        "nombre": "Candados",
        "unidad": "Unidad",
        "precio": 6.50  # promedio
    },

    # --- Tuberías, grifería y plomería ---
    "tuberia pvc": {
        "nombre": "Tubería PVC (presión) - Eternit",
        "unidad": "Tubo (3m)",
        "precio": 8.00
    },
    "tuberia pvc sanitario": {
        "nombre": "Tubería PVC sanitaria - Eternit",
        "unidad": "Tubo (3m)",
        "precio": 6.00
    },
    "tuberia galvanizada": {
        "nombre": "Tubería Galvanizada - Adelca",
        "unidad": "Tubo (3m)",
        "precio": 12.00
    },
    "tubo estructural": {
        "nombre": "Tubo Estructural (cuadrado/rectangular) - Adelca",
        "unidad": "Tubo (6m)",
        "precio": 30.00  # promedio
    },
    "tubo cobre": {
        "nombre": "Tubo para Gas (cobre)",
        "unidad": "Metro",
        "precio": 6.00
    },
    "codo pvc": {
        "nombre": "Codo PVC - Eternit",
        "unidad": "Unidad",
        "precio": 2.00  # promedio
    },
    "tee pvc": {
        "nombre": "Tee PVC - Eternit",
        "unidad": "Unidad",
        "precio": 3.00
    },
    "reduccion pvc": {
        "nombre": "Reducción PVC - Eternit",
        "unidad": "Unidad",
        "precio": 2.50
    },
    "codo galvanizado": {
        "nombre": "Codo Galvanizado - Adelca",
        "unidad": "Unidad",
        "precio": 4.00
    },
    "tee galvanizado": {
        "nombre": "Tee Galvanizada - Adelca",
        "unidad": "Unidad",
        "precio": 5.00
    },
    "niple": {
        "nombre": "Niple Galvanizado - Foset",
        "unidad": "Unidad",
        "precio": 3.00
    },
    "niple campana": {
        "nombre": "Niple Campana para Gas - Foset",
        "unidad": "Unidad",
        "precio": 3.00
    },
    "grifo lavabo": {
        "nombre": "Grifería para Lavabo",
        "unidad": "Juego",
        "precio": 27.50
    },
    "grifo cocina": {
        "nombre": "Grifería para Cocina",
        "unidad": "Juego",
        "precio": 35.00
    },
    "valvula paso": {
        "nombre": "Válvula de Paso",
        "unidad": "Unidad",
        "precio": 5.50
    },
    "llave agua": {
        "nombre": "Llave de Agua",
        "unidad": "Unidad",
        "precio": 8.50
    },
    "flexible agua": {
        "nombre": "Flexible de Agua",
        "unidad": "Unidad",
        "precio": 4.50
    },

    # --- Cubiertas, techos y acabados ---
    "teja fibrocemento": {
        "nombre": "Teja de Fibrocemento (ondulada) - Eternit",
        "unidad": "Unidad/m²",
        "precio": 8.50
    },
    "teja polipropileno": {
        "nombre": "Teja de Polipropileno (Techolit) - Eternit",
        "unidad": "Unidad/m²",
        "precio": 10.00
    },
    "eterboard": {
        "nombre": "Plancha de Fibrocemento (Eterboard) - Eternit",
        "unidad": "Plancha",
        "precio": 22.50
    },
    "plancha acero": {
        "nombre": "Plancha de Acero Inoxidable",
        "unidad": "Plancha",
        "precio": 55.00
    },
    "plancha zinc": {
        "nombre": "Plancha de Zinc / Galvanizada - Adelca",
        "unidad": "Plancha",
        "precio": 35.00
    },
    "panel techo": {
        "nombre": "Panel de Techo - Adelca",
        "unidad": "Unidad/m²",
        "precio": 18.50
    },
    "losa techo": {
        "nombre": "Losa de Techo - Adelca",
        "unidad": "Unidad/m²",
        "precio": 15.00
    },
    "cumbrero": {
        "nombre": "Cumbrero para Techo - Adelca",
        "unidad": "Unidad",
        "precio": 11.50
    },
    "caballete": {
        "nombre": "Caballete para Techo - Eternit",
        "unidad": "Unidad",
        "precio": 8.50
    },

    # --- Pinturas y acabados ---
    "pintura esmalte": {
        "nombre": "Pintura Esmalte - Kubiec",
        "unidad": "Galón (4L)",
        "precio": 22.00
    },
    "pintura latex": {
        "nombre": "Pintura Látex - Kubiec",
        "unidad": "Galón (4L)",
        "precio": 23.00
    },
    "pintura aerosol": {
        "nombre": "Pintura en Aerosol (400 ml) - Acuario/Truper",
        "unidad": "Unidad",
        "precio": 6.00
    },
    "pintura metalica": {
        "nombre": "Pintura en Aerosol (metálico)",
        "unidad": "Unidad",
        "precio": 7.00
    },
    "esmalte sintetico": {
        "nombre": "Esmalte Sintético - Kubiec",
        "unidad": "Galón (4L)",
        "precio": 25.00
    },
    "barniz": {
        "nombre": "Barniz - Kubiec",
        "unidad": "Galón (4L)",
        "precio": 20.00
    },
    "empaste": {
        "nombre": "Empaste para Paredes",
        "unidad": "Frasco/Kilo",
        "precio": 5.50
    },
    "masilla": {
        "nombre": "Masilla",
        "unidad": "Frasco/Kilo",
        "precio": 4.25
    },
    "thinner": {
        "nombre": "Diluyente / Thinner",
        "unidad": "Galón (4L)",
        "precio": 10.00
    },
    "brocha": {
        "nombre": "Brochas (varios tamaños)",
        "unidad": "Unidad",
        "precio": 3.75
    },
    "rodillo": {
        "nombre": "Rodillos para Pintar",
        "unidad": "Juego",
        "precio": 5.50
    },
    "lija": {
        "nombre": "Lijas (diferentes granos)",
        "unidad": "Unidad",
        "precio": 1.00
    },

    # --- Equipo de seguridad ---
    "casco": {
        "nombre": "Casco de Seguridad",
        "unidad": "Unidad",
        "precio": 6.50
    },
    "guantes cuero": {
        "nombre": "Guantes de Cuero",
        "unidad": "Par",
        "precio": 4.00
    },
    "guantes nitrilo": {
        "nombre": "Guantes de Nitrilo",
        "unidad": "Par",
        "precio": 3.00
    },
    "botas seguridad": {
        "nombre": "Botas Punta de Acero",
        "unidad": "Par",
        "precio": 35.00
    },
    "gafas": {
        "nombre": "Gafas de Seguridad",
        "unidad": "Unidad",
        "precio": 5.50
    },
    "mascarilla": {
        "nombre": "Mascarilla de Protección",
        "unidad": "Unidad",
        "precio": 2.50
    },
    "arnes": {
        "nombre": "Arnés de Seguridad",
        "unidad": "Unidad",
        "precio": 37.50
    },
    "cuerda seguridad": {
        "nombre": "Cuerda de Seguridad",
        "unidad": "Metro",
        "precio": 3.50
    },
    "tapones": {
        "nombre": "Tapones para Oídos",
        "unidad": "Par",
        "precio": 2.00
    },
    "chaleco": {
        "nombre": "Chaleco Reflectivo",
        "unidad": "Unidad",
        "precio": 7.50
    },
    "señalizacion": {
        "nombre": "Señalización de Obra",
        "unidad": "Unidad",
        "precio": 12.50
    },

    # --- Metalmecánica y estructuras metálicas ---
    "perfil estructural": {
        "nombre": "Perfil Estructural (viga/columna) - Novacero/Adelca",
        "unidad": "Metro/Unidad",
        "precio": 37.50
    },
    "tubo cuadrado": {
        "nombre": "Tubo Estructural (cuadrado) - Adelca",
        "unidad": "Tubo (6m)",
        "precio": 32.50
    },
    "tubo rectangular": {
        "nombre": "Tubo Estructural (rectangular) - Adelca",
        "unidad": "Tubo (6m)",
        "precio": 37.50
    },
    "angulo acero": {
        "nombre": "Ángulo de Acero - Novacero",
        "unidad": "Metro/Unidad",
        "precio": 14.00
    },
    "canal acero": {
        "nombre": "Canal de Acero - Novacero",
        "unidad": "Metro/Unidad",
        "precio": 17.50
    },
    "plancha acero": {
        "nombre": "Plancha de Acero (lámina) - Novacero",
        "unidad": "Plancha",
        "precio": 55.00
    },
    "rejilla metalica": {
        "nombre": "Rejilla Metálica",
        "unidad": "Plancha",
        "precio": 27.50
    },
    "malla ciclonica": {
        "nombre": "Malla Ciclónica",
        "unidad": "Metro/Rollo",
        "precio": 20.00
    },
    "alambre púas": {
        "nombre": "Alambre de Púas",
        "unidad": "Rollo",
        "precio": 35.00
    },

    # --- Otros productos ---
    "cemento": {
        "nombre": "Cemento (Chimborazo)",
        "unidad": "Saco (50 kg)",
        "precio": 7.05
    },
    "cemento he": {
        "nombre": "Cemento Tipo HE (Chimborazo)",
        "unidad": "Saco (50 kg)",
        "precio": 8.50
    },
    "cal": {
        "nombre": "Cal",
        "unidad": "Saco (25 kg)",
        "precio": 6.50
    },
    "yeso": {
        "nombre": "Yeso",
        "unidad": "Saco (25 kg)",
        "precio": 8.00
    },
    "pegamento ceramica": {
        "nombre": "Pegamento para Cerámica",
        "unidad": "Saco (25 kg)",
        "precio": 11.50
    },
    "pegablok": {
        "nombre": "Pegablok (Tipo II)",
        "unidad": "Saco",
        "precio": 3.50
    },
    "escoba": {
        "nombre": "Escoba",
        "unidad": "Unidad",
        "precio": 4.50
    },
    "recogedor": {
        "nombre": "Recogedor",
        "unidad": "Unidad",
        "precio": 3.00
    },
    "trapeador": {
        "nombre": "Trapeador",
        "unidad": "Unidad",
        "precio": 6.00
    },
    "balde": {
        "nombre": "Balde Plástico",
        "unidad": "Unidad",
        "precio": 3.75
    },
    "carretilla": {
        "nombre": "Carretilla",
        "unidad": "Unidad",
        "precio": 55.00
    },
    "pala": {
        "nombre": "Pala",
        "unidad": "Unidad",
        "precio": 11.50
    },
    "pico": {
        "nombre": "Pico",
        "unidad": "Unidad",
        "precio": 14.00
    },
    "barreta": {
        "nombre": "Barreta",
        "unidad": "Unidad",
        "precio": 16.00
    },
    "cinta aislar": {
        "nombre": "Cinta de Aislar",
        "unidad": "Rollo",
        "precio": 2.00
    },
    "cinta teiplon": {
        "nombre": "Cinta Teiplon",
        "unidad": "Rollo",
        "precio": 1.00
    },
    "pegamento pvc": {
        "nombre": "Pegamento PVC",
        "unidad": "Frasco",
        "precio": 3.50
    }
}

# ============================================================
# 2. ESTADO DE USUARIOS (en memoria)
# ============================================================
# Cada usuario guarda:
#   - 'nombre': str
#   - 'paso': str  (None, 'esperando_nombre', 'menu', 'compra_cantidad', 'compra_datos', 'compra_confirmar')
#   - 'producto_actual': dict  (producto que está comprando)
#   - 'carrito': list  (para futura expansión)
#   - 'ultimo_mensaje': str

estados_usuarios = {}

# ============================================================
# 3. FUNCIONES DE PROCESAMIENTO
# ============================================================

def normalizar_texto(texto):
    """Elimina espacios extras, convierte a minúsculas y quita tildes básicas."""
    texto = texto.strip().lower()
    # Reemplazar tildes comunes
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u'
    }
    for acento, sin_acento in reemplazos.items():
        texto = texto.replace(acento, sin_acento)
    return texto

def buscar_producto(mensaje):
    """
    Busca si el mensaje contiene alguna clave de producto.
    Devuelve (clave_encontrada, producto) o (None, None)
    """
    mensaje_norm = normalizar_texto(mensaje)
    # Ordenar claves por longitud (para que "varilla quintal" tenga prioridad sobre "varilla")
    claves = sorted(PRODUCTOS.keys(), key=len, reverse=True)
    for clave in claves:
        if clave in mensaje_norm:
            return clave, PRODUCTOS[clave]
    return None, None

def formatear_producto(clave, producto):
    """Devuelve un mensaje bonito con la información del producto."""
    return (f"📏 *{producto['nombre']}*\n"
            f"   - Unidad: {producto['unidad']}\n"
            f"   - Precio: ${producto['precio']:.2f}\n\n"
            f"¿Quieres comprar? Responde *'comprar {clave}'* para iniciar el pedido.")

def obtener_respuesta(mensaje, numero_usuario):
    """
    Función principal que procesa el mensaje y devuelve la respuesta del bot.
    """
    mensaje_norm = normalizar_texto(mensaje)
    estado = estados_usuarios.get(numero_usuario, {})
    paso = estado.get('paso', None)

    # ============================================================
    # CASO 1: PRIMERA VEZ - SIN NOMBRE REGISTRADO
    # ============================================================
    if not estado.get('nombre'):
        # Si el usuario ya había iniciado pero no dio nombre, preguntamos
        if paso == 'esperando_nombre':
            nombre = mensaje.strip()
            if len(nombre) < 2:
                return "Por favor, escríbeme tu nombre completo para poder ayudarte mejor."
            # Guardar nombre
            estado['nombre'] = nombre.title()
            estado['paso'] = 'menu'
            estados_usuarios[numero_usuario] = estado
            return (f"¡Encantado de conocerte, {nombre.title()}! 🤝\n\n"
                    "Soy el asistente virtual de *Ecuahierro*.\n"
                    "Puedes escribir el nombre de cualquier producto (ej. 'varilla', 'cemento', 'pintura') y te daré su precio y unidad de venta.\n\n"
                    "También puedes usar estos comandos:\n"
                    "📍 *dirección* - Dónde estamos\n"
                    "🕒 *horario* - Horarios de atención\n"
                    "💬 *asesor* - Hablar con un vendedor\n"
                    "🛒 *carrito* - Ver tu pedido (próximamente)\n\n"
                    "¿En qué te ayudo hoy?")
        else:
            # Primera interacción
            estado['paso'] = 'esperando_nombre'
            estados_usuarios[numero_usuario] = estado
            return ("¡Hola! Bienvenido a *Ecuahierro* 🏗️\n\n"
                    "Somos tu ferretería de confianza en Riobamba con más de 45 años de experiencia.\n"
                    "Para empezar, ¿me podrías decir tu nombre?")

    # ============================================================
    # CASO 2: COMPRA EN PROCESO
    # ============================================================
    if paso == 'compra_cantidad':
        # Esperamos que el usuario escriba un número (cantidad)
        try:
            cantidad = float(mensaje_norm.replace(',', '.'))
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser positiva")
        except:
            return ("Por favor, escribe una cantidad válida (ej. '5', '3.5').\n"
                    "Si quieres cancelar la compra, escribe *'cancelar'*.")

        producto_actual = estado.get('producto_actual')
        if not producto_actual:
            # Si por error no hay producto, reiniciamos al menú
            estado['paso'] = 'menu'
            estados_usuarios[numero_usuario] = estado
            return "Parece que hubo un error. Vuelve a escribir el producto que deseas comprar."

        # Calcular total
        precio_unitario = producto_actual['precio']
        total = cantidad * precio_unitario
        nombre_producto = producto_actual['nombre']
        unidad = producto_actual['unidad']

        # Guardar datos en estado
        estado['cantidad'] = cantidad
        estado['total'] = total
        estado['paso'] = 'compra_datos'
        estados_usuarios[numero_usuario] = estado

        return (f"✅ *Resumen de tu pedido*\n"
                f"   Producto: {nombre_producto}\n"
                f"   Cantidad: {cantidad} {unidad}\n"
                f"   Precio unitario: ${precio_unitario:.2f}\n"
                f"   *Total: ${total:.2f}*\n\n"
                f"Para confirmar, necesito tus datos:\n"
                f"   - Tu nombre completo\n"
                f"   - Dirección de entrega\n"
                f"   - Teléfono de contacto\n\n"
                f"Escríbemelos en un solo mensaje, separados por comas.\n"
                f"Ejemplo: 'Juan Pérez, Av. 10 de Agosto 123, 0987654321'\n"
                f"O escribe *'cancelar'* para anular la compra.")

    if paso == 'compra_datos':
        if mensaje_norm == 'cancelar':
            estado['paso'] = 'menu'
            estado.pop('producto_actual', None)
            estado.pop('cantidad', None)
            estado.pop('total', None)
            estados_usuarios[numero_usuario] = estado
            return "🔄 Compra cancelada. Puedes seguir consultando productos o usar los comandos de ayuda."

        # Extraer datos (nombre, dirección, teléfono)
        partes = [p.strip() for p in mensaje.split(',')]
        if len(partes) < 3:
            return ("Por favor, proporciona los tres datos separados por comas:\n"
                    "Ejemplo: 'Juan Pérez, Av. 10 de Agosto 123, 0987654321'\n"
                    "O escribe *'cancelar'* para anular la compra.")

        nombre_cliente = partes[0].title()
        direccion = partes[1].title()
        telefono = partes[2].strip()

        # Guardar datos
        estado['cliente_nombre'] = nombre_cliente
        estado['cliente_direccion'] = direccion
        estado['cliente_telefono'] = telefono
        estado['paso'] = 'compra_confirmar'
        estados_usuarios[numero_usuario] = estado

        producto_actual = estado.get('producto_actual')
        cantidad = estado.get('cantidad')
        total = estado.get('total')

        return (f"📋 *Confirmación de pedido*\n\n"
                f"Producto: {producto_actual['nombre']}\n"
                f"Cantidad: {cantidad} {producto_actual['unidad']}\n"
                f"Total: ${total:.2f}\n\n"
                f"Cliente: {nombre_cliente}\n"
                f"Dirección: {direccion}\n"
                f"Teléfono: {telefono}\n\n"
                f"¿Confirmas este pedido? Responde *'confirmar'* o *'cancelar'*.")

    if paso == 'compra_confirmar':
        if mensaje_norm == 'confirmar':
            # Aquí se podría enviar una notificación a Ecuahierro (ej. correo, webhook)
            # Por simplicidad, solo damos el mensaje final
            nombre_cliente = estado.get('cliente_nombre', 'Cliente')
            producto_actual = estado.get('producto_actual')
            cantidad = estado.get('cantidad')
            total = estado.get('total')
            direccion = estado.get('cliente_direccion', '')
            telefono = estado.get('cliente_telefono', '')

            # Limpiar estado de compra, pero mantener el nombre
            estado['paso'] = 'menu'
            estado.pop('producto_actual', None)
            estado.pop('cantidad', None)
            estado.pop('total', None)
            estado.pop('cliente_nombre', None)
            estado.pop('cliente_direccion', None)
            estado.pop('cliente_telefono', None)
            estados_usuarios[numero_usuario] = estado

            return (f"✅ *¡Pedido confirmado!*\n\n"
                    f"Hemos recibido tu compra:\n"
                    f"- Producto: {producto_actual['nombre']}\n"
                    f"- Cantidad: {cantidad} {producto_actual['unidad']}\n"
                    f"- Total: ${total:.2f}\n"
                    f"- Entrega en: {direccion}\n"
                    f"- Contacto: {telefono}\n\n"
                    f"📞 Un asesor de Ecuahierro se comunicará contigo para coordinar el pago y la entrega.\n"
                    f"¡Gracias por tu compra, {nombre_cliente}! 🙌\n"
                    f"¿Necesitas algo más? Puedes seguir consultando productos.")

        elif mensaje_norm == 'cancelar':
            estado['paso'] = 'menu'
            estado.pop('producto_actual', None)
            estado.pop('cantidad', None)
            estado.pop('total', None)
            estado.pop('cliente_nombre', None)
            estado.pop('cliente_direccion', None)
            estado.pop('cliente_telefono', None)
            estados_usuarios[numero_usuario] = estado
            return "🔄 Compra cancelada. ¿En qué más puedo ayudarte?"

        else:
            return "Por favor, responde *'confirmar'* para aceptar el pedido o *'cancelar'* para anularlo."

    # ============================================================
    # CASO 3: MENÚ PRINCIPAL (comandos y búsqueda de productos)
    # ============================================================
    # Comandos especiales
    if mensaje_norm in ['dirección', 'direccion']:
        return ("📍 *Dirección de Ecuahierro*\n\n"
                "📌 *Ecuahierro Centro*\n"
                "   Eugenio Espejo 27-19 y Junín, Riobamba\n\n"
                "📌 *Ecuahierro Sur*\n"
                "   (Nueva sucursal)\n\n"
                "¡Te esperamos! 🏬")

    if mensaje_norm in ['horario', 'horarios']:
        return ("🕒 *Horarios de atención*\n\n"
                "📅 *Lunes a Viernes*\n"
                "   8:00 AM – 1:00 PM\n"
                "   2:00 PM – 6:00 PM\n\n"
                "📅 *Sábado*\n"
                "   8:00 AM – 1:00 PM\n"
                "   2:30 PM – 5:00 PM\n\n"
                "📅 *Domingo*\n"
                "   Cerrado\n\n"
                "¡Ven a visitarnos! 🛠️")

    if mensaje_norm in ['asesor', 'vendedor', 'hablar', 'contacto']:
        return ("💬 *Hablar con un asesor*\n\n"
                "📞 Llámanos al: *+593 3-296-4202*\n"
                "📍 Visítanos en: Eugenio Espejo 27-19 y Junín, Riobamba\n\n"
                "Nuestros vendedores están capacitados para ayudarte con tus proyectos. ¡No dudes en contactarnos! 🤝")

    if mensaje_norm in ['menu', 'ayuda', 'hola', 'buenos dias', 'buenas tardes']:
        return (f"¡Hola de nuevo, {estado['nombre']}! 👋\n\n"
                "Recuerda que puedes:\n"
                "• Escribir el nombre de un producto para ver su precio.\n"
                "• Usar comandos: *dirección*, *horario*, *asesor*.\n"
                "• Si quieres comprar, escribe *'comprar [producto]'*.\n\n"
                "¿Qué necesitas?")

    # Búsqueda de productos por nombre
    if mensaje_norm.startswith('comprar '):
        # Intento de compra directa: "comprar varilla"
        termino = mensaje_norm.replace('comprar ', '').strip()
        clave, producto = buscar_producto(termino)
        if clave:
            # Iniciar proceso de compra
            estado['paso'] = 'compra_cantidad'
            estado['producto_actual'] = producto
            estados_usuarios[numero_usuario] = estado
            return (f"🛒 *Iniciando compra de {producto['nombre']}*\n\n"
                    f"Precio unitario: ${producto['precio']:.2f} por {producto['unidad']}\n"
                    f"¿Cuántas unidades deseas comprar? (Escribe un número)")
        else:
            return ("No encontré ese producto. Por favor, verifica el nombre o escribe solo el producto sin 'comprar'.\n"
                    "Ejemplo: *varilla*, *cemento*, *pintura*.")

    # Buscar producto normal (sin "comprar")
    clave, producto = buscar_producto(mensaje)
    if clave:
        # Mostrar información del producto y sugerir compra
        return formatear_producto(clave, producto)

    # ============================================================
    # CASO 4: MENSAJE NO RECONOCIDO
    # ============================================================
    return (f"Lo siento, no entendí tu mensaje, {estado['nombre']}. 🤔\n\n"
            "Puedes:\n"
            "• Escribir el *nombre de un producto* (ej. 'varilla', 'cemento', 'pintura').\n"
            "• Usar comandos: *dirección*, *horario*, *asesor*.\n"
            "• Iniciar una compra: *'comprar varilla'*.\n\n"
            "¿Qué deseas hacer?")

# ============================================================
# 4. ENDPOINT WEBHOOK PARA TWILIO
# ============================================================

@app.route('/webhook', methods=['POST'])
def webhook():
    # Obtener datos de Twilio
    incoming_msg = request.values.get('Body', '').strip()
    user_number = request.values.get('From', '')

    # Obtener respuesta del bot
    response_text = obtener_respuesta(incoming_msg, user_number)

    # Crear respuesta Twilio
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)

    return Response(str(resp), mimetype='application/xml')

# ============================================================
# 5. INICIO DEL SERVIDOR
# ============================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
