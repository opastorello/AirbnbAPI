# AirbnbAPI - Automação de Coleta de Reservas

Este projeto permite automatizar a coleta de dados de reservas do Airbnb utilizando a API privada da plataforma.
Ele fornece as informações de reservas e gera um arquivo JSON contendo os dados formatados, além de fornecer um resumo estatístico detalhado.
## Requisitos

- **Python 3.8 ou superior**
- **Bibliotecas Python:**
  - `requests`
  - `python-dotenv`
- **Conta Airbnb válida** com acesso autenticado (API Key e Cookie necessários).

## Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/opastorello/minhas-reservas.git
   cd minhas-reservas
   ```

2. **Crie um ambiente virtual (opcional):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env`:**

   Crie um arquivo chamado `.env` na raiz do projeto com as seguintes variáveis:

   ```env
   API_KEY=SuaAPIKeyAqui
   COOKIE=SeuCookieAqui
   ```

   Substitua `SuaAPIKeyAqui` e `SeuCookieAqui` pelos valores reais obtidos na sua conta Airbnb.

## Estrutura do Projeto

```plaintext
/
|-- AirbnbAPI.py        # Classe para interagir com a API Airbnb
|-- main.py             # Script principal para executar o fluxo
|-- requirements.txt    # Lista de dependências
|-- .env                # Configurações de autenticação (não incluído no repositório)
|-- README.md           # Documentação do projeto
```

## Uso

1. **Execute o script principal:**

   ```bash
   python main.py
   ```

   O script:
   - Carrega as variáveis de ambiente do arquivo `.env`.
   - Autentica na API Airbnb.
   - Recupera as reservas e as salva no arquivo `reservas.json`.
   - Recupera as reservas e as salva no arquivo `reservas.ics`.
   - Gera logs detalhados da execução no arquivo `reservas.log`.

2. **Verifique o arquivo gerado:**

   O arquivo `reservas.json` conterá os dados das reservas formatados e um resumo estatístico, por exemplo:

   ```json
   {
       "summary": {
           "reservations_sum": 10,
           "earnings_sum": "R$5.000,00",
           "nights_sum": 30,
           "status_count": {
               "Hóspede anterior": 8,
               "Confirmada": 2
           }
       },
       "reservations": [
           {
               "status": "Confirmada",
               "confirmation_code": "ABC123",
               "property_name": "Apartamento Luxo",
               "booking_date": "2025-01-01",
               "check_in": "2025-01-10",
               "check_out": "2025-01-15",
               "nights": 5,
               "earnings": 1000.0,
               "guest": {
                   "name": "João Silva",
                   "phone": "+55 11 99999-9999",
                   "location": "São Paulo, Brasil",
                   "details": {
                       "adults": 2,
                       "children": 1,
                       "infants": 0,
                       "pets": 1
                   }
               }
           }
       ]
   }
   ```

## Logs

Os logs de execução são salvos no arquivo `reservas.log`, contendo informações detalhadas sobre cada etapa, incluindo:
- Inicialização do script.
- Sucesso ou falhas na comunicação com a API.
- Criação do arquivo de saída.

## Benefícios do Projeto

- **Automatização:** Coleta automática de todas as reservas disponíveis na conta Airbnb.
- **Formatado e Pronto para Análise:** Os dados são organizados em JSON para facilitar análises posteriores.
- **Resumo Estatístico:** Inclui um resumo com informações financeiras, noites reservadas e status das reservas.
- **Personalizável:** Parâmetros como idioma, moeda e limites de paginação podem ser ajustados facilmente.

## Contribuição

Contribuições são bem-vindas! Se você encontrar bugs ou tiver ideias para melhorias, abra uma [issue](https://github.com/opastorello/minhas-reservas/issues) ou envie um pull request.

## Próximos Passos

- **Relatórios Adicionais:** Expandir os relatórios gerados com gráficos e tabelas.
- **Melhoria na Documentação:** Adicionar imagens e exemplos de uso mais avançados.
- **Captura de Cookie e Token API:** Adicionar como recuperar os dados de uma sessão.

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo `LICENSE` para mais informações.

