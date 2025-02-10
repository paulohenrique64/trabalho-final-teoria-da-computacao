from io import BytesIO
from typing import Any, Dict, List, Tuple
from fastapi import APIRouter, HTTPException
from automata.tm.dtm import DTM
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
tm_list_cache = {}
id_counter = 0

class tmCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    tape_symbols: List[str]
    transitions: Dict[str, Dict[str, Tuple[str, str, str]]]
    initial_state: str
    blank_symbol: str
    final_states: List[str]

@router.get("/{tm_id}")
async def return_selected_tm(tm_id: int):
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
    
@router.post("/")
async def create_tm(request: tmCreateRequest):
    global id_counter
    tm_id = id_counter
    id_counter = id_counter + 1

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

@router.post("/{tm_id}/verify")
async def verify_acceptance(tm_id: int, word: str):
    tm = tm_list_cache.get(tm_id)

    if tm is None:  
        raise HTTPException(status_code=404, detail="selected tm not found")
    
    try:
        accepted = tm.accepts_input(word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{tm_id}/image")
async def visualize_afd(tm_id: int):
    tm = tm_list_cache.get(tm_id)

    if tm is None:
        raise HTTPException(status_code=404, detail="selected tm not found")
    
    try:
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
        
        # Render to PNG
        buf = BytesIO()
        buf.write(dot.pipe(format='png'))
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))