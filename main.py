import sys
import os
from models import Apartamento, Casa, Estudio, Orcamento
from db import Repo

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
    action = (os.environ.get("ACTION", "") or "").strip().lower()
    if action == "buscar":
        repo = Repo()
        repo.init_db()
        q = os.environ.get("QUERY", "") or ""
        resultados = repo.find_clients(q) if q else []
        if not resultados:
            print("Nenhum cliente encontrado.")
            return True
        for r in resultados:
            print(f"{r['id']}: {r['nome']}  Doc: {r['documento'] or ''}  Contato: {r['contato'] or ''}")
            budgets = repo.list_budgets_by_client(r["id"])
            for b in budgets:
                st = repo.get_budget_status(b["id"])
                print(f"  Budget {b['id']} • {b['tipo_imovel']} • Mensal R$ {b['mensalidade']:.2f} • Pago R$ {st['paid_total']:.2f} • Falta R$ {st['remaining_total']:.2f}")
        return True
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
    salvar_db = to_bool(os.environ.get("SALVAR_DB"), False)
    if salvar_db:
        repo = Repo()
        repo.init_db()
        nome_cli = os.environ.get("NOME_CLIENTE") or ""
        doc_cli = os.environ.get("DOCUMENTO_CLIENTE") or None
        contato_cli = os.environ.get("CONTATO_CLIENTE") or None
        client_id = repo.add_client(nome_cli, doc_cli, contato_cli)
        tipo_imovel = imovel.tipo
        num_quartos = getattr(imovel, "num_quartos", None)
        tem_criancas = 1 if getattr(imovel, "tem_criancas", True) else 0 if hasattr(imovel, "tem_criancas") else None
        vaga_garagem = 1 if getattr(imovel, "vaga_garagem", False) else 0 if hasattr(imovel, "vaga_garagem") else None
        num_vagas = getattr(imovel, "num_vagas", None)
        budget_id = repo.add_budget(client_id, tipo_imovel, orcamento.mensalidade, orcamento.parcelas_contrato, orcamento.VALOR_CONTRATO_TOTAL, num_quartos, tem_criancas, vaga_garagem, num_vagas)
        print(f"Orçamento salvo. Cliente ID {client_id}, Budget ID {budget_id}.")
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
    print("1. Apartamento (novo orçamento)")
    print("2. Casa (novo orçamento)")
    print("3. Estúdio (novo orçamento)")
    print("4. Buscar cliente e ver status")
    print("5. Registrar pagamento")
    print("6. Editar cliente")
    print("7. Editar orçamento")
    print("0. Sair")
    print("="*40)
    return input("Escolha o tipo de imóvel: ")

def launch_menu():
    limpar_tela()
    print("="*40)
    print("   INICIO - IMOBILIÁRIA R.M")
    print("="*40)
    print("1. Cadastrar cliente e gerar orçamento")
    print("2. Buscar cliente cadastrado")
    print("3. Menu completo")
    print("0. Sair")
    print("="*40)
    return input("Escolha uma opção: ")

def criar_orcamento_interativo(repo: Repo, tipo_opcao: str):
    imovel = None
    if tipo_opcao == '1':
        quartos = int(input("Número de quartos (1 ou 2): ") or 1)
        criancas = input("Possui crianças? (S/N): ").strip().lower() == 's'
        vaga = input("Deseja vaga de garagem? (S/N): ").strip().lower() == 's'
        imovel = Apartamento(num_quartos=quartos, tem_criancas=criancas, vaga_garagem=vaga)
    elif tipo_opcao == '2':
        quartos = int(input("Número de quartos (1 ou 2): ") or 1)
        vaga = input("Deseja vaga de garagem? (S/N): ").strip().lower() == 's'
        imovel = Casa(num_quartos=quartos, vaga_garagem=vaga)
    elif tipo_opcao == '3':
        vagas = int(input("Número de vagas de estacionamento: ") or 0)
        imovel = Estudio(num_vagas=vagas)
    else:
        print("Opção inválida!")
        input("\nPressione Enter para continuar...")
        return
    parcelas = int(input("Parcelar taxa de contrato em quantas vezes (1-5): ") or 1)
    orcamento = Orcamento(imovel, parcelas)
    orcamento.exibir_resumo()
    salvar = input("\nSalvar orçamento no banco de dados? (S/N): ").strip().lower()
    if salvar == 's':
        nome = input("Nome do cliente: ").strip()
        documento = input("Documento (CPF/ID) do cliente (opcional): ").strip()
        contato = input("Contato (telefone/email) (opcional): ").strip()
        client_id = repo.add_client(nome, documento or None, contato or None)
        tipo = imovel.tipo
        num_quartos = getattr(imovel, "num_quartos", None)
        tem_criancas = 1 if getattr(imovel, "tem_criancas", True) else 0 if hasattr(imovel, "tem_criancas") else None
        vaga_garagem = 1 if getattr(imovel, "vaga_garagem", False) else 0 if hasattr(imovel, "vaga_garagem") else None
        num_vagas = getattr(imovel, "num_vagas", None)
        budget_id = repo.add_budget(
            client_id=client_id,
            tipo_imovel=tipo,
            mensalidade=orcamento.mensalidade,
            parcelas_contrato=orcamento.parcelas_contrato,
            valor_contrato_total=orcamento.VALOR_CONTRATO_TOTAL,
            num_quartos=num_quartos,
            tem_criancas=tem_criancas,
            vaga_garagem=vaga_garagem,
            num_vagas=num_vagas
        )
        print(f"Orçamento salvo com ID {budget_id}.")
    salvar_csv = input("\nDeseja gerar o arquivo CSV com o plano de 12 meses? (S/N): ").strip().lower()
    if salvar_csv == 's':
        nome_arquivo = f"orcamento_{imovel.tipo.lower()}_{int(orcamento.mensalidade)}.csv"
        caminho = orcamento.gerar_csv(nome_arquivo)
        print(f"Arquivo gerado com sucesso: {caminho}")
    input("\nPressione Enter para voltar ao menu...")

def buscar_cliente(repo: Repo):
    termo = input("Buscar por nome ou documento: ").strip()
    resultados = repo.find_clients(termo)
    if not resultados:
        print("Nenhum cliente encontrado.")
        input("\nPressione Enter para continuar...")
        return
    print("\nClientes:")
    for r in resultados:
        print(f"{r['id']}: {r['nome']}  Doc: {r['documento'] or ''}  Contato: {r['contato'] or ''}")
    try:
        cid = int(input("\nInforme o ID do cliente para ver orçamentos (0 para voltar): ") or "0")
    except Exception:
        return
    if cid == 0:
        return
    budgets = repo.list_budgets_by_client(cid)
    if not budgets:
        print("Nenhum orçamento para este cliente.")
        input("\nPressione Enter para continuar...")
        return
    print("\nOrçamentos:")
    for b in budgets:
        st = repo.get_budget_status(b["id"])
        exp = st["expected_total"]
        paid = st["paid_total"]
        rem = st["remaining_total"]
        print(f"ID {b['id']} • {b['tipo_imovel']}  Mensal: R$ {b['mensalidade']:.2f}  Contrato: R$ {b['valor_contrato_total']:.2f}  Pago: R$ {paid:.2f}  Falta: R$ {rem:.2f} (Total: R$ {exp:.2f})")
    input("\nPressione Enter para continuar...")

def registrar_pagamento(repo: Repo):
    try:
        bid = int(input("ID do orçamento (budget): ").strip())
    except Exception:
        print("ID inválido.")
        input("\nPressione Enter para continuar...")
        return
    try:
        valor = float(input("Valor do pagamento: ").replace(",", "."))
    except Exception:
        print("Valor inválido.")
        input("\nPressione Enter para continuar...")
        return
    tipo = input("Tipo (aluguel/contrato - opcional): ").strip() or None
    try:
        mes = input("Mês referente (1-12, opcional): ").strip()
        mes_ref = int(mes) if mes else None
    except Exception:
        mes_ref = None
    pid = repo.add_payment(bid, valor, tipo, mes_ref)
    st = repo.get_budget_status(bid)
    if st:
        print(f"Pagamento registrado (ID {pid}). Pago: R$ {st['paid_total']:.2f} • Falta: R$ {st['remaining_total']:.2f}")
    input("\nPressione Enter para continuar...")

def editar_cliente(repo: Repo):
    try:
        cid = int(input("ID do cliente: ").strip())
    except Exception:
        print("ID inválido.")
        input("\nPressione Enter para continuar...")
        return
    nome = input("Novo nome (deixe em branco para manter): ")
    documento = input("Novo documento (deixe em branco para manter): ")
    contato = input("Novo contato (deixe em branco para manter): ")
    repo.update_client(cid, nome if nome else None, documento if documento else None, contato if contato else None)
    print("Cliente atualizado.")
    input("\nPressione Enter para continuar...")

def editar_orcamento(repo: Repo):
    try:
        bid = int(input("ID do orçamento (budget): ").strip())
    except Exception:
        print("ID inválido.")
        input("\nPressione Enter para continuar...")
        return
    mensal = input("Nova mensalidade (deixe em branco para manter): ").strip()
    parc = input("Novo número de parcelas de contrato (1-5, deixe em branco para manter): ").strip()
    mensalidade = float(mensal.replace(",", ".")) if mensal else None
    parcelas = int(parc) if parc else None
    repo.update_budget(bid, mensalidade, parcelas)
    st = repo.get_budget_status(bid)
    if st:
        print(f"Orçamento atualizado. Pago: R$ {st['paid_total']:.2f} • Falta: R$ {st['remaining_total']:.2f} • Total: R$ {st['expected_total']:.2f}")
    input("\nPressione Enter para continuar...")

def main():
    repo = Repo()
    repo.init_db()
    while True:
        escolha = launch_menu()
        if escolha == '0':
            print("Saindo...")
            break
        if escolha == '1':
            print("\nSelecione o tipo de imóvel:")
            print("1. Apartamento")
            print("2. Casa")
            print("3. Estúdio")
            tipo = input("Opção: ").strip()
            criar_orcamento_interativo(repo, tipo)
        elif escolha == '2':
            buscar_cliente(repo)
        elif escolha == '3':
            while True:
                opcao = menu()
                if opcao == '0':
                    break
                if opcao in ('1', '2', '3'):
                    criar_orcamento_interativo(repo, opcao)
                elif opcao == '4':
                    buscar_cliente(repo)
                elif opcao == '5':
                    registrar_pagamento(repo)
                elif opcao == '6':
                    editar_cliente(repo)
                elif opcao == '7':
                    editar_orcamento(repo)
                else:
                    print("Opção inválida!")
                    input("\nPressione Enter para continuar...")
        else:
            print("Opção inválida!")
            input("\nPressione Enter para continuar...")

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
