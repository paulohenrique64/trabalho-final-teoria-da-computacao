from fastapi import FastAPI
from routers import dfa, acp, tm
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
   
def get_application() -> FastAPI:
    application = FastAPI(title="trabalho pratico teoria da computacao", version="0.0.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(dfa.router, prefix="/dfa", tags=["deterministic finite automata"])
    application.include_router(acp.router, prefix="/acp", tags=["acp"])
    application.include_router(tm.router, prefix="/tm", tags=["turing machine"])    

    return application

app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
