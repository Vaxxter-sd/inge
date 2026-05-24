from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import smtplib
from email.message import EmailMessage
from datetime import datetime
import threading   # Opcional, para no bloquear si quieres

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN DE LA BASE DE DATOS (Railway)
DB_CONFIG = {
    'host': 'mysql.railway.internal',
    'user': 'root',
    'password': 'uAWtpgQEHbDcTFiJOmxratreEnpIJXjb',
    'database': 'railway',
    'port': 38086
}

# CONFIGURACIÓN DEL CORREO (Gmail)
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'user': 'sescolarinformes@gmail.com',
    'password': 'buwu imql jbol brae'
}

@app.route('/nuevo_lead', methods=['POST'])
def nuevo_lead():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        correo = data.get('correo')
        tipo_escuela = data.get('tipo_escuela')
        fecha = datetime.now()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verificar si el correo ya existe (evitar duplicados)
        cursor.execute("SELECT id FROM leads WHERE correo = %s", (correo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'mensaje': 'Este correo ya está registrado.'}), 400

        # Insertar lead (la tabla ya existe, no se crea)
        sql = "INSERT INTO leads (nombre, correo, tipo_escuela, fecha_registro) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, correo, tipo_escuela, fecha))
        conn.commit()
        cursor.close()
        conn.close()

        # Enviar correo (puedes dejarlo así o ponerlo en hilo para que no bloquee)
        msg = EmailMessage()
        msg['Subject'] = f'¡Gracias por contactarnos, {nombre}! - SEscolar.ce'
        msg['From'] = SMTP_CONFIG['user']
        msg['To'] = correo
        msg.set_content(f'Hola {nombre},\nGracias por tu interés. En breve te contactaremos.\n\nSi no ves este correo en tu bandeja de entrada, revisa tu carpeta de spam.')
        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as smtp:
            smtp.starttls()
            smtp.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
            smtp.send_message(msg)

        return jsonify({'status': 'ok', 'mensaje': 'Lead guardado y correo enviado'}), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
