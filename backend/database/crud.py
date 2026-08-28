from sqlalchemy.orm import Session

from backend.database.models import (
    Conversation,
    Document,
    Message,
)


# -------------------------
# Document operations
# -------------------------

def create_document(
    db: Session,
    document_id: str,
    filename: str,
    source: str,
    page_count: int,
    file_size: int,
    title: str | None,
    author: str | None,
    creation_date: str | None,
) -> Document:

    document = Document(
        document_id=document_id,
        filename=filename,
        source=source,
        page_count=page_count,
        file_size=file_size,
        title=title,
        author=author,
        creation_date=creation_date,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_documents(
    db: Session,
) -> list[Document]:

    return db.query(
        Document
    ).all()


def get_document_by_document_id(
    db: Session,
    document_id: str,
) -> Document | None:

    return (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )


# -------------------------
# Conversation operations
# -------------------------

def create_conversation(
    db: Session,
    document_id: int,
) -> Conversation:

    conversation = Conversation(
        document_id=document_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    conversation_id: int,
) -> Conversation | None:

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )


# -------------------------
# Message operations
# -------------------------

def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:

    if role not in {"user", "assistant"}:
        raise ValueError(
            "Message role must be "
            "'user' or 'assistant'."
        )

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    limit: int = 10,
) -> list[Message]:

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id
        )
        .order_by(
            Message.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    # Messages were fetched newest first.
    # Reverse them so the LLM receives
    # the conversation in chronological order.
    return list(
        reversed(messages)
    )