import os
import logging
import time
from dotenv import load_dotenv
from AirbnbAPI import AirbnbAPI

def load_env_variables():
    """
    Carrega as variáveis de ambiente do arquivo `.env` e valida a existência delas.

    Returns:
        tuple: Retorna a API_KEY e o COOKIE carregados do ambiente.

    Raises:
        ValueError: Caso API_KEY ou COOKIE não estejam definidas no arquivo `.env`.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    cookie = os.getenv("COOKIE")
    if not api_key or not cookie:
        raise ValueError("As variáveis API_KEY e COOKIE devem estar definidas no arquivo .env.")
    return api_key, cookie

def save_to_file(output_file, content):
    """
    Salva o conteúdo em um arquivo no formato JSON. Se o arquivo já existir, ele será removido antes de ser recriado.

    Args:
        output_file (str): Nome do arquivo onde o conteúdo será salvo.
        content (str): Conteúdo a ser salvo no arquivo.

    Raises:
        IOError: Caso ocorra algum problema ao salvar o arquivo (ex.: permissão ou disco cheio).
    """
    if os.path.exists(output_file):
        os.remove(output_file)
        logging.info(f"[ATUALIZAÇÃO] Arquivo '{output_file}' removido.")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(content)
    logging.info(f"[CRIAÇÃO] Arquivo '{output_file}' criado com sucesso.")

if __name__ == "__main__":
    # Configuração do logging para rastreamento da execução
    logging.basicConfig(
        filename="reservas.log",
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Bloco principal do script
    try:
        # Registrar início da execução
        total_start_time = time.time()
        logging.info("[INICIALIZAÇÃO] Script iniciado.")

        # Carregar as variáveis de ambiente necessárias
        API_KEY, COOKIE = load_env_variables()

        # Instanciar a classe AirbnbAPI com a chave de API e o cookie carregados das variáveis de ambiente
        airbnb_api = AirbnbAPI(API_KEY, COOKIE)

        # Recuperar as reservas no formato JSON com os seguintes filtros:
        reservas_json = airbnb_api.get_reservations_as_json(
            sort_by="check_out",         # Campo utilizado para ordenação. Aqui, as reservas serão ordenadas com base no campo "check_out".
            sort_order="asc",            # Ordem crescente. O menor valor de "check_out" aparecerá primeiro.
            start_date="2024-01-01",     # Data inicial do filtro. Somente reservas com "check_out" a partir de 1º de janeiro de 2024 serão incluídas.
            end_date="2024-12-31",       # Data final do filtro. Somente reservas com "check_out" até 31 de dezembro de 2024 serão incluídas.
            date_filter_field="check_out",  # Campo de data utilizado para filtragem. O "check_out" será usado como referência para aplicar os filtros de data.
            status_filter=["Hóspede anterior", "Aguardando avaliação do hóspede"] 
            # Filtro de status. Somente reservas com o status "Hóspede anterior" ou "Aguardando avaliação do hóspede" serão incluídas.
        )

        # Gerar arquivo ICS a partir do JSON de reservas
        reservas_ics = airbnb_api.generate_ics(reservas_json)

        # Definir nomes dos arquivos de saída
        output_file_json = "reservas.json"
        output_file_ics = "reservas.ics"

        # Salvar os dados em arquivos
        save_to_file(output_file_json, reservas_json)  # Salvar reservas em formato JSON
        save_to_file(output_file_ics, reservas_ics)    # Salvar reservas em formato ICS
        
        # Calcular e registrar a duração total da execução
        total_duration = time.time() - total_start_time
        logging.info(f"[EXECUÇÃO COMPLETA] Tempo total de execução: {total_duration:.4f} segundos.")

    except ValueError as e:
        # Erro crítico devido a configurações inválidas
        logging.critical(f"[ERRO CRÍTICO] {e}")
        print(f"Erro: {e}")
    except Exception as e:
        # Capturar outros erros inesperados
        logging.critical(f"[ERRO] Erro inesperado: {e}")
        print(f"Erro inesperado: {e}")
