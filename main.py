import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QComboBox, QMessageBox
from PyQt5.uic import loadUi

# Clase principal del programa
class VerduleriaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)

        self.productos = []  # Lista para almacenar productos
        self.compra_venta = []  # Lista para almacenar movimientos de compra/venta

        # Cargar datos desde un JSON si existe
        self.load_data()

        # Conectar botones del menú
        self.bt_productos_vender.clicked.connect(self.abrir_productos_a_vender)
        self.bt_consultar_precio.clicked.connect(self.abrir_consultar_precio_unitario)
        self.bt_compra_productos.clicked.connect(self.abrir_compra_productos)
        self.bt_consulta_inventario.clicked.connect(self.mostrar_inventario)
        self.bt_datos_maestros.clicked.connect(self.abrir_datos_maestros)
        self.bt_lista_compras_ventas.clicked.connect(self.mostrar_lista_compras_ventas)  

    def load_data(self):
        try:
            with open("productos.json", "r") as file:
                self.productos = json.load(file)
        except FileNotFoundError:
            self.productos = []

        try:
            with open("compra_venta.json", "r") as file:
                self.compra_venta = json.load(file)
        except FileNotFoundError:
            self.compra_venta = []

    def save_data(self):
        with open("productos.json", "w") as file:
            json.dump(self.productos, file)
        with open("compra_venta.json", "w") as file:
            json.dump(self.compra_venta, file)

    def abrir_productos_a_vender(self):
        dialog = ProductosAVenderDialog(self.productos, self.compra_venta)
        dialog.exec_()

    def abrir_consultar_precio_unitario(self):
        dialog = ConsultarPrecioUnitarioDialog(self.productos)
        dialog.exec_()

    def abrir_compra_productos(self):
        dialog = CompraProductosDialog(self.productos, self.compra_venta)
        dialog.exec_()

    def mostrar_inventario(self):
        QMessageBox.information(self, "Inventario", "Esta funcionalidad está en desarrollo.")

    def abrir_datos_maestros(self):
        dialog = DatosMaestrosDialog(self.productos, self.save_data)
        dialog.exec_()

    def mostrar_lista_compras_ventas(self):
        dialog = ListaCompraVentaDialog(self.compra_venta)
        dialog.exec_()

# Diálogo para "Lista de Compras y Ventas"
class ListaCompraVentaDialog(QDialog):
    def __init__(self, compra_venta):
        super().__init__()
        loadUi("lista_compra_venta.ui", self)
        self.compra_venta = compra_venta

        self.cargar_datos()

    def cargar_datos(self):
        self.tableWidgetCompraVenta.setRowCount(0)
        for row in self.compra_venta:
            row_position = self.tableWidgetCompraVenta.rowCount()
            self.tableWidgetCompraVenta.insertRow(row_position)

            self.tableWidgetCompraVenta.setItem(row_position, 0, QTableWidgetItem(row['FechaOperacion']))
            self.tableWidgetCompraVenta.setItem(row_position, 1, QTableWidgetItem(row['TipoOperacion']))
            self.tableWidgetCompraVenta.setItem(row_position, 2, QTableWidgetItem(row['DenominacionProducto']))
            self.tableWidgetCompraVenta.setItem(row_position, 3, QTableWidgetItem(row['Tipo']))
            self.tableWidgetCompraVenta.setItem(row_position, 4, QTableWidgetItem(row['UnidadMedida']))
            self.tableWidgetCompraVenta.setItem(row_position, 5, QTableWidgetItem(str(row['Cantidad'])))
            self.tableWidgetCompraVenta.setItem(row_position, 6, QTableWidgetItem(str(row['PrecioUnitario'])))
            self.tableWidgetCompraVenta.setItem(row_position, 7, QTableWidgetItem(str(row['PrecioTotal'])))

# Diálogo para "Productos a Vender"
class ProductosAVenderDialog(QDialog):
    def __init__(self, productos, compra_venta):
        super().__init__()
        loadUi("productos_a_vender.ui", self)
        self.productos = productos
        self.compra_venta = compra_venta

        self.cb_producto.currentIndexChanged.connect(self.actualizar_datos_producto)
        self.bt_guardar.clicked.connect(self.guardar_venta)
        self.bt_cancelar.clicked.connect(self.close)

        self.cargar_productos()
        self.le_fecha.setText(datetime.now().strftime("%Y-%m-%d"))
        self.le_tipo_operacion.setText("VENTA")
        self.le_tipo_operacion.setEnabled(False)

    def cargar_productos(self):
        self.cb_producto.addItem("Seleccionar")
        for producto in self.productos:
            self.cb_producto.addItem(producto["Denominacion"])

    def actualizar_datos_producto(self):
        index = self.cb_producto.currentIndex() - 1
        if index >= 0:
            producto = self.productos[index]
            self.le_tipo.setText(producto["Tipo"])
            self.le_unidad_medida.setText(producto["UnidadMedida"])
            self.le_precio_unitario.setText(str(producto["PrecioUnitario"]))

    def guardar_venta(self):
        if self.cb_producto.currentIndex() == 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return

        cantidad = float(self.le_cantidad.text())
        precio_unitario = float(self.le_precio_unitario.text())
        total = cantidad * precio_unitario

        movimiento = {
            "FechaOperacion": self.le_fecha.text(),
            "TipoOperacion": self.le_tipo_operacion.text(),
            "DenominacionProducto": self.cb_producto.currentText(),
            "Tipo": self.le_tipo.text(),
            "UnidadMedida": self.le_unidad_medida.text(),
            "Cantidad": cantidad,
            "PrecioUnitario": precio_unitario,
            "PrecioTotal": total
        }

        self.compra_venta.append(movimiento)
        QMessageBox.information(self, "Éxito", "Venta registrada exitosamente.")
        self.close()

# Diálogo para "Consultar Precio Unitario"
class ConsultarPrecioUnitarioDialog(QDialog):
    def __init__(self, productos):
        super().__init__()
        loadUi("consultar_precio_unitario.ui", self)
        self.productos = productos

        self.bt_buscar.clicked.connect(self.buscar_precio)
        self.bt_nueva_busqueda.clicked.connect(self.nueva_busqueda)

    def buscar_precio(self):
        nombre_producto = self.le_producto.text()
        for producto in self.productos:
            if producto["Denominacion"] == nombre_producto:
                self.le_precio_unitario.setText(str(producto["PrecioUnitario"]))
                self.le_unidad_medida.setText(producto["UnidadMedida"])
                self.le_producto.setEnabled(False)
                return
        QMessageBox.warning(self, "Error", "Producto no encontrado.")

    def nueva_busqueda(self):
        self.le_producto.clear()
        self.le_precio_unitario.clear()
        self.le_unidad_medida.clear()
        self.le_producto.setEnabled(True)

# Diálogo para "Compra de Productos"
class CompraProductosDialog(QDialog):
    def __init__(self, productos, compra_venta):
        super().__init__()
        loadUi("compra_productos.ui", self)
        self.productos = productos
        self.compra_venta = compra_venta

        self.cb_producto.currentIndexChanged.connect(self.actualizar_datos_producto)
        self.bt_guardar.clicked.connect(self.guardar_compra)
        self.bt_cancelar.clicked.connect(self.close)

        self.cargar_productos()
        self.le_fecha.setText(datetime.now().strftime("%Y-%m-%d"))
        self.le_tipo_operacion.setText("COMPRA")
        self.le_tipo_operacion.setEnabled(False)

    def cargar_productos(self):
        self.cb_producto.addItem("Seleccionar")
        for producto in self.productos:
            self.cb_producto.addItem(producto["Denominacion"])

    def actualizar_datos_producto(self):
        index = self.cb_producto.currentIndex() - 1
        if index >= 0:
            producto = self.productos[index]
            self.le_tipo.setText(producto["Tipo"])
            self.le_unidad_medida.setText(producto["UnidadMedida"])

    def guardar_compra(self):
        if self.cb_producto.currentIndex() == 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return

        cantidad = float(self.le_cantidad.text())
        precio_unitario = float(self.le_precio_unitario.text())
        total = cantidad * precio_unitario

        movimiento = {
            "FechaOperacion": self.le_fecha.text(),
            "TipoOperacion": self.le_tipo_operacion.text(),
            "DenominacionProducto": self.cb_producto.currentText(),
            "Tipo": self.le_tipo.text(),
            "UnidadMedida": self.le_unidad_medida.text(),
            "Cantidad": cantidad,
            "PrecioUnitario": precio_unitario,
            "PrecioTotal": total
        }

        self.compra_venta.append(movimiento)
        QMessageBox.information(self, "Éxito", "Compra registrada exitosamente.")
        self.close()

# Diálogo para "Datos Maestros de Productos"
class DatosMaestrosDialog(QDialog):
    def __init__(self, productos, save_data_callback):
        super().__init__()
        loadUi("datos_maestros.ui", self)
        self.productos = productos
        self.save_data_callback = save_data_callback

        self.cargar_productos()
        self.bt_guardar.clicked.connect(self.guardar_productos)
        self.btnIngresar.clicked.connect(self.agregar_producto)

    def cargar_productos(self):
        self.tabla_productos.setRowCount(len(self.productos))
        for row, producto in enumerate(self.productos):
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(producto["Denominacion"]))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(producto["Tipo"]))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(producto["UnidadMedida"]))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(producto["PrecioUnitario"])))

    def agregar_producto(self):
        row_count = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(row_count)

    def guardar_productos(self):
        productos_actualizados = []
        for row in range(self.tabla_productos.rowCount()):
            denominacion_item = self.tabla_productos.item(row, 0)
            tipo_item = self.tabla_productos.item(row, 1)
            unidad_medida_item = self.tabla_productos.item(row, 2)
            precio_unitario_item = self.tabla_productos.item(row, 3)

            if not (denominacion_item and tipo_item and unidad_medida_item and precio_unitario_item):
                QMessageBox.warning(self, "Error", "Complete todos los campos de la tabla.")
                return

            producto = {
                "Denominacion": denominacion_item.text(),
                "Tipo": tipo_item.text(),
                "UnidadMedida": unidad_medida_item.text(),
                "PrecioUnitario": float(precio_unitario_item.text())
            }
            productos_actualizados.append(producto)

        self.productos = productos_actualizados
        self.save_data_callback()
        QMessageBox.information(self, "Éxito", "Datos maestros guardados exitosamente.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VerduleriaApp()
    window.show()
    sys.exit(app.exec_())
