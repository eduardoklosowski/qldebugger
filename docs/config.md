# Configuração

Toda a configuração do Queue Lambda Debugger fica no arquivo de configuração `qldebugger.toml` no diretório local, que é um arquivo no formato [TOML v1.0.0](https://toml.io/en/v1.0.0). Seus parâmetros são descritos a baixo:

## `aws`

Essa seção descreve a configuração que deve ser utilizada para acessar os serviços da AWS (ou algum mock).

Todos os seus parâmetros são opcionais e a própria seção pode ser omitida, e caso não esteja presente, a configuração atual do ambiente será utilizada.

### `aws.profile`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Nome do profile do arquivo de configuração da AWS que deve ser utilizado para acessar a AWS.

### `aws.access_key_id`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Parâmetro `access_key_id` para acessar a AWS.

### `aws.secret_access_key`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Parâmetro `secret_access_key` para acessar a AWS.

### `aws.session_token`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Parâmetro `session_token` para acessar a AWS.

### `aws.region`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Nome da região da AWS que deve ser utilizada.

### `aws.endpoint_url`

- Parâmetro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

URL do endpoint para acessar a AWS. Normalmente utilizado por mocks.

## `secrets`

Essa seção é opcional e descreve os segredos do SecretsManager utilizados pelo Queue Lambda Debugger. Ela deve ser um dicionário, onde a chave é o nome do segredo, e o valor é um dicionário indicando o tipo de segredo (string ou binário) e seu valor. Exemplos:

```toml
[secrets]
stringSecret = {string = "abc"}
binarySecret = {binary = "123"}
```

### `secrets.*.string`

- Parâmetro obrigatório (conflita com `binary`)
- Tipo: `str`

Valor como string para o segredo.

### `secrets.*.binary`

- Parâmetro obrigatório (conflita com `string`)
- Tipo: `str`

Valor como binário para o segredo.

## `topics`

Essa seção é opcional e descreve os tópicos SNS utilizados pelo Queue Lambda Debugger. Ela deve ser um dicionário, onde a chave é o nome do tópico, e o valor é um dicionário com seus parâmetros conforme descrito a seguir. Exemplos:

```toml
[topics]
mytopic = {}

[[topics.mytopic2.subscribers]]
queue = "myqueue"
raw_message_delivery = true
filter_policy = "{\"status\":[\"success\"]}"
```

### `topics.*.subscribers`

- Parâmetro opcional
- Tipo: `List[ConfigTopicSubscriber]`
- Valor padrão: `[]`

Lista de inscrições para o tópico SNS.

### `topics.*.subscribers[].queue`

- Parâmetro obrigatório
- Tipo: `str`

Nome da fila SQS que deverá se inscrever para receber as mensagens publicadas nesse tópico.

### `topics.*.subscribers[].raw_message_delivery`

- Parâmatro opcional
- Tipo: `bool`
- Valor padrão: `False`

Define se devem ser adicionado campos com informações do tópico nas mensagens entregues na fila SQS.

### `topics.*.subscribers[].filter_policy`

- Pametro opcional
- Tipo: `Optional[str]`
- Valor padrão: `None`

Define um filtro para que apenas as mensagens que atendam os critérios sejam encaminhadas para a fila SQS. O exemplo `{\"status\":[\"success\"]}` encaminhará apenas mensagens com o atributo `status` igual a `success`.

## `queues`

Essa seção é obrigatória e descreve as filas Amazon SQS utilizadas pelo Queue Lambda Debugger. Ela deve ser um dicionário, onde a chave é o nome da fila, e o valor é um dicionário com seus parâmetros. Exemplo:

```toml
[queues]
myqueue = {redrive_policy = {dead_letter_queue = "myqueue2", max_receive_count = 3}}
myqueue2 = {}
```

### `queues.*.redrive_policy`

- Parâmetro opcional
- Tipo: `Optional[ConfigQueueRedrivePolicy]`
- Valor padrão: `None`

Define uma política para retentativas de processamento de mensagens da fila, enviando-a para outra fila ao ocorerrem certa quantidade de erros no processamento daquela mensagem.

### `queues.*.redrive_policy.dead_letter_queue`

- Parâmetro obrigatório
- Tipo: `str`

Nome da fila para onde a mensagem deverá ser enviada após certa quantidade de tentativas de processamento.

### `queues.*.redrive_policy.max_receive_count`

- Parâmetro obrigatório
- Tipo: `int`

Quantas vezes um mesma mensagem pode ser recuperada da fila antes de enviá-la para a fila dead letter.

## `lambdas`

Essa seção é obrigatório e descreve os AWS Lambda utilizados pelo Queue Lambda Debugger. Ela deve ser um dicionário, onde a chave é o nome do lambda, e o valor é um dicionário com seus parâmetros como descritos a seguir.

### `lambdas.*.handler`

- Parâmetro obrigatório
- Tipo: `str`

Caminho da função Python que será executada por esse AWS Lambda. Deve ser escrito na forma `A.B`, de forma que seja possível importar a função com `from A import B`, onde `A` pode conter vários `.` indicando pacotes Python.

### `lambdas.*.environment`

- Parâmetro opcional
- Tipo: `Dict[str, str]`
- Valor padrão: `{}`

Dicionário com as variáveis de ambiente configuradas para a execução do AWS Lambda.

## `event_source_mapping`

Essa seção é obrigatória e descreve os AWS Lambda *event source mapping* utilizados pelo Queue Lambda Debugger. Ela deve ser um dicionário, onde a chave é o nome de um *event source mapping*, e o valor é um dicionário com seus parâmetros como descritos a seguir.

### `event_source_mapping.*.queue`

- Parâmetro obrigatório
- Tipo: `str`

Nome da fila Amazon SQS configurada na seção `queues` que será utilizada para receber mensagens e passar para o AWS Lambda.

### `event_source_mapping.*.batch_size`

- Parâmetro opcional
- Tipo: `int`
- Valor padrão: `10`

Quantidade máxima de mensagens que será requisitada para a fila Amazon SQS e passada para o AWS Lambda.

### `event_source_mapping.*.maximum_batching_window`

- Parâmetro opcional
- Tipo: `int`
- Valor padrão: `0`

Tempo máximo que o cliente Amazon SQS ficará aguardando mensagens (*long polling*). `0` desativa o *long polling*.

### `event_source_mapping.*.function_name`

- Parâmetro obrigatório
- Tipo: `str`

Nome do AWS Lambda configurada na seção `lambdas` que será executada por esse *event source mapping*.
