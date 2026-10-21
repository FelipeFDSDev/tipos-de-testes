# API CRUD de pedidos e testes automatizados

Aplicacao funcional em Python com uma API HTTP para cadastrar, consultar, atualizar e excluir pedidos. Os dados sao armazenados em SQLite no arquivo `orders.sqlite3`. O repositorio tambem demonstra testes unitarios, de integracao e performance, organizados para execucao independente.

## Requisitos e instalacao

Python 3.11 ou superior. Na raiz do projeto, instale a aplicacao e as dependencias de teste:

```powershell
python -m pip install -e ".[test]"
```

## Iniciar a aplicacao

```powershell
python -m test_types_demo
```

A API fica em `http://127.0.0.1:5000`. Envie e receba JSON. Exemplo para criar um pedido, em outro terminal:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/orders -ContentType 'application/json' -Body '{"customer":"Ana","items":[{"name":"Caderno","quantity":2,"price":12.5}]}'
```

Rotas disponiveis:

| Metodo | Rota | Acao |
|---|---|---|
| GET | `/orders` | Lista os pedidos |
| POST | `/orders` | Cria pedido |
| GET | `/orders/<id>` | Consulta pedido |
| PUT | `/orders/<id>` | Atualiza pedido |
| DELETE | `/orders/<id>` | Exclui pedido |

O corpo de POST e PUT usa `customer` e `items`; cada item contem `name`, `quantity` e `price`.

## Executar os testes

```powershell
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v
python -m pytest tests/performance -m performance -v --benchmark-columns=min,mean,median,max
```

Para executar todos os testes: `python -m pytest -v`. A CI no GitHub Actions instala as dependencias e executa cada grupo em uma etapa separada a cada push para `main`, exibindo os resultados nos logs da execucao.
