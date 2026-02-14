import csv
from abc import ABC, abstractmethod
try:
    from dataclasses import dataclass
except Exception:
    dataclass = None

class Imovel(ABC):
    def __init__(self, tipo):
        self.tipo = tipo
        self.valor_base = 0.0
        self.vaga_garagem = False
        self.num_quartos = 1

    @abstractmethod
    def calcular_aluguel(self):
        pass

class Apartamento(Imovel):
    def __init__(self, num_quartos=1, tem_criancas=True, vaga_garagem=False):
        super().__init__("Apartamento")
        self.valor_base = 700.0
        self.num_quartos = num_quartos
        self.tem_criancas = tem_criancas
        self.vaga_garagem = vaga_garagem

    def calcular_aluguel(self):
        valor = self.valor_base
        if self.num_quartos == 2:
            valor += 200.0
        
        if self.vaga_garagem:
            valor += 300.0
            
        if not self.tem_criancas:
            valor *= 0.95 # 5% de desconto
            
        return valor

class Casa(Imovel):
    def __init__(self, num_quartos=1, vaga_garagem=False):
        super().__init__("Casa")
        self.valor_base = 900.0
        self.num_quartos = num_quartos
        self.vaga_garagem = vaga_garagem

    def calcular_aluguel(self):
        valor = self.valor_base
        if self.num_quartos == 2:
            valor += 250.0
            
        if self.vaga_garagem:
            valor += 300.0
            
        return valor

class Estudio(Imovel):
    def __init__(self, num_vagas=0):
        super().__init__("Estúdio")
        self.valor_base = 1200.0
        self.num_vagas = num_vagas

    def calcular_aluguel(self):
        valor = self.valor_base
        if self.num_vagas == 2:
            valor += 250.0
        elif self.num_vagas > 2:
            valor += 250.0 + (self.num_vagas - 2) * 60.0
        return valor

class Orcamento:
    VALOR_CONTRATO_TOTAL = 2000.0

    def __init__(self, imovel, parcelas_contrato=1):
        self.imovel = imovel
        self.parcelas_contrato = min(max(parcelas_contrato, 1), 5)
        self.mensalidade = imovel.calcular_aluguel()
        self.valor_parcela_contrato = self.VALOR_CONTRATO_TOTAL / self.parcelas_contrato

    def gerar_csv(self, filename="orcamento_12_meses.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Mês", "Mensalidade Aluguel", "Parcela Contrato", "Total Mensal"])
            
            for mes in range(1, 13):
                p_contrato = self.valor_parcela_contrato if mes <= self.parcelas_contrato else 0.0
                total = self.mensalidade + p_contrato
                writer.writerow([mes, f"R$ {self.mensalidade:.2f}", f"R$ {p_contrato:.2f}", f"R$ {total:.2f}"])
        return filename

    def exibir_resumo(self):
        print("\n" + "="*40)
        print("       ORÇAMENTO IMOBILIÁRIA R.M")
        print("="*40)
        print(f"Tipo de Imóvel: {self.imovel.tipo}")
        if hasattr(self.imovel, 'num_quartos'):
            print(f"Quartos: {self.imovel.num_quartos}")
        
        print(f"Mensalidade base: R$ {self.mensalidade:.2f}")
        print(f"Taxa de Contrato: R$ {self.VALOR_CONTRATO_TOTAL:.2f}")
        print(f"Parcelamento contrato: {self.parcelas_contrato}x de R$ {self.valor_parcela_contrato:.2f}")
        print("-" * 40)
        print(f"Total nos meses de contrato: R$ {self.mensalidade + self.valor_parcela_contrato:.2f}")
        print(f"Total após contrato: R$ {self.mensalidade:.2f}")
        print("="*40)

if dataclass:
    @dataclass
    class Cliente:
        nome: str
        documento: str = None
        contato: str = None
else:
    class Cliente:  # fallback
        def __init__(self, nome, documento=None, contato=None):
            self.nome = nome
            self.documento = documento
            self.contato = contato
