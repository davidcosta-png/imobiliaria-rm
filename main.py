import sys
import os
from models import Apartamento, Casa, Estudio, Orcamento

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def to_bool(s, default=False):
    if s is None:
        return default
    v = str(s).strip().lower()
    if v in ("s", "y", "yes", "true", "1"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    return default

def to_int(s, default=0):
    try:
        if s is None or str(s).strip() == "":
            return default
        return int(str(s).strip())
    except Exception:
        return default

def run_env():
    tipo = (os.environ.get("TIPO_IMOVEL", "") or "").strip().lower()
    if not tipo:
        return False
    imovel = None
    if tipo == "apartamento":
        quartos = to_int(os.environ.get("NUM_QUARTOS"), 1)
        criancas = to_bool(os.environ.get("TEM_CRIANCAS"), True)
        vaga = to_bool(os.environ.get("VAGA_GARAGEM"), False)
        imovel = Apartamento(num_quartos=quartos, tem_criancas=criancas, vaga_garagem=vaga)
    elif tipo == "casa":
        quartos = to_int(os.environ.get("NUM_QUARTOS"), 1)
        vaga = to_bool(os.environ.get("VAGA_GARAGEM"), False)
        imovel = Casa(num_quartos=quartos, vaga_garagem=vaga)
    elif tipo == "estudio" or tipo == "estúdio":
        vagas = to_int(os.environ.get("NUM_VAGAS"), 0)
        imovel = Estudio(num_vagas=vagas)
    else:
        print("Tipo inválido")
        return True
    parcelas = to_int(os.environ.get("PARCELAS_CONTRATO"), 1)
    orcamento = Orcamento(imovel, parcelas)
    orcamento.exibir_resumo()
    gerar = to_bool(os.environ.get("GERAR_CSV"), False)
    if gerar:
        nome = os.environ.get("CSV_NOME")
        if not nome or not nome.strip():
            nome = f"orcamento_{imovel.tipo.lower()}_{int(orcamento.mensalidade)}.csv"
        caminho = orcamento.gerar_csv(nome)
        print(f"Arquivo gerado com sucesso: {caminho}")
    return True

def menu():
    limpar_tela()
    print("="*40)
    print("   SISTEMA DE ORÇAMENTO IMOBILIÁRIA R.M")
    print("="*40)
    print("1. Apartamento")
    print("2. Casa")
    print("3. Estúdio")
    print("0. Sair")
    print("="*40)
    return input("Escolha o tipo de imóvel: ")

def main():
    while True:
        opcao = menu()
        
        if opcao == '0':
            print("Saindo...")
            break
            
        imovel = None
        
        if opcao == '1':
            # Apartamento
            quartos = int(input("Número de quartos (1 ou 2): ") or 1)
            criancas = input("Possui crianças? (S/N): ").strip().lower() == 's'
            vaga = input("Deseja vaga de garagem? (S/N): ").strip().lower() == 's'
            imovel = Apartamento(num_quartos=quartos, tem_criancas=criancas, vaga_garagem=vaga)
            
        elif opcao == '2':
            # Casa
            quartos = int(input("Número de quartos (1 ou 2): ") or 1)
            vaga = input("Deseja vaga de garagem? (S/N): ").strip().lower() == 's'
            imovel = Casa(num_quartos=quartos, vaga_garagem=vaga)
            
        elif opcao == '3':
            # Estúdio
            vagas = int(input("Número de vagas de estacionamento: ") or 0)
            imovel = Estudio(num_vagas=vagas)
            
        else:
            print("Opção inválida!")
            input("\nPressione Enter para continuar...")
            continue

        if imovel:
            parcelas = int(input("Parcelar taxa de contrato em quantas vezes (1-5): ") or 1)
            orcamento = Orcamento(imovel, parcelas)
            orcamento.exibir_resumo()
            
            salvar = input("\nDeseja gerar o arquivo CSV com o plano de 12 meses? (S/N): ").strip().lower()
            if salvar == 's':
                nome_arquivo = f"orcamento_{imovel.tipo.lower()}_{int(orcamento.mensalidade)}.csv"
                caminho = orcamento.gerar_csv(nome_arquivo)
                print(f"Arquivo gerado com sucesso: {caminho}")
            
            input("\nPressione Enter para voltar ao menu...")

if __name__ == "__main__":
    try:
        if os.environ.get("AUTO_START") == "1" or os.environ.get("TIPO_IMOVEL"):
            run_env()
        else:
            main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        sys.exit(0)
    except ValueError:
        print("\nErro: Por favor, insira valores válidos.")
        input("\nPressione Enter para voltar ao menu...")
        main()
