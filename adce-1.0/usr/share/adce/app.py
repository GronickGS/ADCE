import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import csv 
import pathlib

class AplicacionGestorComponentes:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador Electronica")

        #============================================================================!
        # anchura y altura de la pantalla
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()

        # anchura y altura de la ventana    
        ancho_ventana = 1000  
        alto_ventana = 450  

        # Calcular la posición x y y para centrar la ventana
        posicion_x = (ancho_pantalla - ancho_ventana) // 2
        posicion_y = (alto_pantalla - alto_ventana) // 2

        # posición de la ventana
        root.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")
        #============================================================================!

        # Conexión a la base de datos SQLite
        self.conexion = sqlite3.connect('data.db')
        self.crear_tabla()

        # Marco principal
        self.marco_principal = tk.Frame(root)
        self.marco_principal.pack(fill=tk.BOTH, expand=True)

        # Título del sistema
        self.titulo_sistema = tk.Label(self.marco_principal, text="SISTEMA GS", font=("Courier New", 14, "bold"),)
        self.titulo_sistema.pack(side=tk.TOP, pady=10)

        # Marco para agregar componentes
        self.marco_agregar = tk.Frame(self.marco_principal, padx=10, pady=10)
        self.marco_agregar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cargar la imagen y redimensionarla
        self.imagen_usuario = tk.PhotoImage(file="image.png").subsample(5, 5)  # tamaño de imagen

        self.etiqueta_imagen = tk.Label(self.marco_agregar, image=self.imagen_usuario)
        self.etiqueta_imagen.grid(row=0, column=1, padx=(0, 50), pady=0, sticky="nsew")

        # widgets para agregar componentes
        #===================================================================================================== NOMBRE
        self.etiqueta_nombre = tk.Label(self.marco_agregar, text="Nombre:", font=("Courier New", 10, "bold"))
        self.etiqueta_nombre.grid(row=1, column=0, sticky="e", padx=10, pady=5)

        self.entrada_nombre = tk.Entry(self.marco_agregar)
        self.entrada_nombre.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

         #===================================================================================================== SERIE

        self.etiqueta_Serie = tk.Label(self.marco_agregar, text="serie:", font=("Courier New", 10, "bold"),)
        self.etiqueta_Serie.grid(row=2, column=0, sticky="e", padx=10, pady=5)

        self.entrada_Serie = tk.Entry(self.marco_agregar)
        self.entrada_Serie.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")


         #===================================================================================================== CANTIDAD
        # Nuevo campo para ingresar cantidad
        self.etiqueta_cantidad = tk.Label(self.marco_agregar, text="Cantidad:", font=("Courier New", 10, "bold"))
        self.etiqueta_cantidad.grid(row=3, column=0, sticky="e", padx=10, pady=5)

        self.entrada_cantidad = tk.Entry(self.marco_agregar, validate="key", validatecommand=(root.register(self.es_numero), '%P'))
        self.entrada_cantidad.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

        # Establecer valor predeterminado en "1" para la entrada cantidad
        self.entrada_cantidad.insert(0, "1")

        #===================================================================================================== BOTON AGREGAR
        self.boton_agregar = tk.Button(self.marco_agregar, text="Agregar", font=("Courier New", 10, "bold"), command=self.agregar_componente, bg="red", fg="white", borderwidth=2, relief="raised")
        self.boton_agregar.grid(row=5, column=0, columnspan=2, pady=10)

        # Campo de búsqueda
        self.marco_buscar = tk.Frame(self.marco_principal)
        self.marco_buscar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.etiqueta_buscar = tk.Label(self.marco_buscar, text="Buscar:", font=("Courier New", 10, "bold"))
        self.etiqueta_buscar.pack(side=tk.LEFT, padx=(0, 5))

        self.entrada_buscar = tk.Entry(self.marco_buscar)
        self.entrada_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entrada_buscar.bind('<KeyRelease>', self.buscar_componente)

        # Mostrar componentes
        self.marco_mostrar = tk.Frame(self.marco_principal, padx=10, pady=10)
        self.marco_mostrar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Crear el árbol para mostrar componentes
        self.arbol = ttk.Treeview(self.marco_mostrar, columns=('Nombre', 'serie', 'cantidad'), show='headings')
        self.arbol.heading('Nombre', text='Nombre')
        self.arbol.heading('serie', text='Serie')
        self.arbol.heading('cantidad', text='Cantidad')
        self.arbol.pack(expand=True, fill='both')

        # Botón para exportar a CSV
        self.boton_exportar = tk.Button(self.marco_mostrar, text="Exportar a CSV", font=("Courier New", 10, "bold"), command=self.exportar_a_csv, bg="red", fg="white", borderwidth=2, relief="raised")
        self.boton_exportar.pack(side=tk.BOTTOM, pady=10)

        # Marco para los botones de edición y borrado
        self.marco_botones = tk.Frame(self.marco_mostrar)
        self.marco_botones.pack(side=tk.BOTTOM)

        # Botones para editar y borrar componente
        self.boton_editar = tk.Button(self.marco_botones, text="Editar", font=("Courier New", 10, "bold"), command=self.editar_componente, bg="red", fg="white", borderwidth=2, relief="raised")
        self.boton_editar.pack(side=tk.LEFT, padx=5, pady=(10, 0))  # Ajusta el margen superior (top) a 5

        self.boton_borrar = tk.Button(self.marco_botones, text="Borrar", font=("Courier New", 10, "bold"),command=self.borrar_componente, bg="red", fg="white", borderwidth=2, relief="raised")
        self.boton_borrar.pack(side=tk.LEFT, padx=5, pady=(10, 0))  # Ajusta el margen superior (top) a 5

        # Cargar componentes existentes
        self.cargar_componentes()

    
    def buscar_componente(self, event=None):
        texto_busqueda = self.entrada_buscar.get().lower()
        componentes_filtrados = []

        for componente in self.componentes:
            nombre = componente[1].lower()
            Serie = componente[2].lower()
            if texto_busqueda in nombre or texto_busqueda in Serie:
                componentes_filtrados.append(componente)

        self.mostrar_componentes(componentes_filtrados)

    def crear_tabla(self):
        cursor = self.conexion.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS componentes
                        (id INTEGER PRIMARY KEY, nombre TEXT, Serie TEXT, cantidad INTEGER)''')  # Agregar la columna "cantidad"
        self.conexion.commit()


    def agregar_componente(self):
        nombre = self.entrada_nombre.get().capitalize()  # Capitaliza la primera letra del nombre
        Serie = self.entrada_Serie.get()
        cantidad = self.entrada_cantidad.get()

        if nombre and Serie and cantidad:  # Verificar que todos los campos estén completos
            cursor = self.conexion.cursor()
            cursor.execute('INSERT INTO componentes (nombre, Serie, cantidad) VALUES (?, ?, ?)', (nombre, Serie, cantidad))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Componente agregado correctamente")
            self.limpiar_entradas()
            self.cargar_componentes()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def limpiar_entradas(self):
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_Serie.delete(0, tk.END)
        self.entrada_cantidad.delete(0, tk.END)

    def cargar_componentes(self):
        cursor = self.conexion.cursor()
        cursor.execute('SELECT * FROM componentes ORDER BY nombre ASC')  # Ordenar por nombre de forma ascendente
        self.componentes = cursor.fetchall()
        self.mostrar_componentes()

    def mostrar_componentes(self, componentes=None):
        if componentes is None:
            componentes = self.componentes

        # Limpiar árbol antes de volver a cargar los componentes
        for row in self.arbol.get_children():
            self.arbol.delete(row)

        # Insertar componentes
        for componente in componentes:
            self.arbol.insert('', 'end', values=(componente[1], componente[2], componente[3]))

    def exportar_a_csv(self):
        if self.componentes:
            nombre_archivo = "componentes.csv"
            with open(nombre_archivo, 'w', newline='') as csvfile:
                nombres_columnas = ['Nombre', 'serie', 'cantidad']
                escritor_csv = csv.DictWriter(csvfile, fieldnames=nombres_columnas)
                escritor_csv.writeheader()
                for componente in self.componentes:
                    escritor_csv.writerow({'Nombre': componente[1], 'serie': componente[2], 'cantidad': componente[3]})
            messagebox.showinfo("Éxito", f"componentes exportados a {nombre_archivo}")
        else:
            messagebox.showerror("Error", "No hay componentes para exportar")
    
    def editar_componente(self):
        elemento_seleccionado = self.arbol.selection()
        if elemento_seleccionado:
            nombre = self.arbol.item(elemento_seleccionado, 'values')[0]
            Serie = self.arbol.item(elemento_seleccionado, 'values')[1]
            cantidad = self.arbol.item(elemento_seleccionado, 'values')[2]

            ventana_editar = tk.Toplevel(self.root)
            ventana_editar.title("Editar componente")

            etiqueta_nombre = tk.Label(ventana_editar, text="Nombre:")
            etiqueta_nombre.grid(row=0, column=0, padx=10, pady=5)
            entrada_nombre = tk.Entry(ventana_editar)
            entrada_nombre.insert(0, nombre)
            entrada_nombre.grid(row=0, column=1, padx=10, pady=5)

            etiqueta_Serie = tk.Label(ventana_editar, text="serie:")
            etiqueta_Serie.grid(row=1, column=0, padx=10, pady=5)
            entrada_Serie = tk.Entry(ventana_editar)
            entrada_Serie.insert(0, Serie)
            entrada_Serie.grid(row=1, column=1, padx=10, pady=5)

            entrada_cantidad = tk.Label(ventana_editar, text="cantidad:")
            entrada_cantidad.grid(row=2, column=0, padx=10, pady=5)
            entrada_cantidad = tk.Entry(ventana_editar)
            entrada_cantidad.insert(0, cantidad)
            entrada_cantidad.grid(row=2, column=1, padx=10, pady=5)

            boton_guardar = tk.Button(ventana_editar, text="Guardar Cambios", command=lambda: self.guardar_cambios(elemento_seleccionado, entrada_nombre.get(), entrada_Serie.get(),entrada_cantidad.get(), ventana_editar), bg="red", fg="white")
            boton_guardar.grid(row=3, column=0, columnspan=2, pady=10)

    def borrar_componente(self):
        elemento_seleccionado = self.arbol.selection()
        if elemento_seleccionado:
            confirmacion = messagebox.askyesno("Eliminar componente", "¿Está seguro que desea eliminar este componente?")
            if confirmacion:
                cursor = self.conexion.cursor()
                cursor.execute('DELETE FROM componentes WHERE nombre=? AND Serie=?',
                            (self.arbol.item(elemento_seleccionado, 'values')[0], self.arbol.item(elemento_seleccionado, 'values')[1]))
                self.conexion.commit()
                self.cargar_componentes()

    def guardar_cambios(self, elemento_seleccionado, nuevo_nombre, nuevo_Serie, nuevo_cantidad, ventana_editar):
        cursor = self.conexion.cursor()
        cursor.execute('UPDATE componentes SET nombre=?, Serie=?, cantidad=?  WHERE nombre=? AND Serie=? AND cantidad=?',
                       (nuevo_nombre, nuevo_Serie, nuevo_cantidad, self.arbol.item(elemento_seleccionado, 'values')[0], self.arbol.item(elemento_seleccionado, 'values')[1],  self.arbol.item(elemento_seleccionado, 'values')[2]))
        self.conexion.commit()
        messagebox.showinfo("Éxito", "componente actualizado correctamente")
        ventana_editar.destroy()
        self.cargar_componentes()

    def es_numero(self, texto):
        return texto.isdigit() or texto == ""



if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionGestorComponentes(root)
    root.mainloop()