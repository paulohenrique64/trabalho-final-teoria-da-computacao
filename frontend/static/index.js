let currentType = 'dfa';
        let currentAutomatonId = null;

        const API_BASE_URL = 'http://localhost:8000';

        const sampleConfigs = {
            dfa: {
                states: ['q0', 'q1'],
                input_symbols: ['0', '1'],
                transitions: {
                    'q0': {'0': 'q0', '1': 'q1'},
                    'q1': {'0': 'q1', '1': 'q0'}
                },
                initial_state: 'q0',
                final_states: ['q0']
            },
            pda: {
                states: ['q0', 'q1', 'q2'],
                input_symbols: ['0', '1'],
                stack_symbols: ['0', '1', 'Z'],
                transitions: {
                    'q0': {
                        '0': {
                            'Z': [['q0', ['0', 'Z']]]
                        }
                    }
                },
                initial_state: 'q0',
                initial_stack_symbol: 'Z',
                final_states: ['q2']
            },
            tm: {
                states: ['q0', 'q1', 'q2'],
                input_symbols: ['0', '1'],
                tape_symbols: ['0', '1', 'B'],
                transitions: {
                    'q0': {'0': ['q1', '1', 'R']},
                    'q1': {'1': ['q2', '0', 'L']}
                },
                initial_state: 'q0',
                blank_symbol: 'B',
                final_states: ['q2']
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
                    headers: {'Content-Type': 'application/json'},
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
                    headers: {'Content-Type': 'application/json'},
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