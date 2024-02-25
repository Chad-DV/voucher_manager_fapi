from fastapi import FastAPI, HTTPException
from models import DefaultVoucher,generate_unique_code
from database.database import Voucher,RedemptionDate
from voucher import VoucherRepository,RedemptionDateRepository
from datetime import datetime


app = FastAPI()

@app.post("/voucher/")
def create_voucher(voucher: DefaultVoucher):
    voucher.code = generate_unique_code()
    created_voucher = VoucherRepository.store(pydantic_to_sqlalchemy(voucher))
    return created_voucher

@app.post("/voucher/infinite/")
def create_infinite_voucher():
    new_voucher = DefaultVoucher()
    new_voucher.is_infinite = True
    new_voucher.valid_to = datetime(year=9999, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    created_voucher = VoucherRepository.store(pydantic_to_sqlalchemy(new_voucher))
    return {"message": "Infinite voucher created successfully", "voucher": created_voucher}

@app.post("/voucher/{max_redemtions}/{valid_to}")
def create_x_redeemable_voucher(voucher: DefaultVoucher,max_redemptions:int,valid_to:datetime):
    voucher.code = generate_unique_code()
    voucher.max_redemptions = max_redemptions
    voucher.valid_to = valid_to

    created_voucher = VoucherRepository.store(pydantic_to_sqlalchemy(voucher))
    return created_voucher

@app.get("/voucher/{code}")
def get_voucher(code: str):
    voucher = VoucherRepository.get_one(code)
    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

@app.get("/voucher/")
def get_all_vouchers():
    vouchers = VoucherRepository.get_all()
    return vouchers

@app.delete("/voucher/{code}")
def delete_voucher(code: str):
    deleted = VoucherRepository.delete(code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return {"message": "Voucher deleted successfully"}

@app.put("/voucher/{code}/redeem")
def redeem_voucher(code: str):
    voucher = VoucherRepository.get_one(code)
    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")

    # Check if voucher is expired
    current_datetime = datetime.now()
    if not voucher.is_infinite:
        if voucher.valid_to is not None and current_datetime > voucher.valid_to:
            raise HTTPException(status_code=400, detail="Voucher has expired")

        if voucher.valid_from is not None and current_datetime < voucher.valid_from:
            raise HTTPException(status_code=400, detail="Voucher is not yet valid")

    redemption_date = RedemptionDate(voucher_code=code, redeemed_at=current_datetime)

    if not voucher.is_infinite and voucher.max_redemptions <= 0:
        raise HTTPException(status_code=400, detail="Voucher max redemptions reached")
    elif not voucher.is_infinite:
        voucher.max_redemptions -= 1

    voucher.redeemed_at = current_datetime


    VoucherRepository.update(voucher)
    RedemptionDateRepository.create(redemption_date)

    return {"message": "Voucher redeemed successfully"}

#--- helper functions---#
def pydantic_to_sqlalchemy(pydantic_instance: DefaultVoucher) -> Voucher:
    return Voucher(
        code=pydantic_instance.code,
        max_redemptions=pydantic_instance.max_redemptions,
        valid_from=pydantic_instance.valid_from,
        valid_to=pydantic_instance.valid_to,
        is_infinite=pydantic_instance.is_infinite
    )

if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)