import seaborn as sns  # Estilo para las gráficas
import matplotlib.pyplot as plt
import serial
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import firebase_admin
from firebase_admin import credentials, db

# Configura Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Reemplaza con tu archivo JSON de Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sensor-de-agua-iot-default-rtdb.firebaseio.com/'  # Reemplaza con la URL de tu base de datos
})

# Configura el estilo de las gráficas con Seaborn
sns.set_style("darkgrid")

# Configura el puerto serial (ajusta 'COM7' según tu sistema)
arduino = serial.Serial('COM7', 9600)  # Cambia COM7 por el puerto correspondiente

# Listas para almacenar datos
datos = []
porcentajes = []
niveles = []
tiempo = []  # Tiempos para graficarlos

def clasificar_nivel(porcentaje):
    """Clasifica el nivel como Mínimo, Medio o Máximo."""
    if porcentaje < 10:  # Menor a 10%
        return "Mínimo"
    elif 10 <= porcentaje < 28:  # Entre 10% y 28%
        return "Medio"
    else:  # Mayor o igual a 28%
        return "Máximo"

print("Recibiendo datos del Arduino...")

try:
    while True:
        lectura = arduino.readline().decode().strip()  # Lee los datos enviados por el Arduino
        if lectura.isdigit():  # Verifica que los datos sean un número válido
            valor = int(lectura)  # Convierte el dato a entero
            datos.append(valor)  # Agrega el valor a la lista de datos
            
            # Calcular el porcentaje
            porcentaje = (valor / 1023) * 100
            porcentajes.append(porcentaje)
            
            # Clasificar el nivel
            nivel = clasificar_nivel(porcentaje)
            niveles.append(nivel)
            
            # Guardar el momento de la lectura
            tiempo_actual = datetime.now().strftime("%H:%M:%S")
            tiempo.append(tiempo_actual)

            # Enviar los datos a Firebase
            ref = db.reference('sensor_agua')  # Referencia a la base de datos en Firebase
            ref.push({
                'porcentaje': porcentaje,
                'nivel': nivel,
                'timestamp': tiempo_actual
            })

            # Imprimir en la consola para retroalimentación en tiempo real
            print(f"Valor: {valor}, Porcentaje: {porcentaje:.2f}%, Nivel: {nivel}, Enviado a Firebase.")
            
            # Graficar en tiempo real con Matplotlib
            plt.cla()  # Limpia la gráfica
            color = "blue" if nivel == "Mínimo" else "green" if nivel == "Medio" else "red"
            plt.plot(porcentajes, label=f"Sensor de agua (%) - {nivel}", marker="o", linestyle="-", color=color)
            plt.xticks(rotation=45)  # Rotar etiquetas del eje X
            plt.xlabel("Tiempo")
            plt.ylabel("Porcentaje (%)")
            plt.title(f"Lecturas en tiempo real: Nivel ({nivel})")
            plt.legend()
            plt.tight_layout()  # Ajusta los márgenes automáticamente
            # Guardar la gráfica como archivo de imagen
            nombre_imagen = "grafica_sensor.png"  # Nombre del archivo
            plt.savefig(nombre_imagen)  # Guarda la gráfica en el directorio del proyecto
            print(f"Gráfica guardada como {nombre_imagen}")
            plt.pause(0.1)  # Pausa breve para actualizar la gráfica
except KeyboardInterrupt:
    print("\nFinalizando captura...")
    arduino.close()  # Cierra la conexión serial con el Arduino
    plt.show()  # Muestra la gráfica final

# Generar la gráfica interactiva con Plotly
fig = make_subplots(rows=1, cols=1)
fig.add_trace(go.Scatter(
    x=tiempo,
    y=porcentajes,
    mode="lines+markers",
    name="Sensor de agua (%)",
    line=dict(color="blue"),
    marker=dict(size=8)
))

fig.update_layout(
    title="Lecturas capturadas del sensor de agua en porcentaje",
    xaxis_title="Tiempo",
    yaxis_title="Porcentaje del sensor (%)",
    template="plotly_dark"  # Cambia el estilo a un diseño oscuro interactivo
)

fig.show()
