from io import BytesIO
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from automata.pda.npda import NPDA
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
pda_list_cache = {}
id_counter = 0

class PdaCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    stack_symbols: List[str]
    transitions: Dict[str, Dict[str, Dict[str, List[List[Any]]]]]
    initial_state: str
    initial_stack_symbol: str
    final_states: List[str]

@router.get("/{pda_id}")
async def return_selected_pda(pda_id: int):
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
    
@router.post("/")
async def create_pda(request: PdaCreateRequest):
    global id_counter
    pda_id = id_counter
    id_counter = id_counter + 1

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

@router.post("/{pda_id}/verify")
async def verify_acceptance(pda_id: int, word: str):
    pda = pda_list_cache.get(pda_id)

    if pda is None:  
        raise HTTPException(status_code=404, detail="selected pda not found")
    
    try:
        accepted = pda.accepts_input(word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{pda_id}/image")
async def visualize_afd(pda_id: int):
    pda = pda_list_cache.get(pda_id)

    if pda is None:
        raise HTTPException(status_code=404, detail="selected pda not found")
    
    try:
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
        
        # render to PNG
        buf = BytesIO()
        buf.write(dot.pipe(format='png'))
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))