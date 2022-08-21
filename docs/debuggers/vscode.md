# Visual Studio Code

O [Visual Studio Code](https://code.visualstudio.com/) (ou VS Code) pode ser utilizado para executar o debug do AWS Lambda, para isso é necessário ter instalado a [extenção do Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python), e executar o Queue Lambda Debugger como um módulo do Python, passando os parâmetros `run <event_source_mapping_name>`.

Exemplo de configuração do arquivo `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Lambda myrun",
      "type": "python",
      "request": "launch",
      "module": "qldebugger",
      "args": ["run", "myrun"],
      "justMyCode": true
    }
  ]
}
```
