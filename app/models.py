from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import date
from enum import Enum

# Enums for better type safety
class PersonRoleType(str, Enum):
    FOUNDER = "founder"
    GP = "gp"
    LP = "lp"
    ANGEL_INVESTOR = "angel_investor"
    EXECUTIVE = "executive"
    ADVISOR = "advisor"
    OTHER = "other"

class StartupStage(str, Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    EXIT = "exit"

class StartupStatus(str, Enum):
    ACTIVE = "active"
    ACQUIRED = "acquired"
    CLOSED = "closed"
    IPO = "ipo"

class VCFirmType(str, Enum):
    INDEPENDENT = "independent"
    CORPORATE_VC = "corporate_vc"
    GOVERNMENT = "government"
    FAMILY_OFFICE = "family_office"

class InstitutionType(str, Enum):
    INCUBATOR = "incubator"
    ACCELERATOR = "accelerator"
    VENTURE_BUILDER = "venture_builder"
    UNIVERSITY = "university"
    RESEARCH_CENTER = "research_center"

# Entity Models
class Person(BaseModel):
    name: str = Field(..., description="Nome completo")
    surname: Optional[str] = Field(None, description="Cognome")
    role_type: PersonRoleType = Field(..., description="Tipo di ruolo primario")
    linkedin_url: Optional[HttpUrl] = Field(None, description="Profilo LinkedIn")
    twitter_handle: Optional[str] = Field(None, description="Handle Twitter/X")
    biography: Optional[str] = Field(None, description="Biografia breve")
    location: Optional[str] = Field(None, description="Città/Regione")
    birth_year: Optional[int] = Field(None, description="Anno di nascita", ge=1900, le=2010)
    education: Optional[str] = Field(None, description="Background educativo")
    previous_experience: Optional[str] = Field(None, description="Esperienze precedenti")
    specialization: Optional[str] = Field(None, description="Settori di specializzazione")
    reputation_score: Optional[int] = Field(None, description="Score reputazione", ge=1, le=100)

class Startup(BaseModel):
    name: str = Field(..., description="Nome della startup")
    description: Optional[str] = Field(None, description="Descrizione dell'attività")
    website: Optional[HttpUrl] = Field(None, description="Sito web")
    founded_year: Optional[int] = Field(None, description="Anno di fondazione", ge=1990, le=2025)
    stage: Optional[StartupStage] = Field(None, description="Fase di sviluppo")
    sector: Optional[str] = Field(None, description="Settore principale")
    business_model: Optional[str] = Field(None, description="Modello di business")
    headquarters: Optional[str] = Field(None, description="Sede principale")
    employee_count: Optional[int] = Field(None, description="Numero dipendenti", ge=0)
    status: StartupStatus = Field(StartupStatus.ACTIVE, description="Stato attuale")
    total_funding: Optional[float] = Field(None, description="Totale finanziamenti (€)", ge=0)
    last_funding_date: Optional[date] = Field(None, description="Data ultimo round")
    exit_date: Optional[date] = Field(None, description="Data di exit")
    exit_value: Optional[float] = Field(None, description="Valore di exit (€)", ge=0)

class VCFirm(BaseModel):
    name: str = Field(..., description="Nome della firm")
    description: Optional[str] = Field(None, description="Descrizione della società")
    website: Optional[HttpUrl] = Field(None, description="Sito web")
    founded_year: Optional[int] = Field(None, description="Anno di fondazione", ge=1900, le=2025)
    headquarters: Optional[str] = Field(None, description="Sede principale")
    type: VCFirmType = Field(..., description="Tipo di firm")
    investment_focus: Optional[str] = Field(None, description="Focus settoriale")
    stage_focus: Optional[str] = Field(None, description="Focus su stage")
    geographic_focus: Optional[str] = Field(None, description="Focus geografico")
    team_size: Optional[int] = Field(None, description="Dimensione team", ge=1)
    assets_under_management: Optional[float] = Field(None, description="AUM (€)", ge=0)
    portfolio_companies_count: Optional[int] = Field(None, description="Numero aziende portfolio", ge=0)

class VCFund(BaseModel):
    name: str = Field(..., description="Nome del fondo")
    fund_size: Optional[float] = Field(None, description="Dimensione fondo (€)", ge=0)
    vintage_year: Optional[int] = Field(None, description="Anno di vintage", ge=2000, le=2030)
    fund_number: Optional[str] = Field(None, description="Numero del fondo")
    status: Optional[str] = Field(None, description="Stato del fondo")
    target_sectors: Optional[str] = Field(None, description="Settori target")
    target_stages: Optional[str] = Field(None, description="Stage target")
    geographic_focus: Optional[str] = Field(None, description="Focus geografico")
    first_close_date: Optional[date] = Field(None, description="Data primo closing")
    final_close_date: Optional[date] = Field(None, description="Data closing finale")
    investment_period: Optional[int] = Field(None, description="Periodo investimento (anni)", ge=1, le=10)
    fund_life: Optional[int] = Field(None, description="Durata fondo (anni)", ge=5, le=15)
    deployed_capital: Optional[float] = Field(None, description="Capitale investito (€)", ge=0)

class AngelSyndicate(BaseModel):
    name: str = Field(..., description="Nome del syndicate")
    type: Literal["angel_syndicate", "family_office", "crowdfunding_platform", "other"] = Field(..., description="Tipo")
    description: Optional[str] = Field(None, description="Descrizione")
    website: Optional[HttpUrl] = Field(None, description="Sito web")
    founded_year: Optional[int] = Field(None, description="Anno di fondazione", ge=1990, le=2025)
    headquarters: Optional[str] = Field(None, description="Sede principale")
    members_count: Optional[int] = Field(None, description="Numero membri", ge=1)
    investment_focus: Optional[str] = Field(None, description="Focus settoriale")
    stage_focus: Optional[str] = Field(None, description="Focus su stage")
    ticket_size_min: Optional[float] = Field(None, description="Ticket minimo (€)", ge=0)
    ticket_size_max: Optional[float] = Field(None, description="Ticket massimo (€)", ge=0)
    total_investments: Optional[int] = Field(None, description="Totale investimenti", ge=0)

class Institution(BaseModel):
    name: str = Field(..., description="Nome dell'istituzione")
    type: InstitutionType = Field(..., description="Tipo di istituzione")
    description: Optional[str] = Field(None, description="Descrizione attività")
    website: Optional[HttpUrl] = Field(None, description="Sito web")
    founded_year: Optional[int] = Field(None, description="Anno di fondazione", ge=1900, le=2025)
    headquarters: Optional[str] = Field(None, description="Sede principale")
    program_duration: Optional[int] = Field(None, description="Durata programma (mesi)", ge=1, le=24)
    batch_size: Optional[int] = Field(None, description="Dimensione batch", ge=1)
    sectors_focus: Optional[str] = Field(None, description="Settori di focus")
    equity_taken: Optional[float] = Field(None, description="% equity media", ge=0, le=100)
    funding_provided: Optional[float] = Field(None, description="Finanziamento medio (€)", ge=0)
    portfolio_companies_count: Optional[int] = Field(None, description="Aziende supportate", ge=0)
    success_rate: Optional[float] = Field(None, description="Tasso di successo (%)", ge=0, le=100)

class Corporate(BaseModel):
    name: str = Field(..., description="Nome dell'azienda")
    description: Optional[str] = Field(None, description="Descrizione attività")
    website: Optional[HttpUrl] = Field(None, description="Sito web")
    founded_year: Optional[int] = Field(None, description="Anno di fondazione", ge=1800, le=2025)
    headquarters: Optional[str] = Field(None, description="Sede principale")
    sector: Optional[str] = Field(None, description="Settore principale")
    size: Optional[Literal["startup", "sme", "large_enterprise", "multinational"]] = Field(None, description="Dimensione")
    revenue: Optional[float] = Field(None, description="Fatturato annuale (€)", ge=0)
    employee_count: Optional[int] = Field(None, description="Numero dipendenti", ge=1)
    stock_exchange: Optional[str] = Field(None, description="Borsa di quotazione")
    ticker: Optional[str] = Field(None, description="Ticker azionario")
    has_cvc_arm: bool = Field(False, description="Ha braccio CVC")
    innovation_programs: bool = Field(False, description="Ha programmi innovazione")

# Relationship Models
class Investment(BaseModel):
    round_stage: StartupStage = Field(..., description="Stage del round")
    round_date: date = Field(..., description="Data del round")
    amount: float = Field(..., description="Importo investito (€)", ge=0)
    valuation_pre: Optional[float] = Field(None, description="Valutazione pre-money (€)", ge=0)
    valuation_post: Optional[float] = Field(None, description="Valutazione post-money (€)", ge=0)
    is_lead_investor: bool = Field(False, description="È lead investor")
    board_seats: Optional[int] = Field(None, description="Posti CdA ottenuti", ge=0)
    equity_percentage: Optional[float] = Field(None, description="% equity ottenuta", ge=0, le=100)

class AngelInvestment(BaseModel):
    investment_date: date = Field(..., description="Data investimento")
    round_stage: StartupStage = Field(..., description="Stage del round")
    amount: float = Field(..., description="Importo investito (€)", ge=0)
    lead_investor: bool = Field(False, description="È lead investor")
    board_seat: bool = Field(False, description="Ha posto in CdA")

class Employment(BaseModel):
    role: str = Field(..., description="Ruolo")
    start_date: date = Field(..., description="Data inizio")
    end_date: Optional[date] = Field(None, description="Data fine")
    seniority_level: Optional[str] = Field(None, description="Livello seniority")
    is_current: bool = Field(True, description="È ancora attivo")

class FundManagement(BaseModel):
    management_fee: Optional[float] = Field(None, description="Fee di gestione (%)", ge=0, le=10)
    carried_interest: Optional[float] = Field(None, description="Carried interest (%)", ge=0, le=50)
    start_date: date = Field(..., description="Data inizio gestione")

class Founding(BaseModel):
    role: str = Field(..., description="Ruolo nella fondazione (CEO, CTO, Co-founder)")
    founding_date: date = Field(..., description="Data di fondazione")
    equity_percentage: Optional[float] = Field(None, description="% equity iniziale", ge=0, le=100)
    is_current: bool = Field(True, description="È ancora attivo nella startup")
    exit_date: Optional[date] = Field(None, description="Data di uscita dalla startup")

class LPParticipation(BaseModel):
    commitment_amount: float = Field(..., description="Importo committed (€)", gt=0)
    commitment_date: date = Field(..., description="Data del commitment")
    investor_type: str = Field(..., description="Tipo di investitore (institutional, hnwi, family_office, etc.)")

class Acceleration(BaseModel):
    program_name: str = Field(..., description="Nome del programma")
    batch_name: Optional[str] = Field(None, description="Nome del batch")
    start_date: date = Field(..., description="Data inizio programma")
    end_date: Optional[date] = Field(None, description="Data fine programma")
    equity_taken: Optional[float] = Field(None, description="% equity presa", ge=0, le=100)
    funding_received: Optional[float] = Field(None, description="Finanziamento ricevuto (€)", ge=0)
    demo_day_date: Optional[date] = Field(None, description="Data demo day")

class Acquisition(BaseModel):
    acquisition_date: date = Field(..., description="Data acquisizione")
    acquisition_value: Optional[float] = Field(None, description="Valore acquisizione (€)", gt=0)
    acquisition_type: str = Field(..., description="Tipo (full_acquisition, majority_stake, minority_stake)")
    strategic_rationale: Optional[str] = Field(None, description="Razionale strategico")
    integration_status: Optional[str] = Field(None, description="Stato integrazione")

class Partnership(BaseModel):
    partnership_type: str = Field(..., description="Tipo (strategic, commercial, investment, program)")
    start_date: date = Field(..., description="Data inizio partnership")
    description: Optional[str] = Field(None, description="Descrizione della partnership")
    is_active: bool = Field(True, description="Partnership ancora attiva")

class Mentorship(BaseModel):
    start_date: date = Field(..., description="Data inizio mentorship")
    end_date: Optional[date] = Field(None, description="Data fine (se applicabile)")
    relationship_type: str = Field(..., description="Tipo (formal_mentor, advisor, informal)")
    context: Optional[str] = Field(None, description="Contesto della relazione")

class SpinOff(BaseModel):
    spinoff_date: date = Field(..., description="Data dello spin-off")
    technology_transferred: Optional[str] = Field(None, description="Tecnologia trasferita")
    initial_equity: Optional[float] = Field(None, description="Equity iniziale mantenuta dalla parent", ge=0, le=100)
    support_provided: Optional[str] = Field(None, description="Supporto fornito dalla parent")