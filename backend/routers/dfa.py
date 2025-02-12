import base64
from io import BytesIO
import os
from typing import Dict, List
import uuid
from fastapi import APIRouter, HTTPException
from automata.fa.dfa import DFA
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
dfa_list_cache = {}

class DfaCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    transitions: Dict[str, Dict[str, str]]
    initial_state: str
    final_states: List[str]

class WordRequest(BaseModel):
    word: str

@router.get("/{dfa_id}", summary="Obter um DFA")
async def return_selected_dfa(dfa_id: str):
    dfa = dfa_list_cache.get(dfa_id)

    if dfa is None:  
        raise HTTPException(status_code=404, detail="o dfa selecionado nao foi encontrado")
    
    return {
        "states": dfa.states,
        "input_symbols": dfa.input_symbols,
        "transitions": dfa.transitions,
        "initial_state": dfa.initial_state,
        "final_states": dfa.final_states,
    }

@router.put("/{dfa_id}", summary="Atualizar um DFA")
async def update_dfa(dfa_id: str, request: DfaCreateRequest):
    dfa = dfa_list_cache.get(dfa_id)

    if dfa is None: 
        raise HTTPException(status_code=404, detail="o dfa selecionado nao foi encontrado")

    try:
        dfa = DFA(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    dfa_list_cache[dfa_id] = dfa

    return {"automato finito deterministico " + dfa_id + " atualizado com sucesso"}
    
@router.post("/", summary="Criar um novo DFA")
async def create_dfa(request: DfaCreateRequest):
    dfa_id = str(uuid.uuid4())

    try:
        dfa = DFA(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    dfa_list_cache[dfa_id] = dfa

    return {"id": dfa_id}

@router.post("/{dfa_id}/verify", summary="Verificar aceitação de palavra")
async def verify_acceptance(dfa_id: str, request: WordRequest):
    dfa = dfa_list_cache.get(dfa_id)

    print(request.word)

    if dfa is None:  
        raise HTTPException(status_code=404, detail="o dfa selecionado nao foi encontrado")
    
    try:
        accepted = dfa.accepts_input(request.word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{dfa_id}/save-image", summary="Gerar imagem do DFA")
async def save_dfa_image(dfa_id: str):
    dfa = dfa_list_cache.get(dfa_id)

    if dfa is None:
        raise HTTPException(status_code=404, detail="o dfa selecionado nao foi encontrado")
    
    try:
        # criar diretório 'images' se não existir
        if not os.path.exists('images/dfa'):
           os.makedirs('images/dfa')
        
        # nome do arquivo baseado no ID do dfa
        filename = f"images/dfa/dfa_{dfa_id}.png"

        dot = Digraph()
        dot.attr(rankdir='LR')
        
        # add states
        for state in dfa.states:
            if state in dfa.final_states:
                dot.node(state, state, shape='doublecircle')
            else:
                dot.node(state, state, shape='circle')
        
        # add transitions
        for from_state, transitions in dfa.transitions.items():
            for symbol, to_state in transitions.items():
                dot.edge(from_state, to_state, label=symbol)
        
        # mark initial state
        dot.node('', '', shape='none')
        dot.edge('', dfa.initial_state)
        
        # salvar a imagem no arquivo
        dot.render(filename.replace('.png', ''), format='png', cleanup=True)

        # ler o arquivo e converter para base64
        with open(filename, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "imagem salva com sucesso",
                "image_base64": encoded_string
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))