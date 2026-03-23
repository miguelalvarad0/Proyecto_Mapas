import tkinter as tk
import copy

# -----------------------------------------
def crear_mapa(filename, rows, cols):
    with open(filename, 'w') as f:
        for _ in range(rows):
            f.write("." * cols + "\n")


def leer_mapa(filename):
    with open(filename, 'r') as f:
        return [list(line.strip()) for line in f]


def guardar_mapa(filename, matrix):
    with open(filename, 'w') as f:
        for row in matrix:
            f.write("".join("." if x == "X" else x for x in row) + "\n")


def guardar_copia(filename, matrix, path=None):
    name = filename.replace(".txt", "") + "_copia.txt"

    m = copy.deepcopy(matrix)

    if path:
        for r, c in path:
            if m[r][c] == ".":
                m[r][c] = "*"

    with open(name, 'w') as f:
        for row in m:
            f.write("".join("." if x == "X" else x for x in row) + "\n")


def guardar_error(sr, sc):
    with open("mapa_err.txt", 'w') as f:
        f.write(f"error, mapa sin solución iniciando en la coordenada {sr},{sc}\n")


def limpiar_error():
    with open("mapa_err.txt", 'w') as f:
        f.write("")


# ---------------------------------

def tesoros_accesibles(matrix):
    rows, cols = len(matrix), len(matrix[0])

    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "T":
                if not any(
                    0 <= r+dr < rows and 0 <= c+dc < cols and matrix[r+dr][c+dc] != "#"
                    for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]
                ):
                    return False
    return True


def encontrar_camino(matrix, start):
    rows, cols = len(matrix), len(matrix[0])
    T = {(r,c) for r in range(rows) for c in range(cols) if matrix[r][c] == "T"}

    visited = set()
    found = set()
    path = []

    def bt(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if matrix[r][c] == "#" or (r,c) in visited:
            return False

        visited.add((r,c))
        path.append((r,c))

        if (r,c) in T:
            found.add((r,c))

        if found == T:
            return True

        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            if bt(r+dr, c+dc):
                return True

        if (r,c) in T:
            found.remove((r,c))

        path.pop()
        visited.remove((r,c))
        return False

    return path if bt(*start) else None


# --------------------------------------

class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Backtracking Tesoros")
        self.root.configure(bg="yellow")

        self.matrix = []
        self.filename = ""
        self.start = (0,0)
        self.animating = False
        self.cell_size = 30

        self.build_inicio()

    # -----------------------------------
   
    def build_inicio(self):
        self.frame_inicio = tk.Frame(self.root, bg="yellow")
        self.frame_inicio.pack()

        tk.Label(self.frame_inicio, text="Archivo:", bg="yellow").grid(row=0, column=0)
        self.entry_file = tk.Entry(self.frame_inicio)
        self.entry_file.grid(row=0, column=1)
        tk.Label(self.frame_inicio, text=".txt", bg="yellow").grid(row=0, column=2)

        tk.Label(self.frame_inicio, text="Filas:", bg="yellow").grid(row=1, column=0)
        self.entry_rows = tk.Entry(self.frame_inicio)
        self.entry_rows.grid(row=1, column=1)

        tk.Label(self.frame_inicio, text="Columnas:", bg="yellow").grid(row=2, column=0)
        self.entry_cols = tk.Entry(self.frame_inicio)
        self.entry_cols.grid(row=2, column=1)

        tk.Label(self.frame_inicio, text="Inicio fila:", bg="yellow").grid(row=3, column=0)
        self.entry_sr = tk.Entry(self.frame_inicio)
        self.entry_sr.grid(row=3, column=1)

        tk.Label(self.frame_inicio, text="Inicio col:", bg="yellow").grid(row=4, column=0)
        self.entry_sc = tk.Entry(self.frame_inicio)
        self.entry_sc.grid(row=4, column=1)

        tk.Button(self.frame_inicio, text="Crear mapa", command=self.iniciar)\
            .grid(row=5, column=0, columnspan=3)

    # ---------------------------------------
    def build_editor(self):
        self.frame_editor = tk.Frame(self.root, bg="yellow")
        self.frame_editor.pack()

        self.message = tk.Label(self.frame_editor, bg="yellow")
        self.message.pack()

        container = tk.Frame(self.frame_editor)
        container.pack()

        self.canvas = tk.Canvas(container, width=500, height=500, bg="yellow")
        self.canvas.pack(side="left")

        scroll_y = tk.Scrollbar(container, command=self.canvas.yview)
        scroll_y.pack(side="right", fill="y")

        scroll_x = tk.Scrollbar(self.frame_editor, orient="horizontal",
                                command=self.canvas.xview)
        scroll_x.pack(fill="x")

        self.canvas.configure(yscrollcommand=scroll_y.set,
                              xscrollcommand=scroll_x.set)

        controls = tk.Frame(self.frame_editor, bg="yellow")
        controls.pack()

        self.entry_r = tk.Entry(controls, width=5)
        self.entry_c = tk.Entry(controls, width=5)

        self.entry_r.grid(row=0, column=1)
        self.entry_c.grid(row=0, column=3)

        tk.Label(controls, text="Fila:", bg="yellow").grid(row=0, column=0)
        tk.Label(controls, text="Col:", bg="yellow").grid(row=0, column=2)

        self.tipo = tk.StringVar(value="T")

        tk.Radiobutton(controls, text="T", variable=self.tipo, value="T").grid(row=0, column=4)
        tk.Radiobutton(controls, text="#", variable=self.tipo, value="#").grid(row=0, column=5)

        tk.Button(controls, text="Agregar", command=self.agregar).grid(row=0, column=6)

        tk.Button(self.frame_editor, text="Buscar camino", command=self.buscar).pack()

        # -----------------------------------
        for e in [self.entry_r, self.entry_c]:
            e.bind("<FocusIn>", lambda e: self.stop_anim())

    # --------------------------------

    def iniciar(self):
        fname = self.entry_file.get() or "mapa"
        if not fname.endswith(".txt"):
            fname += ".txt"

        rows = int(self.entry_rows.get())
        cols = int(self.entry_cols.get())

        self.start = (int(self.entry_sr.get()), int(self.entry_sc.get()))
        self.filename = fname

        crear_mapa(fname, rows, cols)
        self.matrix = leer_mapa(fname)

        self.frame_inicio.destroy()
        self.build_editor()
        self.draw()

    def draw(self, path=None, particle=None):
        self.canvas.delete("all")
        rows, cols = len(self.matrix), len(self.matrix[0])

        for r in range(rows):
            for c in range(cols):
                self.canvas.create_text(
                    c*self.cell_size+15,
                    r*self.cell_size+15,
                    text=self.matrix[r][c]
                )

        if path:
            for i in range(len(path)-1):
                r1,c1 = path[i]
                r2,c2 = path[i+1]
                self.canvas.create_line(
                    c1*self.cell_size+15, r1*self.cell_size+15,
                    c2*self.cell_size+15, r2*self.cell_size+15,
                    fill="red", width=3
                )

        if particle:
            r,c = particle
            self.canvas.create_text(
                c*self.cell_size+15,
                r*self.cell_size+15,
                text="●", fill="orange"
            )

        self.canvas.config(scrollregion=(0,0,cols*self.cell_size,rows*self.cell_size))

    def agregar(self):
        try:
            r = int(self.entry_r.get())
            c = int(self.entry_c.get())
            self.matrix[r][c] = self.tipo.get()
            self.draw()
        except:
            pass

    def stop_anim(self):
        self.animating = False

    def buscar(self):
        guardar_mapa(self.filename, self.matrix)

        if not tesoros_accesibles(self.matrix):
            self.message.config(text="❌ Sin solución, no se encontro ningun tesoro", fg="red")
            guardar_error(*self.start)
            guardar_copia(self.filename, self.matrix)
            return

        path = encontrar_camino(self.matrix, self.start)

        if not path:
            self.message.config(text="❌ Sin solución, no se encontro ningun tesoro", fg="red")
            guardar_error(*self.start)
            guardar_copia(self.filename, self.matrix)
            return

        limpiar_error()
        self.matrix[self.start[0]][self.start[1]] = "X"
        guardar_copia(self.filename, self.matrix, path)

        self.message.config(text="✅ Tesoro(s) Encontrado(s)", fg="green")

        self.animating = True
        self.animar(path)

    def animar(self, path, i=0, drawn=None):
        if not self.animating:
            return
        if drawn is None:
            drawn = []

        if i >= len(path):
            return

        drawn = drawn + [path[i]]
        self.draw(drawn, path[i])

        self.root.after(50, lambda: self.animar(path, i+1, drawn))


# ----------------------------------

root = tk.Tk()
app = App(root)
root.mainloop()