# Email AI Classifier

Este projeto é uma solução completa de engenharia de software para o desafio de triagem e resposta automatizada de e-mails corporativos. O sistema utiliza Inteligência Artificial Generativa (Google Gemini via Vertex AI) para classificar mensagens recebidas entre "Produtivas" e "Improdutivas" e sugerir respostas contextualizadas, reduzindo o tempo gasto em tarefas operacionais manuais.

## Tecnologias Utilizadas

A arquitetura foi desenhada priorizando performance, manutenibilidade e escalabilidade serverless.

*   **FastAPI**: Framework web moderno e de alta performance. Escolhido por seu suporte nativo a programação assíncrona, validação de dados via Pydantic e facilidade de criação de APIs RESTful.
*   **Google Vertex AI (Gemini 2.5-pro)**: Motor de IA Generativa. Utilizado pela sua janela de contexto, capacidade de raciocínio lógico e integração segura via IAM (sem chaves de API expostas no código).
*   **HTMX & Jinja2**: Abordagem *Hypermedia-Driven*. Permite interatividade dinâmica no frontend (SPA-feel) sem a complexidade de build steps de frameworks como React/Vue, mantendo a renderização no servidor (SSR) e simplificando a stack.
*   **uv**: Gerenciador de pacotes e projetos Python ultra-rápido (substituto moderno ao pip/poetry), garantindo builds determinísticos e tempos de instalação reduzidos no CI/CD.
*   **Docker & Cloud Run**: O projeto foi containerizado para ser agnóstico de infraestrutura, pronto para deploy escalável e *stateless* no Google Cloud Run.
*   **pdfminer.six**: Biblioteca robusta para extração de texto de PDFs, permitindo que o sistema processe anexos além de texto puro.
*   **Tailwind CSS**: Framework *utility-first* para estilização rápida e responsiva, mantendo um design system consistente.

## Como Rodar o Projeto Localmente

### Pré-requisitos
*   Python 3.10+
*   [uv](https://github.com/astral-sh/uv) instalado
*   Acesso a um projeto Google Cloud com a API Vertex AI habilitada
*   **Configuração de Autenticação GCP** (Veja instruções detalhadas abaixo)

### 1. Instalação e Configuração

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/email-ai-classifier.git
cd email-ai-classifier
uv sync
```

**Configuração do Ambiente e GCP:**

Para configurar corretamente o projeto no Google Cloud (criar Service Account, baixar chaves JSON) e conectar sua aplicação local, siga o guia dedicado:

👉 **[Guia Passo-a-Passo: Configuração GCP e Variáveis de Ambiente](GCP_SETUP.md)** 👈

Após seguir o guia acima, seu arquivo `.env` estará pronto.

### 2. Executando a Aplicação

Inicie o servidor de desenvolvimento:

```bash
uv run uvicorn app.main:app --reload --port 8080
```

Acesse a interface em: `http://localhost:8080`

### 3. Via Docker (Alternativa)

```bash
docker build -t email-classifier .
docker run -p 8080:8080 --env-file .env -v ~/.config/gcloud:/root/.config/gcloud email-classifier
```
*Nota: A montagem de volume do gcloud é necessária para autenticação local dentro do container, a menos que esteja usando Service Account keys.*

## Como Funciona a IA

A inteligência do sistema reside na orquestração de prompts e chamadas à API Vertex AI.

### Classificação (Produtivo vs Improdutivo)
O core da classificação utiliza o modelo **Gemini 2.5-pro** com temperatura `0.0` para maximizar o determinismo.
1.  **Extração**: O texto é extraído de inputs diretos ou arquivos PDF, passando por limpeza de HTML e *stopwords*.
2.  **Prompt Engineering**: Um prompt estruturado (`app/prompts/email_classifier.prompt`) define regras rígidas de negócio. Ele instrui o modelo a analisar a *intencionalidade* do e-mail (ex: solicitação de ação vs. notificação automática) e não apenas palavras-chave.
3.  **Output Estruturado**: O modelo é forçado a retornar um JSON estrito contendo `category`, `confidence` (0.0 a 1.0) e `reason`. Isso garante que a aplicação possa tratar a resposta programaticamente sem falhas de *parsing*.

### Geração de Resposta
Caso o e-mail seja classificado, o sistema aciona um segundo fluxo (pipeline) que gera uma sugestão de resposta baseada na categoria e no conteúdo original, mantendo tom profissional e objetivo.

## Decisões Técnicas

*   **Renderização Server-Side com HTMX**: Optei por não separar o frontend em um repositório/build isolado (ex: Next.js) para reduzir a complexidade operacional. O HTMX permite atualizações parciais da DOM (via AJAX) retornando HTML do backend, o que é ideal para ferramentas internas e dashboards administrativos onde o SEO não é prioridade, mas a velocidade de desenvolvimento é.
*   **Segurança via IAM**: Não há chaves de API "hardcoded". O uso de `vertexai.init()` aproveita o *Application Default Credentials* (ADC) do Google. Isso significa que a segurança é gerenciada por roles do IAM (Identity and Access Management), prática recomendada para ambientes corporativos.
*   **Validação Defensiva**: O código implementa tratativas específicas para alucinações de formato do LLM (ex: `InvalidResponseJsonError`). Mesmo com instruções claras, LLMs podem falhar; o sistema está preparado para capturar esses erros e informar o usuário elegantemente.
*   **Arquitetura em Camadas**:
    *   `app/api`: Apenas definição de rotas e injeção de dependências.
    *   `app/services`: Lógica de negócio e integração com Vertex AI.
    *   `app/prompts`: Prompts externalizados em arquivos `.prompt` para facilitar ajustes sem necessidade de *redeploy* de código.

## Limitações e Melhorias Futuras

Embora funcional, esta versão representa um MVP (Minimum Viable Product). Em um cenário de produção em larga escala, as seguintes evoluções seriam prioritárias:

### Limitações Atuais
*   **Chamadas Síncronas**: Atualmente, a chamada ao Vertex AI bloqueia a thread de execução. Embora o FastAPI gerencie isso com threadpools, sob alta carga, isso pode se tornar um gargalo.
*   **Contexto Único**: O sistema analisa cada e-mail isoladamente, sem conhecimento de threads anteriores ou histórico do cliente.

### Roadmap de Melhorias
1.  **Assincronismo Real**: Migrar para a versão `AsyncGenerativeModel` do SDK da Vertex AI para liberar o *Event Loop* durante a inferência, aumentando drasticamente o throughput.
2.  **Fila de Processamento (Celery/Arq)**: Para volumes massivos, mover o processamento de IA para background jobs, retornando um ID de tarefa para o frontend (polling ou WebSocket).
3.  **Feedback Loop (RLHF)**: Implementar botões de "Joinha/Joinha invertido" na interface para coletar feedback humano sobre a classificação e refinar o modelo via *Fine-tuning* ou *Few-shot prompting* dinâmico.
4.  **Cache Semântico**: Utilizar Redis para armazenar hash de e-mails repetidos (comuns em spam/notificações), economizando custos de API.
5.  **Observabilidade**: Implementar OpenTelemetry para rastrear latência das chamadas ao Gemini e custos por token.
