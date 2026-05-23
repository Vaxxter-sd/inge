from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN DE LA BASE DE DATOS (valores directos de Railway)
DB_CONFIG = {
    'host': 'mysql.railway.internal',   # ← cámbialo por el MYSQLHOST de tu BD
    'user': 'root',                    # ← MYSQLUSER
    'password': 'uAWtpgQEHbDcTFiJOmxratreEnpIJXjb',  # ← MYSQLPASSWORD
    'database': 'railway',             # ← MYSQLDATABASE
    'port': 38086                      # ← MYSQLPORT
}

# CONFIGURACIÓN DEL CORREO
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

        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) NOT NULL,
                tipo_escuela VARCHAR(50) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insertar lead
        sql = "INSERT INTO leads (nombre, correo, tipo_escuela, fecha_registro) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, correo, tipo_escuela, fecha))
        conn.commit()
        cursor.close()
        conn.close()

        # Enviar correo
        msg = EmailMessage()
        msg['Subject'] = f'¡Gracias por contactarnos, {nombre}! - SEscolar.ce'
        msg['From'] = SMTP_CONFIG['user']
        msg['To'] = correo
        msg.set_content(f'Hola {nombre},\nGracias por tu interés. En breve te contactaremos.')
        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as smtp:
            smtp.starttls()
            smtp.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
            smtp.send_message(msg)

        return jsonify({'status': 'ok', 'mensaje': 'Lead guardado'}), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
