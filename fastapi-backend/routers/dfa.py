from io import BytesIO
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from automata.fa.dfa import DFA
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from graphviz import Digraph

router = APIRouter()
dfa_list_cache = {}
id_counter = 0

class DfaCreateRequest(BaseModel):
    states: List[str]
    input_symbols: List[str]
    transitions: Dict[str, Dict[str, str]]
    initial_state: str
    final_states: List[str]

@router.get("/{afd_id}")
async def return_selected_dfa(afd_id: int):
    dfa = dfa_list_cache.get(afd_id)

    if dfa is None:  # Changed from 'if not dfa'
        raise HTTPException(status_code=404, detail="selected dfa not found")
    
    return {
        "states": dfa.states,
        "input_symbols": dfa.input_symbols,
        "transitions": dfa.transitions,
        "initial_state": dfa.initial_state,
        "final_states": dfa.final_states,
    }
    
@router.post("/")
async def create_dfa(request: DfaCreateRequest):
    global id_counter
    dfa_id = id_counter
    id_counter = id_counter + 1

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

@router.post("/{dfa_id}/verify")
async def verify_acceptance(dfa_id: int, word: str):
    dfa = dfa_list_cache.get(dfa_id)

    if dfa is None:  
        raise HTTPException(status_code=404, detail="selected dfa not found")
    
    try:
        accepted = dfa.accepts_input(word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"accepted": accepted}

@router.get("/{dfa_id}/image")
async def visualize_afd(dfa_id: int):
    dfa = dfa_list_cache.get(dfa_id)

    if dfa is None:
        raise HTTPException(status_code=404, detail="selected dfa not found")
    
    try:
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
        
        # render to PNG
        buf = BytesIO()
        buf.write(dot.pipe(format='png'))
        buf.seek(0)
        
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))