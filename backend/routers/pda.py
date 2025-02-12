import base64
from io import BytesIO
import os
from typing import Any, Dict, List
import uuid
from fastapi import APIRouter, HTTPException
from automata.pda.npda import NPDA
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
pda_list_cache = {}

class PdaCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    stack_symbols: List[str]
    transitions: Dict[str, Dict[str, Dict[str, List[List[Any]]]]]
    initial_state: str
    initial_stack_symbol: str
    final_states: List[str]

class WordRequest(BaseModel):
    word: str

@router.get("/{pda_id}", summary="Obter um PDA")
async def return_selected_pda(pda_id: str):
    pda = pda_list_cache.get(pda_id)

    if pda is None:  # Changed from 'if not pda'
        raise HTTPException(status_code=404, detail="selected pda not found")
    
    return {
        "states": pda.states,
        "input_symbols": pda.input_symbols,
        "transitions": pda.transitions,
        "initial_state": pda.initial_state,
        "final_states": pda.final_states,
    }

@router.put("/{pda_id}", summary="Atualizar um PDA")
async def update_pda(pda_id: str, request: PdaCreateRequest):
    pda = pda_list_cache.get(pda_id)

    if pda is None: 
        raise HTTPException(status_code=404, detail="o pda selecionado nao foi encontrado")

    try:
        pda = NPDA(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            stack_symbols=set(request.stack_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            initial_stack_symbol=request.initial_stack_symbol,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    pda_list_cache[pda_id] = pda

    return {"automato com pilha " + pda_id + " atualizado com sucesso"}
    
@router.post("/", summary="Criar um PDA")
async def create_pda(request: PdaCreateRequest):
    pda_id = str(uuid.uuid4())

    try:
        pda = NPDA(
            states=set(request.states),
            input_symbols=set(request.input_symbols),
            stack_symbols=set(request.stack_symbols),
            transitions=request.transitions,
            initial_state=request.initial_state,
            initial_stack_symbol=request.initial_stack_symbol,
            final_states=set(request.final_states)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    pda_list_cache[pda_id] = pda

    return {"id": pda_id}

@router.post("/{pda_id}/verify", summary="Verificar aceitação de palavra")
async def verify_acceptance(pda_id: str, request: WordRequest):
    pda = pda_list_cache.get(pda_id)

    if pda is None:  
        raise HTTPException(status_code=404, detail="selected pda not found")
    
    try:
        accepted = pda.accepts_input(request.word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{pda_id}/save-image", summary="Gerar imagem do PDA")
async def save_pda_image(pda_id: str):
    pda = pda_list_cache.get(pda_id)

    if pda is None:
        raise HTTPException(status_code=404, detail="selected pda not found")
    
    try:
        # criar diretório 'images' se não existir
        if not os.path.exists('images/pda'):
           os.makedirs('images/pda')
        
        # nome do arquivo baseado no ID do pda
        filename = f"images/pda/pda_{pda_id}.png"

        dot = Digraph()
        dot.attr(rankdir='LR')
        
        # add states
        for state in pda.states:
            if state in pda.final_states:
                dot.node(state, state, shape='doublecircle')
            else:
                dot.node(state, state, shape='circle')
        
        # add transitions
        for from_state, input_dict in pda.transitions.items():
            for input_symbol, stack_dict in input_dict.items():
                for stack_top, transitions in stack_dict.items():
                    for transition in transitions:
                        to_state, stack_push = transition
                        label = f"{input_symbol},{stack_top}/{stack_push}"
                        dot.edge(from_state, to_state, label=label)
        
        # mark initial state
        dot.node('', '', shape='none')
        dot.edge('', pda.initial_state)
        
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