# Primeiros passos

## Instalando o Queue Lambda Debugger

O Queue Lambda Debugger é testado no Python 3.8 ou superior e pode ser instalado pelo `pip` (ou outra ferramenta de gerenciamento de dependência, como o [Poetry](https://python-poetry.org/)). Exemplo:

```sh
pip install qldebugger
```

## Criando configuração básica

A configuração do Queue Lambda Debugger fica no arquivo `qldebugger.toml` dentro do diretório do projeto, ela é escrita no formato [TOML v1.0.0](https://toml.io/en/v1.0.0). Um exemplo de configuração pode ser criado executando o comando:

```sh
qldebugger init
```

Após isso é necessário ajustar a configuração de acesso a AWS na seção `aws` dentro do arquivo de configuração. A configuração a baixo é válida para utilizar um mock:

```toml
[aws]
access_key_id = "secret"
secret_access_key = "secret"
region = "us-east-1"
endpoint_url = "http://localhost:4566/"
```

Também é possível remover toda a seção `aws` do arquivo de configuração para que o Queue Lambda Debugger utilize as credenciais de acesso a AWS já configurada no ambiente.

Um mock da AWS pode ser iniciado executando os comandos a baixo em outra janela:

```sh
pip install moto[server]
moto_server -p 4566
```

## Criando filas

As filas no Amazon SQS são configuradas na seção `queues` do arquivo de configuração, e suas criações no mock podem ser feitas através do CLI com o comando:

```sh
qldebugger infra create-queues
```

## Enviando mensagens

Para enviar mensagens para a fila, pode ser utilizado o comando `qldebugger msg send <nome-da-fila> <mensagem>`. Exemplo:

```sh
qldebugger msg send myqueue "test message"
```

## Executando AWS Lambda

A configuração do AWS Lambda é feita na seção `lambdas` do arquivo de configuração, passando a localização da função Python a ser executada no parâmetro `handler`. Exemplo:

```toml
[lambdas]
print = {handler = "qldebugger.example.lambdas.print_messages"}
```

Para informar de qual fila as mensagens devem ser recebidas para enviar para o AWS Lambda, isso é feito na seção `event_source_mapping` do arquivo de configuração, criando um nome que será utilizado para rodar o AWS Lambda e informando o nome da fila e do lambda. Exemplo:

```toml
[event_source_mapping]
myrun = {queue = "myqueue", function_name = "print"}
```

Assim basta executar o comando `qldebugger run <nome-do-event-source-mapping>`. Exemplo:

```sh
qldebugger run myrun
```

Exemplo de saída no terminal:

```txt
INFO:qldebugger:Receved 1 messages from 'myqueue' queue
INFO:qldebugger:Running 'print' lambda...
test message
Total: 1 messages
INFO:qldebugger:Result: None
INFO:qldebugger:Deleted 1 messages from 'myqueue' queue
```

## Executando sua própria função AWS Lambda

A função Python para executar no AWS Lambda pode ser escrita em qualquer módulo Python, nesse exemplo ela foi escrita no arquivo `func.py`:

```python
def handler(event, context):
    print(event)
```

Depois disso é necessário configurá-la na seção `lambdas` no arquivo `qldebugger.toml`, assim como o `event_source_mapping` descrevendo de qual fila as mensagens devem ser recebidas:

```toml
[lambdas]
mylambda = {handler = "func.handler"}

[event_source_mapping]
myrun = {queue = "myqueue", function_name = "mylambda"}
```

Após isso é possível enviar mensagens e executar o AWS Lambda. Porém nesse caso, como o módulo Python não está em nenhum pacote instalado no ambiente, pode ser necessário usar a variável de ambiente `PYTHONPATH` informando ao Python onde ele deve procurar os módulos a serem importados, nesse caso o diretório atual (`.`). Exemplo:

```sh
qldebugger msg send myqueue "test message"
PYTHONPATH=. qldebugger run myrun
```
