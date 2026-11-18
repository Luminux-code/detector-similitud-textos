import os
import threading
import tkinter.messagebox as messagebox
from tkinter import filedialog

import customtkinter as ctk

from config import MODELOS, TITULO_APP
from similitud import NOMBRES_METRICAS, calcular_similitud
from texto import leer_pdf

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(TITULO_APP)
        self.geometry("1250x850")
        self.minsize(1000, 700)
        self._poner_icono()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_encabezado()
        self.caja1, self.lbl_arch1 = self._crear_panel(0, "Texto / Documento 1")
        self.caja2, self.lbl_arch2 = self._crear_panel(1, "Texto / Documento 2")
        self._construir_opciones()
        self._construir_resultados()

    def _poner_icono(self):
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icono.ico")
        if os.path.exists(ruta):
            try:
                self.after(250, lambda: self.iconbitmap(ruta))
            except Exception:
                pass

    def _construir_encabezado(self):
        ctk.CTkLabel(
            self,
            text="Detector de Similitud de Textos",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(15, 0))
        ctk.CTkLabel(
            self,
            text="Pega texto o sube un PDF en cada panel para comparar su similitud",
            text_color=("gray30", "gray70"),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def _crear_panel(self, columna, titulo):
        marco = ctk.CTkFrame(self)
        marco.grid(row=2, column=columna, padx=15, pady=5, sticky="nsew")
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(marco, text=titulo, font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        caja = ctk.CTkTextbox(marco, wrap="word")
        caja.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        lbl_arch = ctk.CTkLabel(
            marco, text="Ningún archivo cargado", text_color=("gray40", "gray60")
        )
        lbl_arch.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkButton(
            marco, text="Subir PDF", width=100,
            command=lambda: self.cargar_pdf(caja, lbl_arch),
        ).grid(row=2, column=1, padx=5, pady=(0, 10))
        ctk.CTkButton(
            marco, text="Limpiar", width=80,
            fg_color=("gray70", "gray35"), hover_color=("gray60", "gray25"),
            command=lambda: self.limpiar(caja, lbl_arch),
        ).grid(row=2, column=2, padx=(0, 10), pady=(0, 10))
        return caja, lbl_arch

    def _construir_opciones(self):
        marco = ctk.CTkFrame(self)
        marco.grid(row=3, column=0, columnspan=2, padx=15, pady=8, sticky="ew")
        marco.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(marco, text="Modelo:").grid(row=0, column=0, padx=(15, 5), pady=10)
        self.menu_modelo = ctk.CTkOptionMenu(
            marco, values=list(MODELOS.keys()), width=260
        )
        self.menu_modelo.grid(row=0, column=1, padx=5)

        self.btn_analizar = ctk.CTkButton(
            marco,
            text="ANALIZAR SIMILITUD",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            command=self.iniciar_analisis,
        )
        self.btn_analizar.grid(row=0, column=2, padx=15, sticky="e")

        ctk.CTkButton(
            marco, text="Copiar tabla", width=110, height=38,
            fg_color=("gray70", "gray35"), hover_color=("gray60", "gray25"),
            command=self.copiar_tabla,
        ).grid(row=0, column=3, padx=(0, 15))

    def _construir_resultados(self):
        marco = ctk.CTkFrame(self)
        marco.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="nsew")
        marco.grid_columnconfigure(tuple(range(len(NOMBRES_METRICAS))), weight=1)

        self.ultimas_metricas = {}
        self.lbl_metricas = {}
        for col, nombre in enumerate(NOMBRES_METRICAS):
            self.lbl_metricas[nombre] = self._crear_metrica(marco, col, nombre)

        self.caja_pares = ctk.CTkTextbox(marco, height=120, wrap="word")
        self.caja_pares.grid(
            row=2, column=0, columnspan=len(NOMBRES_METRICAS),
            padx=10, pady=(0, 10), sticky="ew",
        )
        self.caja_pares.configure(state="disabled")

    def _crear_metrica(self, padre, columna, titulo):
        marco = ctk.CTkFrame(padre, fg_color=("gray85", "gray20"))
        marco.grid(row=0, column=columna, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(
            marco, text=titulo, text_color=("gray30", "gray70"),
            font=ctk.CTkFont(size=12), wraplength=170,
        ).pack(pady=(10, 0), padx=4)
        lbl = ctk.CTkLabel(marco, text="--", font=ctk.CTkFont(size=22, weight="bold"))
        lbl.pack(pady=(0, 10))
        return lbl

    def cargar_pdf(self, caja, lbl_arch):
        ruta = filedialog.askopenfilename(
            title="Selecciona un PDF", filetypes=[("Archivos PDF", "*.pdf")]
        )
        if not ruta:
            return
        try:
            texto = leer_pdf(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el PDF:\n{e}")
            return
        if len(texto.strip()) < 20:
            messagebox.showwarning(
                "PDF sin texto",
                "No se pudo extraer texto. Puede ser un PDF escaneado (imagen) y necesitaría OCR.",
            )
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        nombre = os.path.basename(ruta)
        lbl_arch.configure(text=f"{nombre} ({len(texto.split())} palabras)")

    def limpiar(self, caja, lbl_arch):
        caja.delete("1.0", "end")
        lbl_arch.configure(text="Ningún archivo cargado")

    def iniciar_analisis(self):
        t1 = self.caja1.get("1.0", "end").strip()
        t2 = self.caja2.get("1.0", "end").strip()
        if not t1 or not t2:
            messagebox.showwarning("Faltan datos", "Ingresa texto o sube un PDF en ambos paneles.")
            return

        self.btn_analizar.configure(state="disabled", text="Analizando...")
        clave = self.menu_modelo.get()
        threading.Thread(target=self._trabajo, args=(t1, t2, clave), daemon=True).start()

    def _trabajo(self, t1, t2, clave):
        try:
            resultado = calcular_similitud(t1, t2, clave)
            self.after(0, self._mostrar_resultado, resultado)
        except Exception as e:
            self.after(0, self._mostrar_error, str(e))

    def _mostrar_error(self, mensaje):
        self.btn_analizar.configure(state="normal", text="ANALIZAR SIMILITUD")
        messagebox.showerror("Error", mensaje)

    def _mostrar_resultado(self, resultado):
        metricas, pares = resultado
        self.btn_analizar.configure(state="normal", text="ANALIZAR SIMILITUD")
        self.ultimas_metricas = metricas

        for nombre, valor in metricas.items():
            self.lbl_metricas[nombre].configure(text=f"{valor:.4f}\n{valor*100:.1f}%")

        self.caja_pares.configure(state="normal")
        self.caja_pares.delete("1.0", "end")
        self.caja_pares.insert("end", "FRAGMENTOS MÁS PARECIDOS:\n\n")
        for n, (valor, f1, f2) in enumerate(pares, 1):
            self.caja_pares.insert(
                "end",
                f"#{n}  Similitud: {valor*100:.1f}%\n"
                f"  Doc 1: {f1[:220]}...\n"
                f"  Doc 2: {f2[:220]}...\n\n",
            )
        self.caja_pares.configure(state="disabled")

    def copiar_tabla(self):
        if not self.ultimas_metricas:
            messagebox.showinfo("Sin resultados", "Primero ejecuta el análisis.")
            return
        lineas = ["Técnica\tValor"]
        for nombre, valor in self.ultimas_metricas.items():
            lineas.append(f"{nombre}\t{valor:.4f}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lineas))
        messagebox.showinfo("Copiado", "Tabla copiada. Pégala en Word o Excel.")