## Automata manager

Um sistema web simples com uma API RESTful e um frontend para gerenciar autômatos finitos determinísticos, autômatos com pilha não determinísticos e máquinas de Turing.

- Trabalho da disciplina Teoria da Computação da UFLA
- Visualização gráfica dos autômatos criados.
- Verificação de palavras para determinar se são aceitas pelo autômato.
- Frontend interativo para criação e teste de autômatos.

### Tecnologias utilizadas

* `automata_lib v9.0.0`
* `fastapi v0.115.8`
* `graphviz v0.20.3`
* `pydantic v2.10.6`
* `uvicorn v0.34.0`
* `javascript + html + css`

### Executando o projeto localmente

1. Instale o GraphViz:
   * Ubuntu/Debian: `sudo apt-get install graphviz`
   * MacOS: `brew install graphviz`
   * Windows: Baixe e instale do [site oficial](https://graphviz.org/download/)

2. Para executar o `backend`, na raiz do projeto, execute os seguintes comandos:

```bash
python3 -m venv ./.venv
source .venv/bin/activate
cd backend
pip install -r requirements.txt
uvicorn main:app
```

3. Para executar o `frontend`, vá ao diretório frontend e abra o arquivo `index.html` pelo navegador. 

### Estrutura do projeto

```
├── fastapi-backend
│   ├── images
│   ├── main.py
│   ├── requirements.txt
│   ├── routers
│   └── tests
├── frontend
│   ├── index.html
│   └── static
└── README.md
```

### Endpoints da API

#### **DFA (Autômato Finito Determinístico)**
   * `POST /api/dfa/` → Cria um novo DFA  
   * `GET /api/dfa/{dfa_id}` → Obtém informações do DFA  
   * `PUT /api/dfa/{dfa_id}` → Atualiza um DFA existente  
   * `POST /api/dfa/{dfa_id}/verify` → Testa uma string no DFA  
   * `GET /api/dfa/{dfa_id}/save-image` → Gera e salva uma imagem do DFA  

#### **PDA (Autômato com Pilha)**
   * `POST /api/pda/` → Cria um novo PDA  
   * `GET /api/pda/{pda_id}` → Obtém informações do PDA  
   * `PUT /api/pda/{pda_id}` → Atualiza um PDA existente  
   * `POST /api/pda/{pda_id}/verify` → Testa uma string no PDA  
   * `GET /api/pda/{pda_id}/save-image` → Gera e salva uma imagem do PDA  

#### **TM (Máquina de Turing)**
   * `POST /api/mt/` → Cria uma nova MT  
   * `GET /api/mt/{mt_id}` → Obtém informações da MT  
   * `PUT /api/mt/{mt_id}` → Atualiza uma MT existente  
   * `POST /api/mt/{mt_id}/verify` → Testa uma string na MT  
   * `GET /api/mt/{mt_id}/save-image` → Gera e salva uma imagem da MT  

### Exemplos de Uso

#### 1. Criando um automato finito deterministico
* Exemplo: Cria um AFD que aceita números binários múltiplos de 3
```json
{
  "states": ["q0", "q1", "q2"],
  "input_symbols": ["0", "1"],
  "transitions": {
    "q0": {
      "0": "q0",
      "1": "q1"
    },
    "q1": {
      "0": "q2",
      "1": "q0"
    },
    "q2": {
      "0": "q1",
      "1": "q2"
    }
  },
  "initial_state": "q0",
  "final_states": ["q0"]
}
```

#### 2. Criando um automato com pilha
* Exemplo: Cria um AP que aceita palindromos pares entre 0s e 1s
```json
{
  "states": ["q0", "q1", "q2"],
  "input_symbols": ["0", "1"],
  "stack_symbols": ["0", "1", "Z"],
  "transitions": {
    "q0": {
      "0": {
        "Z": [["q0", ["0", "Z"]]],
        "0": [["q0", ["0", "0"]]],
        "1": [["q0", ["0", "1"]]]
      },
      "1": {
        "Z": [["q0", ["1", "Z"]]],
        "0": [["q0", ["1", "0"]]],
        "1": [["q0", ["1", "1"]]]
      },
      "": {
        "Z": [["q2", ["Z"]]],
        "0": [["q1", ["0"]]],
        "1": [["q1", ["1"]]]
      }
    },
    "q1": {
      "0": {
        "0": [["q1", []]]
      },
      "1": {
        "1": [["q1", []]]
      },
      "": {
        "Z": [["q2", ["Z"]]]
      }
    }
  },
  "initial_state": "q0",
  "initial_stack_symbol": "Z",
  "final_states": ["q2"]
}

```

#### 3. Criando uma MT
* Exemplo: Cria uma máquina de turing que aceita palindromos de quaisquer tamanho entre 0s e 1s

```json
{
  "states": ["q0", "q1", "q2", "q3", "qf"],
  "input_symbols": ["0", "1"],
  "tape_symbols": ["0", "1", "X", "Y", "*"],
  "transitions": {
    "q0": {
      "0": ["q1", "X", "R"],
      "1": ["q2", "Y", "R"],
      "*": ["q3", "*", "R"]
    },
    "q1": {
      "0": ["q1", "0", "R"],
      "1": ["q1", "1", "R"],
      "*": ["q2", "*", "L"]
    },
    "q2": {
      "0": ["q2", "0", "L"],
      "1": ["q2", "1", "L"],
      "X": ["q0", "X", "R"],
      "Y": ["q0", "Y", "R"]
    },
    "q3": {
      "X": ["q3", "X", "R"],
      "Y": ["q3", "Y", "R"],
      "*": ["qf", "*", "R"]
    }
  },
  "initial_state": "q0",
  "blank_symbol": "*",
  "final_states": ["qf"]
}

```



