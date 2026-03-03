import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..controllers.contact_controller import identify_contact
from ..schemas import IdentifyRequest, IdentifyResponse

logger = logging.getLogger("app.identify")
router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
def identify(body: IdentifyRequest, db: Session = Depends(get_db)):
    logger.info("identify call, body=%s", body.json())
    if not body.email and not body.phoneNumber:
        raise HTTPException(status_code=400, detail="email or phoneNumber required")

    try:
        result = identify_contact(db, body.email, body.phoneNumber)
    except Exception:
        logger.exception("identify_contact failed")
        raise
    logger.info("identify result: %s", result)
    return IdentifyResponse(contact=result)

