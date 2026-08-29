from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from backend.database.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    filename = Column(
        String,
        nullable=False,
    )

    source = Column(
        String,
        nullable=False,
    )

    page_count = Column(
        Integer,
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    title = Column(
        String,
        nullable=True,
    )

    author = Column(
        String,
        nullable=True,
    )

    creation_date = Column(
        String,
        nullable=True,
    )

    upload_time = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    conversations = relationship(
        "Conversation",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    document = relationship(
        "Document",
        back_populates="conversations",
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    # Retrieved RAG sources associated
    # with this assistant response.
    sources = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )