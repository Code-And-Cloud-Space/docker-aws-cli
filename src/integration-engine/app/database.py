from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

from . import config

Base = declarative_base()

class SalesforceOAuthToken(Base):
    __tablename__ = "salesforce_oauth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=True, index=True)
    salesforce_user_id = Column(String(100), nullable=True, index=True)
    salesforce_org_id = Column(String(100), nullable=True, index=True)
    salesforce_username = Column(String(255), nullable=True)
    instance_url = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token_secret_arn = Column(String(255), nullable=False)
    token_type = Column(String(50), default="Bearer")
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_refreshed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SalesforceAccount(Base):
    __tablename__ = "salesforce_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salesforce_id = Column(String(18), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    annual_revenue = Column(Text, nullable=True)
    billing_street = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(50), nullable=True)
    billing_country = Column(String(100), nullable=True)
    raw_payload = Column(Text, nullable=True)
    sync_status = Column(String(50), default="SYNCED", index=True)
    salesforce_created_date = Column(DateTime, nullable=True)
    salesforce_last_modified_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    contacts = relationship("SalesforceContact", back_populates="account")
    opportunities = relationship("SalesforceOpportunity", back_populates="account")

class SalesforceContact(Base):
    __tablename__ = "salesforce_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salesforce_id = Column(String(18), unique=True, nullable=False, index=True)
    account_salesforce_id = Column(String(18), nullable=True, index=True)
    account_id = Column(Integer, ForeignKey("salesforce_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    mobile_phone = Column(String(50), nullable=True)
    title = Column(String(150), nullable=True)
    department = Column(String(100), nullable=True)
    raw_payload = Column(Text, nullable=True)
    sync_status = Column(String(50), default="SYNCED", index=True)
    salesforce_created_date = Column(DateTime, nullable=True)
    salesforce_last_modified_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    account = relationship("SalesforceAccount", back_populates="contacts")

class SalesforceOpportunity(Base):
    __tablename__ = "salesforce_opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salesforce_id = Column(String(18), unique=True, nullable=False, index=True)
    account_salesforce_id = Column(String(18), nullable=True, index=True)
    account_id = Column(Integer, ForeignKey("salesforce_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    stage_name = Column(String(100), nullable=False, index=True)
    amount = Column(Text, nullable=True)
    probability = Column(Text, nullable=True)
    close_date = Column(DateTime, nullable=True)
    type = Column(String(100), nullable=True)
    lead_source = Column(String(100), nullable=True)
    raw_payload = Column(Text, nullable=True)
    sync_status = Column(String(50), default="SYNCED", index=True)
    salesforce_created_date = Column(DateTime, nullable=True)
    salesforce_last_modified_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    account = relationship("SalesforceAccount", back_populates="opportunities")
 
class SalesforceCustomMapping(Base):
    __tablename__ = "salesforce_custom_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    sobject = Column(String(100), nullable=False, index=True)
    selected_fields = Column(Text, nullable=False) # JSON array: ["Id", "Name", "BillingCity"]
    field_mappings = Column(Text, nullable=False) # JSON map: {"Id": "Record_ID", "Name": "Company"}
    filter_clause = Column(Text, nullable=True) # e.g. "AnnualRevenue > 100000"
    sort_field = Column(String(100), nullable=True)
    sort_order = Column(String(10), default="DESC")
    record_limit = Column(Integer, default=50)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# Database Engine & Session
engine = create_engine(
    config.DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import text

def init_db():
    """Initializes tables for Salesforce OAuth tokens, Accounts, Contacts, and Opportunities and applies column migrations"""
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            # Migration 1: Ensure session_id column exists on salesforce_oauth_tokens
            res = conn.execute(text("SHOW COLUMNS FROM salesforce_oauth_tokens LIKE 'session_id'"))
            if not res.fetchone():
                print("[MySQL Migration] Adding session_id column to salesforce_oauth_tokens...")
                conn.execute(text("ALTER TABLE salesforce_oauth_tokens ADD COLUMN session_id VARCHAR(100) NULL AFTER id, ADD INDEX idx_session_id(session_id)"))
                conn.commit()

            # Migration 2: Drop legacy user_id column and foreign keys if present
            res = conn.execute(text("SHOW COLUMNS FROM salesforce_oauth_tokens LIKE 'user_id'"))
            if res.fetchone():
                print("[MySQL Migration] Cleaning up legacy user_id column from salesforce_oauth_tokens...")
                try:
                    conn.execute(text("ALTER TABLE salesforce_oauth_tokens DROP FOREIGN KEY salesforce_oauth_tokens_ibfk_1"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE salesforce_oauth_tokens DROP INDEX idx_user_active"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE salesforce_oauth_tokens DROP COLUMN user_id"))
                except Exception:
                    pass
                conn.commit()
    except Exception as e:
        print(f"[MySQL] Notice during DB initialization: {e}")
