import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from threading import Thread
from datetime import datetime
import pandas as pd
import io
import sys
from contextlib import redirect_stdout

# Importações para a funcionalidade de Gráfico
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importa a função de coleta do nosso script
from app.scripts.collect_data import run_collection

class StockApp:
    def __init__(self, root):
        """
        Construtor da nossa aplicação. É aqui que criamos a janela e todos os
        componentes visuais (widgets).
        """
        self.root = root
        self.root.title("Painel de Controle - API de Ações")
        self.root.geometry("750x650")

        # --- Configurações da API ---
        self.base_url = "http://127.0.0.1:8000/api/v1/"
        # ❗ IMPORTANTE: Coloque aqui uma chave de API válida
        self.api_key = "SUA_CHAVE_DE_API_AQUI"
        self.headers = {"X-API-Key": self.api_key}

        # --- Estilo e Estrutura Principal ---
        style = ttk.Style(self.root)
        style.theme_use("clam")
        
        notebook = ttk.Notebook(root)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        self.tab1 = ttk.Frame(notebook, padding="10")
        self.tab2 = ttk.Frame(notebook, padding="10")
        self.tab3 = ttk.Frame(notebook, padding="10")
        self.tab4 = ttk.Frame(notebook, padding="10")

        notebook.add(self.tab1, text='Consulta de Ações')
        notebook.add(self.tab2, text='Visão do Mercado')
        notebook.add(self.tab3, text='Gerenciamento Tickers')
        notebook.add(self.tab4, text='Gerenciar Usuários')

        self._criar_widgets_tab1()
        self._criar_widgets_tab2()
        self._criar_widgets_tab3()
        self._criar_widgets_tab4()

        self.result_text = scrolledtext.ScrolledText(root, height=10, width=80, wrap=tk.WORD, state=tk.DISABLED, bg="black", fg="white")
        self.result_text.pack(pady=5, padx=10, expand=True, fill="both")
        self.status_bar = ttk.Label(root, text="Pronto.", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _criar_widgets_tab1(self):
        frame = self.tab1
        ttk.Label(frame, text="Ticker Específico:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ticker_entry1 = ttk.Entry(frame, width=15)
        self.ticker_entry1.grid(row=0, column=1, padx=5, pady=5)
        self.ticker_entry1.focus()
        ttk.Button(frame, text="Buscar Dados", command=lambda: self.iniciar_thread(self._worker_buscar_ticker)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Buscar Eventos", command=lambda: self.iniciar_thread(self._worker_buscar_eventos)).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame, text="Gerar Gráfico", command=lambda: self.iniciar_thread(self._worker_buscar_grafico)).grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(frame, text="Múltiplos Tickers (vírgula):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.multi_ticker_entry = ttk.Entry(frame, width=30)
        self.multi_ticker_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        ttk.Button(frame, text="Buscar Múltiplos", command=lambda: self.iniciar_thread(self._worker_buscar_multiplos)).grid(row=1, column=4, padx=5, pady=5)

    def _criar_widgets_tab2(self):
        frame = self.tab2
        ttk.Button(frame, text="Listar Todos os Tickers Cadastrados", command=lambda: self.iniciar_thread(self._worker_listar_todos)).pack(pady=10, fill='x')
        ttk.Button(frame, text="Ver Índices Principais (IBOV/IFIX)", command=lambda: self.iniciar_thread(self._worker_buscar_indices)).pack(pady=10, fill='x')
        ttk.Button(frame, text="Gerar Gráfico Comparativo de Performance", command=lambda: self.iniciar_thread(self._worker_buscar_grafico_comparativo)).pack(pady=10, fill='x')

    def _criar_widgets_tab3(self):
        frame = self.tab3
        ttk.Label(frame, text="--- Coleta de Dados (Web Scraper) ---", font="-weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 5))
        self.collect_button = ttk.Button(frame, text="Iniciar Coleta Manual", command=self._confirmar_e_iniciar_coleta)
        self.collect_button.grid(row=1, column=0, pady=(0,10), sticky='w')
        ttk.Button(frame, text="Ver Logs da Coleta", command=lambda: self.iniciar_thread(self._worker_listar_logs_coleta)).grid(row=1, column=1, padx=5, pady=(0,10), sticky='w')
        ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(frame, text="--- Cadastrar Novo Ticker ---", font="-weight bold").grid(row=3, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(frame, text="Código do Ticker:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.new_ticker_codigo = ttk.Entry(frame, width=15); self.new_ticker_codigo.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(frame, text="Nome da Empresa:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.new_ticker_nome = ttk.Entry(frame, width=30); self.new_ticker_nome.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(frame, text="Cadastrar", command=lambda: self.iniciar_thread(self._worker_cadastrar_ticker)).grid(row=6, column=1, pady=10, sticky="w")
        ttk.Separator(frame, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(frame, text="--- Atualizar Nome do Ticker ---", font="-weight bold").grid(row=8, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(frame, text="Ticker para Atualizar:").grid(row=9, column=0, padx=5, pady=2, sticky="w")
        self.update_ticker_codigo = ttk.Entry(frame, width=15); self.update_ticker_codigo.grid(row=9, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(frame, text="Novo Nome:").grid(row=10, column=0, padx=5, pady=2, sticky="w")
        self.update_ticker_nome = ttk.Entry(frame, width=30); self.update_ticker_nome.grid(row=10, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(frame, text="Atualizar", command=lambda: self.iniciar_thread(self._worker_atualizar_ticker)).grid(row=11, column=1, pady=10, sticky="w")
        ttk.Separator(frame, orient='horizontal').grid(row=12, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(frame, text="--- Deletar Ticker Existente ---", font="-weight bold").grid(row=13, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(frame, text="Ticker para Deletar:").grid(row=14, column=0, padx=5, pady=2, sticky="w")
        self.delete_ticker_entry = ttk.Entry(frame, width=15); self.delete_ticker_entry.grid(row=14, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(frame, text="Deletar", command=self._confirmar_e_deletar).grid(row=15, column=1, pady=10, sticky="w")

    def _criar_widgets_tab4(self):
        frame = self.tab4
        list_frame = ttk.Labelframe(frame, text="Usuários Cadastrados", padding="10")
        list_frame.pack(fill="both", expand=True, pady=5)
        self.user_tree = ttk.Treeview(list_frame, columns=("id", "nome", "email", "ativo"), show="headings")
        self.user_tree.heading("id", text="ID"); self.user_tree.column("id", width=40, anchor="center")
        self.user_tree.heading("nome", text="Nome"); self.user_tree.heading("email", text="Email"); self.user_tree.heading("ativo", text="Ativo")
        self.user_tree.column("ativo", width=50, anchor="center")
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)
        action_frame = ttk.Frame(frame, padding="5"); action_frame.pack(fill="x")
        ttk.Button(action_frame, text="Listar/Atualizar Usuários", command=lambda: self.iniciar_thread(self._worker_listar_usuarios)).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Deletar Selecionado", command=self._confirmar_e_deletar_usuario).pack(side="left", padx=5)
        form_frame = ttk.Labelframe(frame, text="Criar / Editar Usuário", padding="10")
        form_frame.pack(fill="x", expand=True, pady=10)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.user_id_entry = ttk.Entry(form_frame, state="readonly"); self.user_id_entry.grid(row=0, column=1, sticky="we", padx=5, pady=2)
        ttk.Label(form_frame, text="Nome:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.user_nome_entry = ttk.Entry(form_frame); self.user_nome_entry.grid(row=1, column=1, sticky="we", padx=5, pady=2)
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.user_email_entry = ttk.Entry(form_frame); self.user_email_entry.grid(row=2, column=1, sticky="we", padx=5, pady=2)
        form_frame.columnconfigure(1, weight=1)
        form_buttons_frame = ttk.Frame(form_frame); form_buttons_frame.grid(row=3, column=1, sticky="e", pady=10)
        ttk.Button(form_buttons_frame, text="Salvar", command=self._salvar_usuario).pack(side="left", padx=5)
        ttk.Button(form_buttons_frame, text="Limpar", command=self._limpar_formulario_usuario).pack(side="left")

    def iniciar_thread(self, target_func, *args):
        thread = Thread(target=target_func, args=args, daemon=True)
        thread.start()

    def _atualizar_status(self, texto):
        self.status_bar.config(text=texto)

    def _atualizar_resultado(self, texto_ou_lista):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        if isinstance(texto_ou_lista, list) and texto_ou_lista:
            try:
                df = pd.DataFrame(texto_ou_lista)
                self.result_text.insert(tk.END, df.to_string())
            except Exception:
                 self.result_text.insert(tk.END, json.dumps(texto_ou_lista, indent=2, ensure_ascii=False))
        else:
            self.result_text.insert(tk.END, str(texto_ou_lista))
        self.result_text.config(state=tk.DISABLED)
        self.root.after(0, self._atualizar_status, "Pronto.")

    def _chamar_api(self, metodo, url_prefixo, url_sufixo="", **kwargs):
        full_url = f"{self.base_url}{url_prefixo}{url_sufixo}"
        self.root.after(0, self._atualizar_status, f"Chamando API: {metodo.upper()} {full_url}")
        try:
            response = requests.request(metodo, full_url, headers=self.headers, timeout=20, **kwargs)
            if response.status_code in [200, 201]:
                self.root.after(0, self._atualizar_resultado, response.json())
                return True, response.json()
            else:
                erro_msg = f"Erro {response.status_code}: {response.text}"
                self.root.after(0, self._atualizar_resultado, erro_msg)
                return False, None
        except requests.exceptions.RequestException as e:
            self.root.after(0, self._atualizar_resultado, f"Erro de conexão com a API: {e}")
            return False, None

    # --- Workers para Ações, Gráficos, Coleta, etc. ---
    def _worker_buscar_ticker(self):
        ticker = self.ticker_entry1.get().strip().upper()
        if ticker: self._chamar_api("GET", "acoes/", ticker)
    def _worker_buscar_eventos(self):
        ticker = self.ticker_entry1.get().strip().upper()
        if ticker: self._chamar_api("GET", "acoes/", f"{ticker}/eventos")
    def _worker_buscar_multiplos(self):
        tickers_str = self.multi_ticker_entry.get().strip().upper()
        if tickers_str:
            params = [("tickers", ticker.strip()) for ticker in tickers_str.split(',')]
            self._chamar_api("GET", "acoes/", "buscar", params=params)
    def _worker_listar_todos(self):
        self._chamar_api("GET", "acoes/", "listar-todos")
    def _worker_buscar_indices(self):
        self._chamar_api("GET", "acoes/", "indices/principais")
    def _worker_cadastrar_ticker(self):
        codigo = self.new_ticker_codigo.get().strip().upper()
        nome = self.new_ticker_nome.get().strip()
        if codigo and nome: self._chamar_api("POST", "acoes/", json={"codigo": codigo, "nome": nome})
    def _worker_atualizar_ticker(self):
        ticker = self.update_ticker_codigo.get().strip().upper()
        nome = self.update_ticker_nome.get().strip()
        if ticker and nome: self._chamar_api("PUT", "acoes/", ticker, json={"nome": nome})
    def _confirmar_e_deletar(self):
        ticker = self.delete_ticker_entry.get().strip().upper()
        if not ticker: return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o ticker '{ticker}'?"):
            self.iniciar_thread(self._worker_deletar_ticker, ticker)
    def _worker_deletar_ticker(self, ticker):
        if ticker: self._chamar_api("DELETE", "acoes/", ticker)
    def _confirmar_e_iniciar_coleta(self):
        if messagebox.askyesno("Confirmar Coleta", "Este processo pode levar vários minutos. Deseja continuar?"):
            self.collect_button.config(state=tk.DISABLED); self.iniciar_thread(self._worker_iniciar_coleta)
    def _worker_iniciar_coleta(self):
        self.root.after(0, self._atualizar_status, "Iniciando coleta..."); self.root.after(0, self._atualizar_resultado, "Log da Coleta em andamento...\n\n")
        log_stream = io.StringIO()
        with redirect_stdout(log_stream):
            try: run_collection()
            except Exception as e: print(f"\n❌ ERRO CRÍTICO NO SCRIPT DE COLETA: {e}")
        self.root.after(0, self._atualizar_resultado, log_stream.getvalue())
        self.root.after(0, self.collect_button.config, {'state': tk.NORMAL})
    def _worker_listar_logs_coleta(self):
        self._chamar_api("GET", "logs/", "coleta")
    
    # --- WORKERS DE GRÁFICO (CORRIGIDOS) ---
    def _worker_buscar_grafico(self):
        ticker = self.ticker_entry1.get().strip().upper()
        if not ticker: return
        self.root.after(0, self._atualizar_status, f"Buscando dados do gráfico para {ticker}...")
        try:
            response = requests.get(f"{self.base_url}acoes/{ticker}/grafico", headers=self.headers, timeout=15)
            if response.status_code == 200:
                self.root.after(0, self._desenhar_grafico, ticker, response.json())
            else:
                erro_msg = f"Erro {response.status_code}: {response.text}"
                self.root.after(0, self._atualizar_resultado, erro_msg)
        except requests.exceptions.RequestException as e:
            self.root.after(0, self._atualizar_resultado, f"Erro de conexão com a API: {e}")
            
    def _worker_buscar_grafico_comparativo(self):
        self.root.after(0, self._atualizar_status, "Buscando dados para o gráfico comparativo...")
        try:
            response = requests.get(f"{self.base_url}acoes/grafico-comparativo", headers=self.headers, timeout=20)
            if response.status_code == 200:
                self.root.after(0, self._desenhar_grafico_comparativo, response.json())
            else:
                erro_msg = f"Erro {response.status_code}: {response.text}"
                self.root.after(0, self._atualizar_resultado, erro_msg)
        except requests.exceptions.RequestException as e:
            self.root.after(0, self._atualizar_resultado, f"Erro de conexão com a API: {e}")
    
    # --- Lógica e Workers para a Aba de Usuários ---
    def _on_user_select(self, event):
        selected_items = self.user_tree.selection()
        if not selected_items: return
        item = self.user_tree.item(selected_items[0]); user_id, nome, email, _ = item['values']
        self._limpar_formulario_usuario()
        self.user_id_entry.config(state="normal"); self.user_id_entry.insert(0, user_id); self.user_id_entry.config(state="readonly")
        self.user_nome_entry.insert(0, nome); self.user_email_entry.insert(0, email)
    def _limpar_formulario_usuario(self):
        self.user_id_entry.config(state="normal"); self.user_id_entry.delete(0, tk.END); self.user_id_entry.config(state="readonly")
        self.user_nome_entry.delete(0, tk.END); self.user_email_entry.delete(0, tk.END); self.user_nome_entry.focus()
    def _popular_treeview_usuarios(self, usuarios: list):
        for i in self.user_tree.get_children(): self.user_tree.delete(i)
        for user in usuarios: self.user_tree.insert("", "end", values=(user['id'], user['nome'], user['email'], user['ativo']))
        self.root.after(0, self._atualizar_resultado, f"{len(usuarios)} usuários carregados.")
    def _salvar_usuario(self):
        user_id = self.user_id_entry.get()
        if user_id: self.iniciar_thread(self._worker_atualizar_usuario, int(user_id))
        else: self.iniciar_thread(self._worker_criar_usuario)
    def _confirmar_e_deletar_usuario(self):
        selected_items = self.user_tree.selection()
        if not selected_items: messagebox.showwarning("Nenhum Usuário", "Selecione um usuário para deletar."); return
        item = self.user_tree.item(selected_items[0]); user_id, nome, _, _ = item['values']
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o usuário '{nome}' (ID: {user_id})?"):
            self.iniciar_thread(self._worker_deletar_usuario, user_id)
    def _worker_listar_usuarios(self):
        sucesso, dados = self._chamar_api("GET", url_prefixo="usuarios/")
        if sucesso: self.root.after(0, self._popular_treeview_usuarios, dados)
    def _worker_criar_usuario(self):
        nome = self.user_nome_entry.get().strip(); email = self.user_email_entry.get().strip()
        if not nome or not email: messagebox.showerror("Erro", "Nome e Email são obrigatórios."); return
        sucesso, _ = self._chamar_api("POST", "usuarios/", json={"nome": nome, "email": email})
        if sucesso: self.iniciar_thread(self._worker_listar_usuarios)
    def _worker_atualizar_usuario(self, user_id: int):
        nome = self.user_nome_entry.get().strip(); email = self.user_email_entry.get().strip()
        if not nome or not email: messagebox.showerror("Erro", "Nome e Email são obrigatórios."); return
        sucesso, _ = self._chamar_api("PUT", "usuarios/", f"{user_id}", json={"nome": nome, "email": email})
        if sucesso: self.iniciar_thread(self._worker_listar_usuarios)
    def _worker_deletar_usuario(self, user_id: int):
        sucesso, _ = self._chamar_api("DELETE", "usuarios/", f"{user_id}")
        if sucesso: self.iniciar_thread(self._worker_listar_usuarios)
        
    def _desenhar_grafico(self, ticker, dados_grafico):
        labels, data = dados_grafico.get('labels', []), [float(p) for p in dados_grafico.get('data', [])]
        if not labels or not data: messagebox.showinfo("Sem Dados", f"Não há dados para gerar o gráfico de {ticker}."); self._atualizar_status("Pronto."); return
        chart_window = tk.Toplevel(self.root); chart_window.title(f"Gráfico - {ticker}"); chart_window.geometry("800x600")
        fig = Figure(figsize=(8, 5), dpi=100); ax = fig.add_subplot(111); ax.plot(labels, data, marker='o', linestyle='-', markersize=4)
        tick_spacing = len(labels) // 10 or 1; ax.set_xticks(ax.get_xticks()[::tick_spacing]); fig.autofmt_xdate(rotation=45)
        ax.set_title(f"Histórico de Preços de {ticker}"); ax.set_xlabel("Data"); ax.set_ylabel("Preço (R$)"); ax.grid(True); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_window); canvas.draw(); canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True); self._atualizar_status("Pronto.")
    def _desenhar_grafico_comparativo(self, dados_grafico):
        labels, datasets = dados_grafico.get('labels', []), dados_grafico.get('datasets', [])
        if not labels or not datasets: messagebox.showinfo("Sem Dados", "Não há dados para gerar o gráfico comparativo."); self._atualizar_status("Pronto."); return
        chart_window = tk.Toplevel(self.root); chart_window.title("Gráfico Comparativo"); chart_window.geometry("900x650")
        fig = Figure(figsize=(9, 6), dpi=100); ax = fig.add_subplot(111)
        for dataset in datasets: ax.plot(labels, dataset['data'], label=dataset['label'], linewidth=2)
        tick_spacing = len(labels) // 10 or 1; ax.set_xticks(ax.get_xticks()[::tick_spacing]); fig.autofmt_xdate(rotation=45)
        ax.set_title("Performance Relativa (Últimos 90 dias)"); ax.set_xlabel("Data"); ax.set_ylabel("Variação (%)"); ax.grid(True, linestyle='--', alpha=0.6); ax.legend(); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_window); canvas.draw(); canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True); self._atualizar_status("Pronto.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()