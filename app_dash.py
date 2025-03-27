import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import firebase_admin
from firebase_admin import credentials, db
import time

# Configura Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Reemplaza con tu archivo JSON de Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sensor-de-agua-iot-default-rtdb.firebaseio.com/'  # Reemplaza con la URL de tu base de datos
})

# Inicializa Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Monitor de Sensor de Agua", style={'textAlign': 'center'}),
    dcc.Graph(id="grafico-sensor"),
    dcc.Interval(
        id="intervalo-actualizacion",
        interval=2000,  # Actualizar cada 2 segundos
        n_intervals=0
    )
])

# Callback para actualizar el gráfico
@app.callback(
    Output("grafico-sensor", "figure"),
    [Input("intervalo-actualizacion", "n_intervals")]
)
def actualizar_grafico_dash(n):
    # Recuperar los datos desde Firebase
    ref = db.reference('sensor_agua')
    datos = ref.order_by_key().limit_to_last(10).get()

    if datos:
        porcentajes = []
        tiempos = []
        for key in datos:
            entry = datos[key]
            porcentajes.append(entry["porcentaje"])
            tiempos.append(entry["timestamp"])
        
        # Crear el gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tiempos,
            y=porcentajes,
            mode="lines+markers",
            name="Sensor de Agua"
        ))
        fig.update_layout(
            title="Lecturas en tiempo real",
            xaxis_title="Tiempo",
            yaxis_title="Porcentaje",
            template="plotly_dark"
        )
        return fig
    else:
        return go.Figure()

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True, port=8050)
