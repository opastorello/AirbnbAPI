import requests
import datetime
import json
import logging
from typing import List, Dict

class AirbnbAPI:
    BASE_URL = "https://www.airbnb.com.br"

    def __init__(self, api_key: str, cookie: str, locale: str = "pt", currency: str = "BRL", limit: int = 40, offset: int = None):
        """
        Inicializa a classe AirbnbAPI com a chave de API, cookie de autenticação,
        e configurações de localidade, moeda, e os parâmetros de paginação.

        Args:
            api_key (str): Chave de API para autenticação na Airbnb.
            cookie (str): Cookie de sessão do usuário autenticado.
            locale (str): Idioma para os dados retornados pela API.
            currency (str): Moeda para valores monetários.
            limit (int): Número de resultados por página.
            offset (int): Índice de onde começar a busca.
        """
        if not api_key or not cookie:
            raise ValueError("Os parâmetros 'api_key' e 'cookie' são obrigatórios.")

        self.headers = {
            "x-airbnb-api-key": api_key,
            "cookie": cookie,
        }

        self.params = {
            "locale": locale,
            "currency": currency,
            "_format": "for_remy",
            "_limit": limit,
            "_offset": offset,
            "collection_strategy": "for_reservations_list",
            "sort_field": "start_date",
            "sort_order": "desc",
            "status": "accepted,request,canceled",
        }

        logging.info("[INICIALIZAÇÃO] AirbnbAPI configurada com sucesso.")

    def format_earnings(self, earnings_str: str) -> float:
        """
        Converte o valor monetário recebido como string para float.

        Args:
            earnings_str (str): Valor em formato string (ex.: 'R$1.234,56').

        Returns:
            float: Valor convertido para float.
        """
        try:
            return float(earnings_str.replace("R$", "").replace(".", "").replace(",", "."))
        except (ValueError, AttributeError):
            logging.error(f"[ERRO] Falha ao formatar valor: {earnings_str}.")
            return 0.0

    def process_reservation(self, reservation: Dict) -> Dict:
        """
        Processa os dados de uma reserva individual, extraindo e formatando informações relevantes.

        Args:
            reservation (Dict): Dados brutos da reserva recebidos da API.

        Returns:
            Dict: Dados processados da reserva.
        """
        try:
            processed = {
                "status": reservation.get("user_facing_status_localized", ""),
                "confirmation_code": reservation.get("confirmation_code", ""),
                "property_name": reservation.get("listing_name", ""),
                "booking_date": reservation.get("booked_date", ""),
                "check_in": reservation.get("start_date", ""),
                "check_out": reservation.get("end_date", ""),
                "nights": reservation.get("nights", ""),
                "earnings": self.format_earnings(reservation.get("earnings", "0.0")),
                "guest": {
                    "name": reservation.get("guest_user", {}).get("full_name", ""),
                    "phone": reservation.get("guest_user", {}).get("phone", ""),
                    "location": reservation.get("guest_user", {}).get("location", ""),
                    "details": {
                        "adults": reservation.get("guest_details", {}).get("number_of_adults", 0),
                        "children": reservation.get("guest_details", {}).get("number_of_children", 0),
                        "infants": reservation.get("guest_details", {}).get("number_of_infants", 0),
                        "pets": reservation.get("guest_details", {}).get("number_of_pets", 0),
                    },
                },
            }

            logging.info(f"[PROCESSAMENTO] Reserva {processed['confirmation_code']} processada com sucesso.")
            return processed
        except Exception as e:
            logging.error(f"[ERRO] Falha ao processar reserva: {e}.")
            return {}

    def calculate_summary(self, reservations: List[Dict], include_canceled: bool = False) -> Dict:
        """
        Calcula estatísticas e totais baseados nas reservas processadas.

        Args:
            reservations (List[Dict]): Lista de reservas processadas.
            include_canceled (bool): Indica se as reservas canceladas devem ser incluídas no cálculo.

        Returns:
            Dict: Resumo das reservas.
        """
        if not include_canceled:
            valid_reservations = [
                res for res in reservations
                if res.get("status") not in ["Cancelado pelo hóspede", "Cancelada pelo Airbnb"]
            ]
        else:
            valid_reservations = reservations

        status_count = {}
        for res in reservations:
            status = res.get("status", "unknown")
            status_count[status] = status_count.get(status, 0) + 1

        if not valid_reservations:
            logging.warning("[RESUMO] Nenhuma reserva válida encontrada.")
            return {
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reservations_sum": 0,
                "earnings_sum": "R$0,00",
                "nights_sum": 0,
                "status_count": status_count,
                "guest_details": {},
                "reservations_per_property": {},
                "earnings_per_property": {},
            }

        earnings_sum = sum(res.get("earnings", 0) for res in valid_reservations)
        nights_sum = sum(res.get("nights", 0) for res in valid_reservations)
        property_count = {}
        property_earnings = {}

        guest_details = {
            "adults_sum": sum(res["guest"]["details"].get("adults", 0) for res in valid_reservations),
            "children_sum": sum(res["guest"]["details"].get("children", 0) for res in valid_reservations),
            "infants_sum": sum(res["guest"]["details"].get("infants", 0) for res in valid_reservations),
            "pets_sum": sum(res["guest"]["details"].get("pets", 0) for res in valid_reservations),
        }

        for res in valid_reservations:
            property_name = res.get("property_name", "Unknown")
            property_count[property_name] = property_count.get(property_name, 0) + 1
            property_earnings[property_name] = property_earnings.get(property_name, 0) + res.get("earnings", 0)

        reservations_sum = len(valid_reservations)

        sorted_property_count = {
            k: {
                "count": v,
                "percentage": f"{(v / reservations_sum) * 100:.2f}%",
            }
            for k, v in sorted(property_count.items(), key=lambda item: item[1], reverse=True)
        }

        sorted_property_earnings = {
            k: {
                "earnings": f"R${v:,.2f}",
                "percentage": f"{(v / earnings_sum) * 100:.2f}%",
                "average_per_reservation": f"R${(v / property_count[k]):,.2f}" if property_count[k] > 0 else "R$0,00",
            }
            for k, v in sorted(property_earnings.items(), key=lambda item: item[1], reverse=True)
        }

        return {
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reservations_sum": reservations_sum,
            "earnings_sum": f"R${earnings_sum:,.2f}",
            "nights_sum": nights_sum,
            "status_count": dict(sorted(status_count.items(), key=lambda item: item[1], reverse=True)),
            "guest_details": guest_details,
            "reservations_per_property": sorted_property_count,
            "earnings_per_property": sorted_property_earnings,
        }

    def fetch_reservations(self) -> List[Dict]:
        """
        Recupera todas as reservas disponíveis utilizando paginação.

        Returns:
            List[Dict]: Lista de reservas processadas.
        """
        offset = 0
        limit = self.params["_limit"]
        all_reservations = []

        while True:
            self.params["_offset"] = offset
            try:
                logging.info(f"[REQUISIÇÃO] Buscando reservas (página: {offset}, limite: {limit}).")
                response = requests.get(
                    f"{self.BASE_URL}/api/v2/reservations",
                    headers=self.headers,
                    params=self.params,
                )
                response.raise_for_status()
                data = response.json()

                reservations = data.get("reservations", [])
                if not reservations:
                    break

                all_reservations.extend(self.process_reservation(res) for res in reservations)
                offset += limit

            except requests.RequestException as e:
                logging.error(f"[ERRO] Falha na comunicação com a API: {e}.")
                break

        logging.info(f"[FINALIZADO] Total de reservas recuperadas: {len(all_reservations)}.")
        return all_reservations

    def get_reservations_as_json(self, indent: int = 4, sort_by: str = None, sort_order: str = "asc", start_date: str = None, end_date: str = None, date_filter_field: str = "check_in") -> str:
        """
        Recupera as reservas e as retorna no formato JSON com resumo, filtradas e ordenadas conforme especificado.

        Args:
            indent (int): Espaçamento para a formatação do JSON.
            sort_by (str): Campo pelo qual as reservas devem ser ordenadas.
            sort_order (str): Ordem da ordenação ('asc' ou 'desc').
            start_date (str): Data inicial do filtro no formato 'YYYY-MM-DD'.
            end_date (str): Data final do filtro no formato 'YYYY-MM-DD'.
            date_filter_field (str): Campo de data usado no filtro ('check_in', 'check_out', 'booking_date').

        Returns:
            str: Reservas formatadas como string JSON.
        """
        reservations = self.fetch_reservations()

        if not reservations:
            logging.warning("[RESULTADO] Nenhuma reserva encontrada.")
            return json.dumps({"message": "Nenhuma reserva encontrada."}, ensure_ascii=False, indent=indent)

        valid_date_fields = ["check_in", "check_out", "booking_date"]
        if date_filter_field not in valid_date_fields:
            logging.error(f"[ERRO] Campo de filtro de data inválido: {date_filter_field}.")
            return json.dumps({"message": f"Campo de filtro de data inválido: {date_filter_field}."}, ensure_ascii=False, indent=indent)

        if start_date or end_date:
            try:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

                def is_within_date_range(reservation):
                    date_field_value = reservation.get(date_filter_field, "")
                    if not date_field_value:
                        return False
                    reservation_date = datetime.datetime.strptime(date_field_value, "%Y-%m-%d")
                    return ((not start_date or reservation_date >= start_date) and
                            (not end_date or reservation_date <= end_date))

                reservations = [res for res in reservations if is_within_date_range(res)]
            except Exception as e:
                logging.error(f"[ERRO] Falha ao filtrar por período de datas: {e}.")
                return json.dumps({"message": "Erro ao filtrar por período de datas."}, ensure_ascii=False, indent=indent)

        if sort_by:
            try:
                reservations.sort(
                    key=lambda res: res.get(sort_by, ""),
                    reverse=(sort_order.lower() == "desc")
                )
            except Exception as e:
                logging.error(f"[ERRO] Falha ao ordenar reservas pelo campo '{sort_by}': {e}.")
                return json.dumps({"message": f"Erro ao ordenar pelo campo '{sort_by}'."}, ensure_ascii=False, indent=indent)

        summary = self.calculate_summary(reservations)
        data_completa = {
            "summary": summary,
            "reservations": reservations,
        }

        return json.dumps(data_completa, ensure_ascii=False, indent=indent)
