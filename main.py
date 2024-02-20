from fastapi import FastAPI
from controllers import voucher_manager as manager
from controllers import voucher_redeemer as redeemer

app = FastAPI()

# Include routes from controller modules
app.include_router(manager.router)
app.include_router(redeemer.router)