from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Interest(Base):
    """
    Interest model representing predefined interest categories.
    
    This table contains all available interests that users can select.
    Interests are organized by category (e.g., Sports, Music, Technology).
    
    Attributes:
        id: Primary key
        category: Main category (e.g., "Sports", "Music", "Gaming", "Arts")
        name: Specific interest name (e.g., "Football", "Rock Music", "PUBG")
        description: Optional description of the interest
        icon: Optional icon/emoji representation
    
    Example data:
        - category: "Sports", name: "Football"
        - category: "Sports", name: "Basketball"
        - category: "Music", name: "Rock"
        - category: "Gaming", name: "PUBG"
        - category: "Technology", name: "AI/ML"
    """
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=True)  # Emoji or icon identifier
    
    # Ensure no duplicate interests
    __table_args__ = (
        UniqueConstraint('category', 'name', name='unique_category_name'),
    )
    
    # Relationships
    # Users who have selected this interest
    users = relationship(
        "UserInterest", 
        back_populates="interest",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Interest(id={self.id}, category='{self.category}', name='{self.name}')>"