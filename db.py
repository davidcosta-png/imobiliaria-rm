import sqlite3
from pathlib import Path
from datetime import datetime

DB_NAME = "imobiliaria.db"

class Repo:
    def __init__(self, db_path=None):
        base = Path(__file__).resolve().parent
        self.path = str(base / (db_path or DB_NAME))
        self._conn = None

    def connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def init_db(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              documento TEXT,
              contato TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              client_id INTEGER NOT NULL,
              tipo_imovel TEXT NOT NULL,
              mensalidade REAL NOT NULL,
              parcelas_contrato INTEGER NOT NULL,
              valor_contrato_total REAL NOT NULL,
              num_quartos INTEGER,
              tem_criancas INTEGER,
              vaga_garagem INTEGER,
              num_vagas INTEGER,
              created_at TEXT NOT NULL,
              FOREIGN KEY(client_id) REFERENCES clients(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              budget_id INTEGER NOT NULL,
              valor REAL NOT NULL,
              data TEXT NOT NULL,
              tipo TEXT,
              mes_referente INTEGER,
              FOREIGN KEY(budget_id) REFERENCES budgets(id)
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_documento ON clients(documento)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_budgets_client ON budgets(client_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_budget ON payments(budget_id)")
        conn.commit()

    def add_client(self, nome, documento=None, contato=None):
        conn = self.connect()
        cur = conn.cursor()
        if documento:
            cur.execute("SELECT id FROM clients WHERE documento = ?", (documento,))
            row = cur.fetchone()
            if row:
                return row["id"]
        cur.execute("INSERT INTO clients (nome, documento, contato) VALUES (?, ?, ?)", (nome, documento, contato))
        conn.commit()
        return cur.lastrowid

    def update_client(self, client_id, nome=None, documento=None, contato=None):
        conn = self.connect()
        cur = conn.cursor()
        fields = []
        vals = []
        if nome is not None:
            fields.append("nome = ?")
            vals.append(nome)
        if documento is not None:
            fields.append("documento = ?")
            vals.append(documento)
        if contato is not None:
            fields.append("contato = ?")
            vals.append(contato)
        if not fields:
            return
        vals.append(client_id)
        cur.execute(f"UPDATE clients SET {', '.join(fields)} WHERE id = ?", vals)
        conn.commit()

    def find_clients(self, query):
        conn = self.connect()
        cur = conn.cursor()
        q = f"%{query.strip()}%"
        cur.execute("SELECT * FROM clients WHERE nome LIKE ? OR documento LIKE ?", (q, q))
        return cur.fetchall()

    def get_client(self, client_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        return cur.fetchone()

    def add_budget(self, client_id, tipo_imovel, mensalidade, parcelas_contrato, valor_contrato_total,
                   num_quartos=None, tem_criancas=None, vaga_garagem=None, num_vagas=None):
        conn = self.connect()
        cur = conn.cursor()
        created_at = datetime.now().isoformat(timespec="seconds")
        cur.execute(
            """
            INSERT INTO budgets (client_id, tipo_imovel, mensalidade, parcelas_contrato, valor_contrato_total,
                                 num_quartos, tem_criancas, vaga_garagem, num_vagas, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, tipo_imovel, mensalidade, parcelas_contrato, valor_contrato_total,
             num_quartos, tem_criancas, vaga_garagem, num_vagas, created_at)
        )
        conn.commit()
        return cur.lastrowid

    def update_budget(self, budget_id, mensalidade=None, parcelas_contrato=None):
        conn = self.connect()
        cur = conn.cursor()
        fields = []
        vals = []
        if mensalidade is not None:
            fields.append("mensalidade = ?")
            vals.append(float(mensalidade))
        if parcelas_contrato is not None:
            fields.append("parcelas_contrato = ?")
            vals.append(int(parcelas_contrato))
        if not fields:
            return
        vals.append(budget_id)
        cur.execute(f"UPDATE budgets SET {', '.join(fields)} WHERE id = ?", vals)
        conn.commit()

    def list_budgets_by_client(self, client_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM budgets WHERE client_id = ? ORDER BY id DESC", (client_id,))
        return cur.fetchall()

    def add_payment(self, budget_id, valor, tipo=None, mes_referente=None):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (budget_id, valor, data, tipo, mes_referente) VALUES (?, ?, ?, ?, ?)",
            (budget_id, float(valor), datetime.now().isoformat(timespec="seconds"), tipo, mes_referente)
        )
        conn.commit()
        return cur.lastrowid

    def get_budget_status(self, budget_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT mensalidade, valor_contrato_total FROM budgets WHERE id = ?", (budget_id,))
        b = cur.fetchone()
        if not b:
            return None
        expected_total = float(b["mensalidade"]) * 12.0 + float(b["valor_contrato_total"])
        cur.execute("SELECT COALESCE(SUM(valor),0) as total_pago FROM payments WHERE budget_id = ?", (budget_id,))
        p = cur.fetchone()
        paid_total = float(p["total_pago"]) if p else 0.0
        remaining = max(expected_total - paid_total, 0.0)
        return {
            "expected_total": expected_total,
            "paid_total": paid_total,
            "remaining_total": remaining
        }
