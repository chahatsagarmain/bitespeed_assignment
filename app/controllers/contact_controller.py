from sqlalchemy.orm import Session
from ..models.contact import Contact


def identify_contact(db: Session, email: str | None, phone: str | None):
    """Core logic for identifying or creating/contact merging.  Returns a
    dict matching the ContactResponse schema.

    so the way it works is:
    
    1. first check for email or phone 
    2. if none is found the we dont have a primary , we create a new primary and return 
    3. if one has primary then we create the respected resonse and return it 
    4. if both have primary then we merge the primary to the oldest one 
    """
    query = db.query(Contact).filter(
        (Contact.email == email) | (Contact.phoneNumber == phone)
    )
    existing = query.order_by(Contact.createdAt).all()

    if not existing:
        new = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence="primary",
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        return {
            "primaryContactId": new.id,
            "emails": [new.email] if new.email else [],
            "phoneNumbers": [new.phoneNumber] if new.phoneNumber else [],
            "secondaryContactIds": [],
        }

    primaries = [c for c in existing if c.linkPrecedence == "primary"]
    if primaries:
        primary = min(primaries, key=lambda x: x.createdAt)
        demoted_ids = []
        for other in primaries:
            if other.id != primary.id:
                other.linkPrecedence = "secondary"
                other.linkedId = primary.id
                demoted_ids.append(other.id)
                db.add(other)
        db.commit()
        if demoted_ids:
            affected = db.query(Contact).filter(Contact.linkedId.in_(demoted_ids)).all()
            for a in affected:
                a.linkedId = primary.id
                a.linkPrecedence = "secondary"
                db.add(a)
            db.commit()
            for a in affected:
                db.refresh(a)
        for c in primaries:
            db.refresh(c)
    else:
        primary = min(existing, key=lambda x: x.createdAt)

    all_contacts = {primary.id: primary}
    for c in existing:
        if c.id != primary.id:
            all_contacts[c.id] = c

    seen_email = any(c.email == email for c in all_contacts.values() if c.email)
    seen_phone = any(c.phoneNumber == phone for c in all_contacts.values() if c.phoneNumber)

    if (email and not seen_email) or (phone and not seen_phone):
        new = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence="secondary",
            linkedId=primary.id,
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        all_contacts[new.id] = new

    emails = []
    phone_numbers = []
    secondary_ids = []

    if primary.email:
        emails.append(primary.email)
    if primary.phoneNumber:
        phone_numbers.append(primary.phoneNumber)

    for cid, c in all_contacts.items():
        if c.id == primary.id:
            continue
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phone_numbers:
            phone_numbers.append(c.phoneNumber)
        if c.linkPrecedence == "secondary":
            secondary_ids.append(c.id)

    return {
        "primaryContactId": primary.id,
        "emails": emails,
        "phoneNumbers": phone_numbers,
        "secondaryContactIds": secondary_ids,
    }
