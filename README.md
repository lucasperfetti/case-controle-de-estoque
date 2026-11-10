# Documentação do Projeto --- Sistema de Controle de Estoque

## 1. Visão geral da solução

O projeto consiste em uma aplicação web para controle básico de estoque,
desenvolvida em Python utilizando o framework Django e banco de dados
SQLite.

A solução permite cadastrar produtos e acompanhar suas quantidades em
diferentes situações:

-   **Quantidade total:** quantidade física registrada no estoque.
-   **Quantidade disponível:** quantidade que pode ser utilizada em
    novas operações.
-   **Quantidade reservada:** quantidade separada para uma reserva
    ativa.
-   **Quantidade bloqueada:** quantidade temporariamente indisponível
    por um bloqueio ativo.

O sistema contempla as seguintes operações:

  -----------------------------------------------------------------------
  Operação                            Comportamento
  ----------------------------------- -----------------------------------
  Entrada                             Aumenta a quantidade total e a
                                      disponível.

  Saída                               Diminui a quantidade total e a
                                      disponível, desde que exista saldo
                                      disponível suficiente.

  Reserva                             Transfere uma quantidade da
                                      disponível para a reservada e gera
                                      uma identificação para consulta e
                                      liberação.

  Bloqueio                            Transfere uma quantidade da
                                      disponível para a bloqueada e gera
                                      uma identificação para consulta e
                                      liberação.

  Liberação                           Localiza uma reserva ou bloqueio
                                      ativo pela identificação e devolve
                                      a quantidade à disponível.

  Consulta                            Apresenta as quantidades atuais de
                                      um produto.
  -----------------------------------------------------------------------

A aplicação também mantém registros das movimentações, permitindo
consultar o histórico das operações realizadas.

## 2. Arquitetura e estrutura adotada

Foi adotada uma arquitetura simples, organizada em um projeto Django
chamado `config` e uma aplicação chamada `estoque`.

A estrutura planejada é:

``` text
projeto/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── estoque/
│   ├── migrations/
│   ├── templates/
│   │   └── estoque/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── produtos.html
│   │       ├── cadastrar_produto.html
│   │       ├── operacao.html
│   │       ├── liberar.html
│   │       └── consultar.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── services.py
├── manage.py
├── db.sqlite3
└── requirements.txt
```

### Responsabilidade dos principais arquivos

-   **`models.py`:** define as entidades persistidas no banco de dados,
    principalmente `Produto` e `Movimentacao`.
-   **`views.py`:** recebe as requisições, coordena formulários e
    serviços e seleciona as páginas que serão exibidas.
-   **`forms.py`:** define e valida os dados enviados pelo usuário.
-   **`services.py`:** concentra as regras de negócio das operações de
    estoque, evitando deixar essas regras espalhadas pelas views.
-   **`urls.py`:** associa os endereços da aplicação às respectivas
    views.
-   **`templates/`:** contém as páginas HTML renderizadas pelo Django.
-   **`static/`:** contém arquivos estáticos, como folhas de estilo.
-   **`settings.py`:** concentra as configurações gerais do projeto
    Django.
-   **`db.sqlite3`:** arquivo do banco de dados SQLite utilizado no
    ambiente local.

### Fluxo simplificado de uma operação

1.  O usuário acessa uma página e preenche um formulário.
2.  O Django recebe a requisição e valida os dados por meio de um
    formulário.
3.  A view chama a função correspondente em `services.py`.
4.  O serviço verifica as regras de negócio e atualiza o produto e o
    registro da movimentação.
5.  A operação é confirmada no banco de dados e o usuário recebe uma
    mensagem de sucesso ou erro.

A interface utiliza Django Templates e Bootstrap 5.3.3. O backend é
responsável pela validação e execução das regras de negócio.

## 3. Principais decisões técnicas

### Django

O Django foi escolhido por oferecer uma estrutura integrada para
desenvolvimento web, incluindo roteamento, formulários, ORM, templates,
proteção CSRF e gerenciamento de banco de dados.

### SQLite

O SQLite foi adotado como banco de dados inicial por ser simples de
configurar e suficiente para desenvolvimento, demonstração e uso local
de baixa concorrência. Não exige a instalação de um servidor de banco de
dados separado.

### Separação entre views e serviços

As views cuidam da comunicação HTTP e da apresentação. As regras que
alteram o estoque ficam concentradas em `services.py`. Essa separação
facilita testes, manutenção e eventual reutilização das operações.

### Modelagem de dados

A entidade `Produto` armazena a identificação e os quatro saldos do
estoque. A entidade `Movimentacao` registra cada operação, incluindo
produto, tipo, quantidade, identificação, status e data de criação.

As identificações das movimentações são únicas. Quando o usuário não
informa uma identificação, o sistema pode gerar uma automaticamente.

### Integridade das quantidades

A regra central do estoque é:

``` text
quantidade_total =
    quantidade_disponivel +
    quantidade_reservada +
    quantidade_bloqueada
```

As operações devem preservar essa igualdade e impedir quantidades
negativas.

### Transações

As funções de operação e liberação utilizam transações atômicas do
Django. Assim, se ocorrer uma falha durante a atualização do produto ou
a criação/alteração da movimentação, as alterações da transação são
revertidas.

As reservas e os bloqueios possuem status. Somente registros ativos
podem ser liberados, impedindo que a mesma operação seja liberada
novamente pelo fluxo normal da aplicação.

## 4. Premissas consideradas

O desenvolvimento considera as seguintes premissas:

-   Cada produto possui uma identificação única.
-   As quantidades são números inteiros positivos ou zero; não há
    controle de unidades fracionárias.
-   Um produto pode ter saldo disponível, reservado e bloqueado
    simultaneamente.
-   Reservas e bloqueios consomem o saldo disponível, mas não reduzem a
    quantidade total.
-   Uma saída reduz tanto o total quanto o disponível.
-   Uma entrada aumenta tanto o total quanto o disponível.
-   A liberação de uma reserva ou bloqueio devolve a quantidade
    correspondente ao saldo disponível.
-   Uma reserva ou bloqueio liberado não pode ser liberado novamente.
-   O histórico das movimentações é mantido; liberar uma operação altera
    seu status, em vez de apagar seu registro.
-   O sistema é inicialmente voltado a um cenário simples, com poucos
    usuários e baixa concorrência.
-   A aplicação é executada em ambiente local durante a fase inicial.

## 5. Limitações conhecidas

A solução atende a um fluxo básico de controle de estoque, mas possui
limitações importantes:

1.  **Banco de dados:** SQLite é adequado para desenvolvimento e
    aplicações pequenas, mas pode apresentar limitações de concorrência
    e escalabilidade quando há várias operações simultâneas.
2.  **Concorrência:** o método `select_for_update()` utilizado pelo
    Django não oferece bloqueio efetivo de linhas no SQLite como ocorre
    em bancos de dados como PostgreSQL. Portanto, não se deve considerar
    o código atual suficiente para proteger operações concorrentes em
    produção.
3.  **Autenticação e autorização:** não há, no escopo atual, definição
    completa de usuários, perfis ou permissões para restringir
    operações.
4.  **Auditoria:** o histórico registra as movimentações de estoque, mas
    não contempla necessariamente o usuário responsável, justificativas,
    origem da operação ou trilha de auditoria imutável.
5.  **Unidades fracionárias:** o modelo utiliza números inteiros.
    Produtos controlados por peso, volume ou medidas fracionárias
    exigiriam outro tipo de representação e regras de precisão.
6.  **Finalização de reservas:** o fluxo atual permite liberar reservas
    e bloqueios. Não foi implementado um processo específico para
    confirmar uma reserva como saída efetiva do estoque.
7.  **Validação operacional:** não há, no escopo atual, recursos
    completos para inventário físico, ajuste de divergências, múltiplos
    depósitos, lotes, validade ou rastreamento por localização.
8.  **Tratamento de falhas:** o tratamento de erros pode ser ampliado
    para lidar de forma mais amigável com identificações duplicadas e
    falhas inesperadas de banco de dados.
9.  **Testes automatizados:** a solução precisa de uma suíte abrangente
    de testes unitários e de integração para validar regras, erros e
    cenários de concorrência.
10. **Implantação:** o servidor de desenvolvimento do Django não deve
    ser utilizado como servidor de produção. Configurações de segurança,
    arquivos estáticos, HTTPS e monitoramento ainda precisam ser
    preparados.

## 6. Instruções para execução

### 6.1. Pré-requisitos

-   Python instalado e disponível no terminal.
-   pip instalado.
-   Acesso ao diretório do projeto.

### 6.2. Preparar o ambiente

No terminal, entre na pasta que contém o arquivo `manage.py`.

Crie um ambiente virtual:

``` bash
python -m venv venv
```

Ative-o no Windows:

``` bash
venv\Scripts\activate
```

Instale as dependências:

``` bash
pip install -r requirements.txt
```


### 6.4. Criar e aplicar as migrações

Execute:

``` bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
```

O comando `check` verifica problemas comuns na configuração.
`makemigrations` gera os arquivos de migração a partir dos modelos e
`migrate` aplica essas migrações ao banco de dados.

### 6.5. Iniciar a aplicação

Execute:

``` bash
python manage.py runserver
```

Por padrão, a aplicação ficará disponível em:

``` text
http://127.0.0.1:8000/
```

Para interromper o servidor, pressione `Ctrl + C` no terminal.

### 6.6. Observações

-   Execute os comandos a partir da pasta que contém `manage.py`.
-   Ative o ambiente virtual antes de instalar dependências ou iniciar o
    projeto.
-   Não apague `db.sqlite3` se desejar preservar os dados cadastrados.
-   Se os modelos forem alterados, gere e aplique as migrações
    novamente.
-   O endereço padrão do servidor de desenvolvimento é destinado a
    testes locais, não à exposição pública da aplicação.

## 7. O que seria diferente em um ambiente real de produção

Caso a solução precisasse operar em um ambiente real, com usuários
simultâneos e dados importantes, eu faria as seguintes evoluções antes
da implantação:

### Banco de dados e concorrência

-   Migraria do SQLite para PostgreSQL.
-   Revisaria a estratégia de concorrência e garantiria que as operações
    de estoque fossem executadas de forma segura e atômica.
-   Utilizaria bloqueios transacionais apropriados no banco de dados,
    como `select_for_update()` no PostgreSQL, acompanhados de tratamento
    de conflitos e tentativas controladas quando necessário.
-   Avaliaria restrições no próprio banco para reforçar integridade,
    além das validações da aplicação.

### Segurança e controle de acesso

-   Implementaria autenticação obrigatória.
-   Criaria perfis e permissões, por exemplo: administrador, operador e
    consulta.
-   Restringiria operações conforme a responsabilidade de cada perfil.
-   Configuraria HTTPS, cookies seguros, proteção de segredos e
    variáveis de ambiente.
-   Revisaria `DEBUG`, `ALLOWED_HOSTS`, CSRF, CORS (se aplicável) e
    demais configurações de segurança do Django.
-   Evitaria armazenar senhas, chaves ou credenciais diretamente no
    código-fonte.

### Auditoria e rastreabilidade

-   Registraria o usuário responsável por cada movimentação.
-   Armazenaria data, hora, tipo, quantidade, justificativa e demais
    informações relevantes.
-   Preservaria uma trilha de auditoria adequada, evitando alterações ou
    exclusões indevidas do histórico.
-   Criaria procedimentos formais para correções e ajustes de estoque,
    sem apagar o histórico original.

### Regras de negócio

-   Implementaria o fluxo de confirmação ou cancelamento de reservas,
    com transições de status bem definidas.
-   Avaliaria suporte a múltiplos depósitos, endereços, lotes, números
    de série e datas de validade, conforme a necessidade do negócio.
-   Definiria regras para inventário físico, ajustes e conciliação de
    divergências.
-   Padronizaria o tratamento de identificações duplicadas e erros de
    operação.
-   Consideraria unidades de medida e quantidades decimais caso os
    produtos exigissem esse controle.

### Qualidade e testes

-   Criaria testes unitários para cada regra de negócio.
-   Criaria testes de integração para os fluxos completos de entrada,
    saída, reserva, bloqueio e liberação.
-   Testaria tentativas de operações inválidas, saldos insuficientes,
    identificações duplicadas e liberações repetidas.
-   Realizaria testes específicos de concorrência para garantir que duas
    operações simultâneas não consumam o mesmo saldo disponível.
-   Integraria os testes a um pipeline de CI/CD para executar
    verificações automaticamente a cada alteração.

### Infraestrutura, operação e manutenção

-   Utilizaria um servidor WSGI/ASGI apropriado para produção, em vez de
    `runserver`.
-   Prepararia a coleta e publicação de arquivos estáticos.
-   Configuraria logs estruturados, monitoramento, alertas e
    acompanhamento de erros.
-   Criaria rotinas de backup e procedimentos testados de restauração do
    banco de dados.
-   Separaria ambientes de desenvolvimento, homologação e produção.
-   Automatizaria implantação e migrações com um processo controlado de
    CI/CD.
-   Documentaria procedimentos de recuperação, atualização e manutenção.