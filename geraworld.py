import tkinter as tk
from PIL import Image, ImageTk, ImageOps
from pathlib import Path
from tkinter import messagebox, filedialog 
import threading 
from playsound import playsound 
COLOR_FONDO = "#2b2b2b"

# --- CONTROL DE AUDIO ---
MUSICA_SONANDO = threading.Event() 
AUDIO_FILE = 'smb2-title.mp3' 

def loop_musica_fondo():
    """Función que reproduce la música del menú en un bucle eterno."""
    global MUSICA_SONANDO
    
    while MUSICA_SONANDO.is_set(): 
        try:
            # playsound bloquea el hilo hasta que termina la canción.
            playsound(AUDIO_FILE)
        except Exception as e:
            print(f"Error al reproducir audio: {e}. Asegúrate de que el archivo '{AUDIO_FILE}' exista.")
            # Si hay error, detenemos el bucle para no causar errores recurrentes
            MUSICA_SONANDO.clear() 
            break
        # Si la canción termina, se reinicia inmediatamente.
        
def iniciar_musica():
    """Inicia el hilo de la música si no está sonando."""
    global MUSICA_SONANDO
    if not MUSICA_SONANDO.is_set():
        MUSICA_SONANDO.set()
        hilo_musica = threading.Thread(target=loop_musica_fondo)
        hilo_musica.daemon = True # El hilo muere si el programa principal se cierra
        hilo_musica.start()

def detener_musica():
    """Detiene el bucle de la música."""
    global MUSICA_SONANDO
    MUSICA_SONANDO.clear() 

# --- Variables Globales para el Nivel ---
# Matriz por defecto 16x20 (0=cielo, 1=ladrillo, 2=gerald, 3=champiñón, 7=irrompible, 9=naty, 50=portal visual)
matriz_default = [
    [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
    [7,2,0,0,1,0,3,0,1,0,0,1,0,0,3,0,1,0,0,7],
    [7,0,7,0,0,1,0,0,0,0,0,0,0,1,7,0,0,0,3,7],
    [7,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,7],
    [7,0,7,1,0,7,1,0,0,0,0,0,1,7,0,7,1,0,1,7],
    [7,0,0,0,3,0,0,1,0,0,0,0,0,0,3,0,0,1,0,7],
    [7,0,7,0,7,7,7,0,7,0,7,0,7,7,7,0,7,0,7,7],
    [7,0,0,3,0,0,50,0,0,0,0,0,0,0,50,0,0,3,0,7],
    [7,0,7,0,7,7,7,0,7,0,7,0,7,7,7,0,7,0,7,7],
    [7,0,3,0,0,0,1,0,0,0,0,0,3,0,0,1,0,0,0,7],
    [7,1,7,0,7,0,1,0,1,0,0,0,7,0,1,0,7,1,0,7],
    [7,0,3,0,0,0,3,0,0,0,0,0,0,3,0,0,0,0,3,7],
    [7,0,7,0,7,1,0,7,0,0,0,0,7,0,1,7,0,7,0,7],
    [7,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,9,7],
    [7,0,7,7,7,7,7,7,7,0,7,7,7,7,7,7,7,7,7,7],
    [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
]

# --- Funciones de Carga de Nivel ---

def cargar_matriz(ruta_archivo):
    """Carga la matriz desde un archivo de texto y calcula los champiñones *después* de las modificaciones."""
    try:
        with open(ruta_archivo, 'r') as f:
            lineas = f.readlines()

        matriz = []
        for linea in lineas:
            fila = [int(x.strip()) for x in linea.split(',') if x.strip().isdigit()]
            if fila:
                matriz.append(fila)

        # Validar el tamaño 16x20 
        if not matriz or len(matriz) != 16 or any(len(row) != 20 for row in matriz):
            messagebox.showerror("Error de Nivel", f"El archivo '{Path(ruta_archivo).name}' no tiene el formato 16x20 correcto.")
            return None, 0

        # Apertura de pasajes centrales
        for i in range(len(matriz)):
            if i not in (0, len(matriz)-1):
                matriz[i][9] = 0 # Columna central abierta
        for j in range(len(matriz[0])):
            if j not in (0, len(matriz[0])-1):
                matriz[7][j] = 0 # Fila central abierta
        
        # Conteo de champiñones
        champis = sum(row.count(3) for row in matriz)
        
        return matriz, champis

    except FileNotFoundError:
        messagebox.showerror("Error de Archivo", f"El archivo de nivel no se encontró: {ruta_archivo}")
        return None, 0
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar el nivel: {e}")
        return None, 0


def iniciar_juego_desde_menu():
    """
    Función que envuelve la selección de archivo y el inicio del juego.
    Esta se llama al presionar el botón 'Jugar'.
    """
    global matriz_default
    
    # Abrir diálogo para seleccionar archivo
    ruta_archivo = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de Nivel", "*.txt"), ("Todos los archivos", "*.*")],
        title="Selecciona un archivo de nivel (matriz.txt)"
    )

    matriz_cargada = None
    champis_cargados = 0
    
    if ruta_archivo:
        matriz_cargada, champis_cargados = cargar_matriz(ruta_archivo)
    
    if matriz_cargada:
        iniciar_juego(matriz_cargada, champis_cargados)
    else:
        # Lógica para el nivel por defecto

        matriz_juego = [row[:] for row in matriz_default] # Copia

        # Aplicar la apertura de centro 
        for i in range(len(matriz_juego)):
            if i not in (0, len(matriz_juego)-1):
                matriz_juego[i][9] = 0
        for j in range(len(matriz_juego[0])):
            if j not in (0, len(matriz_juego[0])-1):
                matriz_juego[7][j] = 0
        
        default_champis = sum(row.count(3) for row in matriz_juego)

        messagebox.showinfo("Nivel por Defecto", "No se seleccionó o cargó un nivel válido. Iniciando con el nivel por defecto.")
        iniciar_juego(matriz_juego, default_champis)


# --- Lógica del Juego ---

def iniciar_juego(matriz_nivel, champis_totales):
    
    if 'ventana' in globals() and isinstance(ventana, tk.Tk):
        ventana.destroy()

    juego = tk.Tk()
    juego.title("Gera Quest - Rescata a Naty")
    juego.configure(bg=COLOR_FONDO)

    # --- Bloqueo de edición/ventana ---
    juego.overrideredirect(True)
    juego.resizable(False, False)
    juego.attributes("-topmost", True)
    juego.protocol("WM_DELETE_WINDOW", lambda: None)
    juego.focus_force()

    TAM_CELDA = 45
    VISIBLE_F, VISIBLE_C = 8, 10
    direccion = "abajo"
    tiene_poder = False
    
    m = matriz_nivel 
    champis_restantes = champis_totales
    
    juego_pausado = False

    # --- Cargar imágenes ---
    def cargar(nombre):
        for ext in [".png", ".jpg", ".jpeg", ".PNG"]:
            p = Path(nombre + ext)
            if p.exists():
                img = Image.open(p).resize((TAM_CELDA, TAM_CELDA), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
        img = Image.new("RGB", (TAM_CELDA, TAM_CELDA), (120, 120, 120))
        return ImageTk.PhotoImage(img)

    try:
        img_gerald = Image.open("gerald.png").resize((TAM_CELDA, TAM_CELDA), Image.LANCZOS)
        img_gerald_izq = ImageOps.mirror(img_gerald)
        img_gerald_abajo = Image.open("gerald_abajo.png").resize((TAM_CELDA, TAM_CELDA), Image.LANCZOS)
        img_gerald_arriba = Image.open("gerald_arriba.png").resize((TAM_CELDA, TAM_CELDA), Image.LANCZOS)

        imagenes = {
            0: cargar("cielo"),
            1: cargar("ladrillo"),
            2: ImageTk.PhotoImage(img_gerald),
            "izquierda": ImageTk.PhotoImage(img_gerald_izq),
            "abajo": ImageTk.PhotoImage(img_gerald_abajo),
            "arriba": ImageTk.PhotoImage(img_gerald_arriba),
            3: cargar("visualizacion"),   # champiñón
            7: cargar("bloque_irrompible"),
            9: cargar("naty")
        }
    except FileNotFoundError as e:
        messagebox.showerror("Error de Imagen", f"No se pudo cargar una imagen esencial (ej: {e.filename}). Asegúrate de que todas las imágenes estén en la misma carpeta.")
        juego.destroy()
        return


    canvas = tk.Canvas(
        juego,
        width=VISIBLE_C*TAM_CELDA,
        height=VISIBLE_F*TAM_CELDA,
        bg=COLOR_FONDO,
        highlightthickness=0
    )
    canvas.pack(padx=10, pady=10)

    offset_x, offset_y = 0, 0

    # --- Dibujo, Posición, y Movimiento ---
    def dibujar():
        canvas.delete("all")
        for y in range(VISIBLE_F):
            for x in range(VISIBLE_C):
                gx, gy = x + offset_x, y + offset_y
                if 0 <= gy < len(m) and 0 <= gx < len(m[0]):
                    val = m[gy][gx]
                    if val == 2:
                        img = imagenes.get(direccion, imagenes[2])
                    else:
                        img = imagenes.get(val, imagenes[0]) 
                    canvas.create_image(x*TAM_CELDA, y*TAM_CELDA, image=img, anchor="nw")

    def pos_gerald_global():
        for y in range(len(m)):
            for x in range(len(m[0])):
                if m[y][x] == 2:
                    return x, y
        m[1][1] = 2 
        return 1, 1

    gerald_x, gerald_y = pos_gerald_global()

    # --- Menú de Pausa (ESC) ---
    def mostrar_menu_pausa():
        nonlocal juego_pausado
        if juego_pausado:
            return
        juego_pausado = True

        pausa_win = tk.Toplevel(juego)
        pausa_win.title("Pausa")
        pausa_win.geometry("300x200")
        pausa_win.configure(bg="#444")
        pausa_win.resizable(False, False)
        pausa_win.grab_set()
        pausa_win.focus_force()
        pausa_win.attributes("-topmost", True)
        pausa_win.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(pausa_win, text="Juego en Pausa", font=("Arial", 16, "bold"),
                 fg="white", bg="#444").pack(pady=20)

        def continuar():
            nonlocal juego_pausado
            juego_pausado = False
            pausa_win.destroy()
            juego.focus_force()

        def salir_menu():
            pausa_win.destroy()
            juego.destroy()

        tk.Button(pausa_win, text="Continuar", font=("Arial", 14),
                  width=15, command=continuar).pack(pady=10)
        tk.Button(pausa_win, text="Salir al Menú", font=("Arial", 14),
                  width=15, command=salir_menu).pack(pady=10)

    # --- Movimiento ---
    def mover(dx, dy, dir_actual):
        nonlocal gerald_x, gerald_y, direccion, offset_x, offset_y, tiene_poder, champis_restantes
        if juego_pausado:
            return
        direccion = dir_actual

        nx, ny = gerald_x + dx, gerald_y + dy
        if not (0 <= nx < len(m[0]) and 0 <= ny < len(m)):
            return

        destino = m[ny][nx]
        if destino == 7:
            return

        if destino == 1:
            if tiene_poder:
                m[ny][nx] = 0
                tiene_poder = False
            else:
                return

        if destino == 3:
            tiene_poder = True
            champis_restantes -= 1
            m[ny][nx] = 0

        if destino == 9:
            if champis_restantes == 0:
                messagebox.showinfo("Victoria", "Has rescatado a Naty después de tomar todos los champiñones.")
                juego.destroy()
                
                if 'ventana' in globals() and isinstance(ventana, tk.Tk):
                    ventana.deiconify() # Muestra la ventana de nuevo
                    ventana.focus_force()
                return
            else:
                messagebox.showwarning("Aún no", f"Recoge todos los champiñones antes de rescatar a Naty.\nRestantes: {champis_restantes}")
                return

        # Movimiento
        m[gerald_y][gerald_x] = 0
        m[ny][nx] = 2
        gerald_x, gerald_y = nx, ny

        # Cambio de cuadrante visible
        max_offset_x = len(m[0]) - VISIBLE_C
        max_offset_y = len(m) - VISIBLE_F    

        if gerald_x < offset_x:
            offset_x = max(0, offset_x - 10)
        elif gerald_x >= offset_x + 10:
            offset_x = min(max_offset_x, offset_x + 10) 
        if gerald_y < offset_y:
            offset_y = max(0, offset_y - 8)
        elif gerald_y >= offset_y + 8:
            offset_y = min(max_offset_y, offset_y + 8)

        dibujar()

    # --- Controles ---
    def tecla(event):
        t = event.keysym.lower()
        if t == "w": mover(0, -1, "arriba")
        elif t == "s": mover(0, 1, "abajo")
        elif t == "a": mover(-1, 0, "izquierda")
        elif t == "d": mover(1, 0, "derecha")
        elif t == "escape": mostrar_menu_pausa()

    juego.bind("<KeyPress>", tecla)
    dibujar()
    juego.wait_window() 
    
    if 'ventana' in globals() and isinstance(ventana, tk.Tk):
        ventana.deiconify()
        ventana.focus_force()


# --- Menú Principal ---
def main_menu():
    global ventana
    
    iniciar_musica() 
    
    ventana = tk.Tk()
    ventana.title("Gera Quest")
    ventana.geometry("1436x768")
    ventana.configure(bg=COLOR_FONDO)

    try:
        logo = tk.PhotoImage(file="gerald.png")
        ventana.iconphoto(True, logo)
    except tk.TclError:
        pass

    def actualizar_fondo(event=None):
        w, h = ventana.winfo_width(), ventana.winfo_height()
        if w <= 1 or h <= 1:
            ventana.after(100, actualizar_fondo)
            return
        try:
            img = Image.open("televisor.PNG").convert("RGBA")
            escala = min(w / img.width, h / img.height)
            nw, nh = max(1, int(img.width * escala)), max(1, int(img.height * escala))
            redim = img.resize((nw, nh), Image.LANCZOS)
            fondo = ImageTk.PhotoImage(redim)
            fondo_label.config(image=fondo, bg=COLOR_FONDO)
            fondo_label.image = fondo
            fondo_label.place(x=(w - nw)//2, y=(h - nh)//2)
        except Exception:
            pass

    fondo_label = tk.Label(ventana, bd=0, bg=COLOR_FONDO)
    fondo_label.place(x=0, y=0)
    ventana.bind("<Configure>", actualizar_fondo)
    actualizar_fondo()

    frame = tk.Frame(ventana, bg="gray")
    frame.place(x=350, y=30, width=646, height=480)

    # --- Botón INICIAR JUEGO ---
    img_play = Image.open("jugar.png").resize((200, 100), Image.LANCZOS)
    img_play = ImageTk.PhotoImage(img_play)
    
    def ocultar_e_iniciar():
        ventana.withdraw() # Oculta la ventana principal
        iniciar_juego_desde_menu() # Inicia el juego.
        
    tk.Button(frame, image=img_play, borderwidth=0, bg="gray", command=ocultar_e_iniciar).pack(pady=60) 
    
    # --- Botón SALIR ---
    img_exit = Image.open("salir.png").resize((200, 100), Image.LANCZOS)
    img_exit = ImageTk.PhotoImage(img_exit)
    
    def salir_y_detener():
        detener_musica() # Detiene el bucle antes de cerrar la aplicación
        ventana.destroy()
        
    tk.Button(frame, image=img_exit, borderwidth=0, bg="gray", command=salir_y_detener).pack(pady=60)

    ventana.mainloop()

# Inicializa el programa
if __name__ == "__main__":
    main_menu()