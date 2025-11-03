from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from shared.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # You can store the generated schema, analysis, etc., here as JSON
    schema_details = Column(JSON)
    analysis_results = Column(JSON)

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    filename: Mapped[str] = mapped_column()
    filepath: Mapped[str] = mapped_column(nullable=True) # Filepath is null until uploaded
    filesize: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="PENDING") # <-- ADD THIS LINE
    
# class UploadedFile(Base):
#     __tablename__ = "uploaded_files"
    
#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(Integer, index=True) # Foreign key to the session
#     filename = Column(String, index=True)
#     filepath = Column(String)
#     filesize = Column(Integer)
    
class ExtractedRecord(Base):
    __tablename__ = "extracted_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True) # Foreign key to the session
    # The JSON type is perfect for storing flexible, extracted data
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            **self.data
        }