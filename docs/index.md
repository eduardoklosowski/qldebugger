# Queue Lambda Debugger

O [Queue Lambda Debugger](https://github.com/eduardoklosowski/qldebugger) é uma ferramenta para receber mensagens de um [Amazon Simple Queue Service (Amazon SQS)](https://aws.amazon.com/sqs/), simulando um [AWS Lambda *event source mapping*](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html), e executar localmente o código de um [AWS Lambda](https://aws.amazon.com/lambda/).

Permitindo utilizar ferramentas de debug para acompanhar a execução do AWS Lambda. Junto com alguma ferramenta que simula o Amazon SQS, como o [Moto](http://docs.getmoto.org/en/latest/) ou o [LocalStack](https://localstack.cloud/), permite a execução do código localmente, sem precisar de conexão com a internet ou conta na [AWS](https://aws.amazon.com/).
