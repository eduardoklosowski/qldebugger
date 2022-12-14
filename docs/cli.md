# CLI

O Queue Lambda Debugger oferece o utilitário `qldebugger` para executar comandos na linha de comando. Exemplo:

```sh
qldebugger <comando>
```

Também é possível executá-lo como um módulo do Python. Exemplo:

```sh
python -m qldebugger <comando>
```

## Comandos

Os comandos oferecidos por esse utilitário são:

### `init`

Esse comando cria um exemplo do arquivo de configuração (`qldebugger.toml`) no diretório atual se ele não existir, caso ele já exista uma mensagem será mostrada, porém seu conteúdo não será alterado.

### `run <event_source_mapping_name>`

Esse comando recebe o nome do um `event_source_mapping` configurado na seção de mesmo nome do arquivo de configuração, recebe mensagens da fila Amazon SQS configurada no parâmetro `queue` e executa o AWS Lambda nomeado no parâmetro `function_name`, exibindo sua saída no terminal.

### `infra create-queues`

Esse comando lê todas as filas Amazon SQS presentes na seção `queues` do arquivo de configuração e envio o comando para criá-la no serviço configurado da AWS.

### `msg send <queue_name> <message>`

Esse comando recebe o nome de uma fila Amazon SQS e uma mensagem, e executa o envio dessa mensagem para a fila no serviço configurado da AWS.
