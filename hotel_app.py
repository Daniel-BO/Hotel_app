import sqlite3
import bcrypt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QComboBox
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLineEdit, QLabel, QFormLayout, QMessageBox, QListWidget
)

DB_NAME = "hotel.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        with open("hotel_schema.sql", "r") as f:
            conn.executescript(f.read())
        # Agregar habitaciones si no existen
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM habitaciones")
        if cursor.fetchone()[0] == 0:
            habitaciones = [
                ("101", "Individual", 50.0),
                ("102", "Doble", 80.0),
                ("201", "Suite", 150.0)
            ]
            cursor.executemany(
                "INSERT INTO habitaciones (numero, tipo, precio_por_noche) VALUES (?, ?, ?)",
                habitaciones
            )
###parte donde se crea el usuario admin esta parque se elimino para que este encriptado el administrador, se maneja con otro scrip
        conn.commit()

class HotelApp(QWidget):
    def __init__(self, usuario_actual, rol_actual):
        super().__init__()
        self.usuario = usuario_actual
        self.rol = rol_actual
        self.setWindowTitle(f"Mini OPERA Hotel PMS - Sesión de {self.usuario}")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()
        self.huesped_form()
        self.habitaciones_disponibles()
        self.setLayout(self.layout)
        if self.rol == "admin":
          self.btn_gestion_usuarios = QPushButton("Gestión de Personal")
          self.btn_gestion_usuarios.clicked.connect(self.abrir_gestion_usuarios)
          self.layout.addWidget(self.btn_gestion_usuarios)

    def abrir_gestion_usuarios(self):
      dialog = GestionUsuarios()
      dialog.exec_()
        

    def huesped_form(self):
        form_layout = QFormLayout()

        self.nombre = QLineEdit()
        self.documento = QLineEdit()
        self.telefono = QLineEdit()
        self.btn_guardar = QPushButton("Registrar Huésped")
        self.btn_guardar.clicked.connect(self.registrar_huesped)

        form_layout.addRow("Nombre:", self.nombre)
        form_layout.addRow("Documento:", self.documento)
        form_layout.addRow("Teléfono:", self.telefono)
        form_layout.addWidget(self.btn_guardar)

        self.layout.addLayout(form_layout)

    def habitaciones_disponibles(self):
        self.lista = QListWidget()
        self.btn_refrescar = QPushButton("Ver Habitaciones Disponibles")
        self.btn_refrescar.clicked.connect(self.cargar_disponibles)

        self.layout.addWidget(self.lista)
        self.layout.addWidget(self.btn_refrescar)

    def registrar_huesped(self):
        nombre = self.nombre.text()
        doc = self.documento.text()
        tel = self.telefono.text()

        if not nombre or not doc:
            QMessageBox.warning(self, "Error", "Nombre y documento son obligatorios")
            return

        with sqlite3.connect(DB_NAME) as conn:
            try:
                conn.execute("INSERT INTO huespedes (nombre, documento, telefono) VALUES (?, ?, ?)",
                             (nombre, doc, tel))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Huésped registrado")
                self.nombre.clear()
                self.documento.clear()
                self.telefono.clear()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Documento duplicado")

    def cargar_disponibles(self):
        self.lista.clear()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numero, tipo, precio_por_noche FROM habitaciones WHERE disponible = 1")
            habitaciones = cursor.fetchall()
            for h in habitaciones:
                self.lista.addItem(f"Habitación {h[0]} - {h[1]} - ${h[2]:.2f}")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Hotel PMS")
        self.setGeometry(100, 100, 300, 150)

        layout = QFormLayout()
        self.usuario_input = QLineEdit()
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Iniciar sesión")
        self.login_btn.clicked.connect(self.verificar_login)

        layout.addRow("Usuario:", self.usuario_input)
        layout.addRow("Contraseña:", self.contrasena_input)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)
        
    def verificar_login(self):
	    usuario = self.usuario_input.text()
	    contrasena = self.contrasena_input.text()
	
	    with sqlite3.connect(DB_NAME) as conn:
	        cursor = conn.cursor()
	        cursor.execute("SELECT contrasena, rol FROM usuarios WHERE usuario = ?", (usuario,))
	        resultado = cursor.fetchone()
	        if resultado:
	            hash_guardado, rol = resultado
	            if bcrypt.checkpw(contrasena.encode('utf-8'),hash_guardado):
	                self.close()
	                self.main_app = HotelApp(usuario, rol)
	                self.main_app.show()
	                return
	
	    QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")


class GestionUsuarios(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Personal")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()
        self.lista_usuarios = QListWidget()
        self.btn_refrescar = QPushButton("Actualizar lista")
        self.btn_nuevo = QPushButton("Crear nuevo usuario")

        self.btn_refrescar.clicked.connect(self.cargar_usuarios)
        self.btn_nuevo.clicked.connect(self.crear_usuario)

        self.layout.addWidget(QLabel("Usuarios registrados:"))
        self.layout.addWidget(self.lista_usuarios)
        self.layout.addWidget(self.btn_refrescar)
        self.layout.addWidget(self.btn_nuevo)

        self.setLayout(self.layout)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.lista_usuarios.clear()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT usuario, rol FROM usuarios")
            for usuario, rol in cursor.fetchall():
                self.lista_usuarios.addItem(f"{usuario} ({rol})")

    def crear_usuario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo usuario")
        layout = QFormLayout()

        usuario_input = QLineEdit()
        contrasena_input = QLineEdit()
        contrasena_input.setEchoMode(QLineEdit.Password)
        rol_input = QComboBox()
        rol_input.addItems(["recepcionista", "admin"])

        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(lambda: self.guardar_usuario(
            dialog, usuario_input.text(), contrasena_input.text(), rol_input.currentText()
        ))

        layout.addRow("Usuario:", usuario_input)
        layout.addRow("Contraseña:", contrasena_input)
        layout.addRow("Rol:", rol_input)
        layout.addWidget(btn_guardar)

        dialog.setLayout(layout)
        dialog.exec_()

    def guardar_usuario(self, dialog, usuario, contrasena, rol):
	    if not usuario or not contrasena:
	        QMessageBox.warning(self, "Error", "Debe ingresar usuario y contraseña")
	        return
	
	    hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
	
	    with sqlite3.connect(DB_NAME) as conn:
	        try:
	            conn.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
	                         (usuario, hashed, rol))
	            conn.commit()
	            QMessageBox.information(self, "Éxito", "Usuario creado correctamente")
	            dialog.close()
	            self.cargar_usuarios()
	        except sqlite3.IntegrityError:
	            QMessageBox.warning(self, "Error", "Nombre de usuario ya existe")


if __name__ == "__main__":
    init_db()
    app = QApplication([])
    login = LoginWindow()
    login.show()
    app.exec_()
    
