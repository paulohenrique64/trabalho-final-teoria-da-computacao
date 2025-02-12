let currentType = 'dfa';
let currentAutomatonId = null;

const API_BASE_URL = 'http://localhost:8000';

const sampleConfigs = {
    dfa: {
        states: ["q0", "q1", "q2"],
        input_symbols: ["0", "1"],
        transitions: {
            q0: {
                "0": "q0",
                "1": "q1"
            },
            q1: {
                "0": "q2",
                "1": "q0"
            },
            q2: {
                "0": "q1",
                "1": "q2"
            }
        },
        initial_state: "q0",
        final_states: ["q0"]
    },
    pda: {
        states: ["q0", "q1", "q2"],
        input_symbols: ["0", "1"],
        stack_symbols: ["0", "1", "Z"],
        transitions: {
            q0: {
                "0": {
                    Z: [["q0", ["0", "Z"]]],
                    "0": [["q0", ["0", "0"]]],
                    "1": [["q0", ["0", "1"]]]
                },
                "1": {
                    Z: [["q0", ["1", "Z"]]],
                    "0": [["q0", ["1", "0"]]],
                    "1": [["q0", ["1", "1"]]]
                },
                "": {
                    Z: [["q2", ["Z"]]],
                    "0": [["q1", ["0"]]],
                    "1": [["q1", ["1"]]]
                }
            },
            q1: {
                "0": {
                    "0": [["q1", []]]
                },
                "1": {
                    "1": [["q1", []]]
                },
                "": {
                    Z: [["q2", ["Z"]]]
                }
            }
        },
        initial_state: "q0",
        initial_stack_symbol: "Z",
        final_states: ["q2"]
    },
    tm: {
        states: ["q0", "q1", "q2", "q3", "qf"],
        input_symbols: ["0", "1"],
        tape_symbols: ["0", "1", "X", "Y", "*"],
        transitions: {
            q0: {
                "0": ["q1", "X", "R"],
                "1": ["q2", "Y", "R"],
                "*": ["q3", "*", "R"]
            },
            q1: {
                "0": ["q1", "0", "R"],
                "1": ["q1", "1", "R"],
                "*": ["q2", "*", "L"]
            },
            q2: {
                "0": ["q2", "0", "L"],
                "1": ["q2", "1", "L"],
                "X": ["q0", "X", "R"],
                "Y": ["q0", "Y", "R"]
            },
            q3: {
                "X": ["q3", "X", "R"],
                "Y": ["q3", "Y", "R"],
                "*": ["qf", "*", "R"]
            }
        },
        initial_state: "q0",
        blank_symbol: "*",
        final_states: ["qf"]
    }
};

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentType = tab.dataset.type;
        document.getElementById('automatonInput').value = JSON.stringify(sampleConfigs[currentType], null, 2);
        resetUI();
    });
});

document.getElementById('automatonInput').value = JSON.stringify(sampleConfigs.dfa, null, 2);

document.getElementById('createBtn').addEventListener('click', async (event) => {
    event.preventDefault();

    try {
        const config = JSON.parse(document.getElementById('automatonInput').value);

        const response = await fetch(`${API_BASE_URL}/${currentType}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const data = await response.json();
        if (data.id) {
            currentAutomatonId = data.id;
            showResult('Automato criado com sucesso!', true);
            loadAutomatonImage();
        }
    } catch (error) {
        showResult("Falha ao criar automato!", false);
    }
});

document.getElementById('verifyBtn').addEventListener('click', async () => {
    if (!currentAutomatonId) {
        showResult('Por favor, crie um automato primeiro!', false);
        return;
    }

    const word = document.getElementById('wordInput').value;

    try {
        const response = await fetch(`${API_BASE_URL}/${currentType}/${currentAutomatonId}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word })
        });

        const data = await response.json();
        console.log(data);



        showResult(`A palavra "${word}" ${data.accepted ? 'é aceita' : 'não é aceita'}!`, data.accepted);
    } catch (error) {
        showResult(error.message, false);
    }
});

async function loadAutomatonImage() {
    try {
        const url = `${API_BASE_URL}/${currentType}/${currentAutomatonId}/save-image`;
        console.log(url);

        const response = await fetch(url);
        const data = await response.json();
        if (data.image_base64) {
            const img = document.getElementById('automatonImage');
            img.src = `data:image/png;base64,${data.image_base64}`;
            img.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading automaton image:', error);
    }
}

function showResult(message, success) {
    const result = document.getElementById('result');
    result.textContent = message;
    result.className = `result ${success ? 'success' : 'error'}`;
    result.style.display = 'block';
}

function resetUI() {
    currentAutomatonId = null;
    document.getElementById('result').style.display = 'none';
    document.getElementById('automatonImage').style.display = 'none';
    document.getElementById('wordInput').value = '';
}