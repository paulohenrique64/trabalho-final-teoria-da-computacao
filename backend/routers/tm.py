import base64
from io import BytesIO
import os
from typing import Any, Dict, List, Tuple
import uuid
from fastapi import APIRouter, HTTPException
from automata.tm.dtm import DTM
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
tm_list_cache = {}

class TmCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    tape_symbols: List[str]
    transitions: Dict[str, Dict[str, Tuple[str, str, str]]]
    initial_state: str
    blank_symbol: str
    final_states: List[str]

class WordRequest(BaseModel):
    word: str

@router.get("/{tm_id}", summary="Obter uma TM")
async def return_selected_tm(tm_id: str):
    tm = tm_list_cache.get(tm_id)

    if tm is None:  # Changed from 'if not tm'
        raise HTTPException(status_code=404, detail="selected tm not found")
    
    return {
        "states": list(tm.states),
        "input_symbols": list(tm.input_symbols),
        "tape_symbols": list(tm.tape_symbols),
        "transitions": tm.transitions,
        "initial_state": tm.initial_state,
        "blank_symbol": tm.blank_symbol,
        "final_states": list(tm.final_states)
    }

@router.put("/{tm_id}", summary="Atualizar uma TM")
async def update_tm(tm_id: str, request: TmCreateRequest):
    tm = tm_list_cache.get(tm_id)

    if tm is None: 
        raise HTTPException(status_code=404, detail="o tm selecionado nao foi encontrado")

    try:
        tm = DTM(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            tape_symbols=set(request.tape_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            blank_symbol=request.blank_symbol,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    tm_list_cache[tm_id] = tm

    return {"maquina de turing " + tm_id + " atualizada com sucesso"}
    
@router.post("/", summary="Criar uma TM")
async def create_tm(request: TmCreateRequest):
    tm_id = str(uuid.uuid4())

    try:
        tm = DTM(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            tape_symbols=set(request.tape_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            blank_symbol=request.blank_symbol,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    tm_list_cache[tm_id] = tm

    return {"id": tm_id}

@router.post("/{tm_id}/verify", summary="Verificar aceitação de uma palavra")
async def verify_acceptance(tm_id: str, request: WordRequest):
    tm = tm_list_cache.get(tm_id)

    if tm is None:  
        raise HTTPException(status_code=404, detail="selected tm not found")
    
    try:
        accepted = tm.accepts_input(request.word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{tm_id}/save-image", summary="Gerar imagem da TM")
async def save_tm_image(tm_id: str):
    tm = tm_list_cache.get(tm_id)

    if tm is None:
        raise HTTPException(status_code=404, detail="selected tm not found")
    
    try:
        # criar diretório 'images' se não existir
        if not os.path.exists('images/tm'):
           os.makedirs('images/tm')
        
        # nome do arquivo baseado no ID do tm
        filename = f"images/tm/tm_{tm_id}.png"

        dot = Digraph()
        dot.attr(rankdir='LR')
        
        # Add states
        for state in tm.states:
            if state in tm.final_states:
                dot.node(state, state, shape='doublecircle')
            else:
                dot.node(state, state, shape='circle')
        
        # Add transitions
        for from_state, transitions in tm.transitions.items():
            for symbol, (to_state, write_symbol, direction) in transitions.items():
                label = f"{symbol}/{write_symbol},{direction}"
                dot.edge(from_state, to_state, label=label)
        
        # Mark initial state
        dot.node('', '', shape='none')
        dot.edge('', tm.initial_state)
        
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