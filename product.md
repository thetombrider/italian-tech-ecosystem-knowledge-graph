# Knowledge Graph - Ecosistema Tech Italiano

## Schema del Grafo

### Entità Principali

#### 1. **Person** (Persona)
**Descrizione**: Individui chiave nell'ecosistema tech italiano

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome completo
- `surname`: Cognome
- `role_type`: Tipo di ruolo primario (founder, gp, lp, angel_investor, executive, advisor, other)
- `linkedin_url`: Profilo LinkedIn
- `twitter_handle`: Handle Twitter/X
- `biography`: Biografia breve
- `location`: Città/Regione
- `birth_year`: Anno di nascita (opzionale)
- `education`: Background educativo
- `previous_experience`: Esperienze lavorative precedenti
- `specialization`: Settori di specializzazione/interesse
- `reputation_score`: Score di reputazione nell'ecosistema (1-100)
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

#### 2. **Startup** 
**Descrizione**: Startup e scale-up dell'ecosistema italiano

**Attributi**:
- `id`: Identificatore univoco  
- `name`: Nome della startup
- `description`: Descrizione dell'attività
- `website`: Sito web
- `founded_year`: Anno di fondazione
- `stage`: Fase di sviluppo (pre_seed, seed, series_a, series_b, series_c, growth, exit)
- `sector`: Settore principale (fintech, healthtech, edtech, etc.)
- `business_model`: Modello di business (b2b, b2c, marketplace, saas, etc.)
- `headquarters`: Sede principale
- `employee_count`: Numero dipendenti
- `status`: Stato attuale (active, acquired, closed, ipo)
- `total_funding`: Totale finanziamenti ricevuti (€)
- `last_funding_date`: Data ultimo round
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

#### 3. **VC_Firm** (Società di Venture Capital)
**Descrizione**: Società che gestiscono fondi di venture capital

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome della firm
- `description`: Descrizione della società
- `website`: Sito web
- `founded_year`: Anno di fondazione
- `headquarters`: Sede principale
- `type`: Tipo (independent, corporate_vc, government, family_office)
- `investment_focus`: Focus settoriale
- `stage_focus`: Focus su stage (early_stage, growth, multi_stage)
- `geographic_focus`: Focus geografico
- `team_size`: Dimensione del team
- `assets_under_management`: Asset gestiti totali (€)
- `portfolio_companies_count`: Numero aziende in portfolio
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

#### 4. **VC_Fund** (Fondo di Venture Capital)
**Descrizione**: Singoli fondi gestiti dalle VC firm

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome del fondo
- `fund_size`: Dimensione del fondo (€)
- `vintage_year`: Anno di vintage
- `fund_number`: Numero del fondo (es. Fund I, Fund II)
- `status`: Stato (fundraising, investing, harvesting, closed)
- `target_sectors`: Settori target
- `target_stages`: Stage target
- `geographic_focus`: Focus geografico
- `first_close_date`: Data primo closing
- `final_close_date`: Data closing finale
- `investment_period`: Periodo di investimento (anni)
- `fund_life`: Durata del fondo (anni)
- `deployed_capital`: Capitale già investito (€)
- `created_at`: Data di creazione del record
- `updated_at`: Date ultimo aggiornamento

#### 5. **Other_Investors** (Altri Investitori)
**Descrizione**: Angel syndicate, family office e altri tipi di investitori

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome del syndicate/gruppo
- `type`: Tipo (angel_syndicate, family_office, crowdfunding_platform, other)
- `description`: Descrizione
- `website`: Sito web
- `founded_year`: Anno di fondazione
- `headquarters`: Sede principale
- `members_count`: Numero membri (per syndicate)
- `investment_focus`: Focus settoriale
- `stage_focus`: Focus su stage
- `ticket_size_min`: Ticket minimo (€)
- `ticket_size_max`: Ticket massimo (€)
- `total_investments`: Totale investimenti effettuati
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

#### 6. **Other_Institutions** (Altri Attori)
**Descrizione**: Incubatori, acceleratori, venture builder

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome dell'istituzione
- `type`: Tipo (incubator, accelerator, venture_builder, university, research_center)
- `description`: Descrizione dell'attività
- `website`: Sito web
- `founded_year`: Anno di fondazione
- `headquarters`: Sede principale
- `program_duration`: Durata programma (per acceleratori/incubatori)
- `batch_size`: Dimensione batch (startup per batch)
- `sectors_focus`: Settori di focus
- `equity_taken`: % equity media presa
- `funding_provided`: Finanziamento medio fornito (€)
- `portfolio_companies_count`: Numero aziende supportate
- `success_rate`: Tasso di successo
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

#### 7. **Corporate** 
**Descrizione**: Aziende corporate, incluse parent di CVC

**Attributi**:
- `id`: Identificatore univoco
- `name`: Nome dell'azienda
- `description`: Descrizione dell'attività
- `website`: Sito web
- `founded_year`: Anno di fondazione
- `headquarters`: Sede principale
- `sector`: Settore principale
- `size`: Dimensione (startup, sme, large_enterprise, multinational)
- `revenue`: Fatturato annuale (€)
- `employee_count`: Numero dipendenti
- `stock_exchange`: Borsa di quotazione (se quotata)
- `ticker`: Ticker azionario
- `has_cvc_arm`: Ha braccio di Corporate VC
- `innovation_programs`: Ha programmi di innovazione
- `created_at`: Data di creazione del record
- `updated_at`: Data ultimo aggiornamento

---

### Relazioni

#### 1. **FOUNDED** (Person → Startup)
**Descrizione**: Persona ha fondato una startup

**Attributi**:
- `role`: Ruolo nella fondazione (ceo, cto, co_founder)
- `founding_date`: Data di fondazione
- `equity_percentage`: Percentuale di equity (se nota)
- `is_current`: Se è ancora attivo nella startup
- `exit_date`: Data di uscita (se applicabile)

#### 2. **WORKS_AT** (Person → VC_Firm | Institution | Corporate)
**Descrizione**: Persona lavora presso un'organizzazione

**Attributi**:
- `role`: Ruolo (partner, principal, associate, analyst, etc.)
- `start_date`: Data inizio
- `end_date`: Data fine (se non più attivo)
- `seniority_level`: Livello di seniority (junior, senior, partner, managing_partner)
- `is_current`: Se è ancora attivo

#### 3. **ANGEL_INVESTS_IN** (Person → Startup)
**Descrizione**: Persona investe come angel in una startup

**Attributi**:
- `investment_date`: Data dell'investimento
- `round_stage`: Stage del round (pre_seed, seed, etc.)
- `amount`: Importo investito (€)
- `lead_investor`: Se è lead investor
- `board_seat`: Se ha un posto nel CdA

#### 4. **MANAGES** (VC_Firm → VC_Fund)
**Descrizione**: VC Firm gestisce un fondo

**Attributi**:
- `management_fee`: Fee di gestione (%)
- `carried_interest`: Carried interest (%)
- `start_date`: Data inizio gestione

#### 5. **INVESTS_IN** (VC_Fund | Angel_Syndicate | Corporate → Startup)
**Descrizione**: Fondo/investitore investe in una startup

**Attributi**:
- `round_stage`: Stage del round
- `round_date`: Data del round
- `amount`: Importo investito (€)
- `valuation_pre`: Valutazione pre-money (€)
- `valuation_post`: Valutazione post-money (€)
- `is_lead_investor`: Se è lead investor del round
- `board_seats`: Numero posti CdA ottenuti
- `equity_percentage`: Percentuale equity ottenuta

#### 6. **PARTICIPATED_IN** (Person → VC_Fund)
**Descrizione**: Persona partecipa come LP in un fondo

**Attributi**:
- `commitment_amount`: Importo committed (€)
- `commitment_date`: Data del commitment
- `investor_type`: Tipo di investitore (institutional, hnwi, family_office, etc.)

#### 7. **ACCELERATED_BY** (Startup → Institution)
**Descrizione**: Startup partecipa a programma di accelerazione/incubazione

**Attributi**:
- `program_name`: Nome del programma
- `batch_name`: Nome del batch
- `start_date`: Data inizio programma
- `end_date`: Data fine programma
- `equity_taken`: % equity presa
- `funding_received`: Finanziamento ricevuto (€)
- `demo_day_date`: Data demo day

#### 8. **ACQUIRED** (Corporate → Startup)
**Descrizione**: Corporate acquisisce una startup

**Attributi**:
- `acquisition_date`: Data acquisizione
- `acquisition_value`: Valore acquisizione (€)
- `acquisition_type`: Tipo (full_acquisition, majority_stake, minority_stake)
- `strategic_rationale`: Razionale strategico
- `integration_status`: Stato integrazione

#### 9. **PARTNERS_WITH** (Corporate → VC_Firm | Institution)
**Descrizione**: Partnership strategica tra corporate e altri attori

**Attributi**:
- `partnership_type`: Tipo (strategic, commercial, investment, program)
- `start_date`: Data inizio partnership
- `description`: Descrizione della partnership
- `is_active`: Se la partnership è ancora attiva

#### 10. **MENTORS** (Person → Person)
**Descrizione**: Relazione di mentorship

**Attributi**:
- `start_date`: Data inizio mentorship
- `end_date`: Data fine (se applicabile)
- `relationship_type`: Tipo (formal_mentor, advisor, informal)
- `context`: Contesto della relazione

#### 11. **SPUN_OFF_FROM** (Startup → Corporate | Institution)
**Descrizione**: Startup è spin-off di un'organizzazione

**Attributi**:
- `spinoff_date`: Data dello spin-off
- `technology_transferred`: Tecnologia trasferita
- `initial_equity`: Equity iniziale mantenuta dalla parent
- `support_provided`: Supporto fornito dalla parent

---

### Relazioni Derivate (Query Pattern)

Le seguenti relazioni possono essere derivate dalle relazioni principali tramite query:

#### **FUNDED_BY** (Startup ← VC_Fund | Angel_Syndicate | Corporate | Person)
**Descrizione**: Startup riceve finanziamento (vista invertita di INVESTS_IN e ANGEL_INVESTS_IN)

**Query Cypher di esempio**:
```cypher
// Tutti i finanziamenti ricevuti da una startup
MATCH (investor)-[r:INVESTS_IN|ANGEL_INVESTS_IN]->(startup:Startup {name: "StartupXYZ"})
RETURN investor, r, startup

// Finanziamenti per round stage
MATCH (investor)-[r:INVESTS_IN]->(startup:Startup)
WHERE r.round_stage = "series_a"
RETURN startup.name, investor.name, r.amount, r.round_date
```

#### **PORTFOLIO_OF** (Startup ← VC_Fund | Angel_Syndicate | Person)
**Descrizione**: Startup nel portfolio di un investitore

**Query Cypher di esempio**:
```cypher
// Portfolio di un fondo
MATCH (fund:VC_Fund {name: "Fund ABC I"})-[r:INVESTS_IN]->(startup:Startup)
RETURN startup, r.round_stage, r.amount, r.round_date
ORDER BY r.round_date DESC
```

---

### Proprietà del Grafo

#### Indici Consigliati
- Person: `name`, `role_type`, `location`
- Startup: `name`, `sector`, `stage`, `founded_year`
- VC_Firm: `name`, `type`, `headquarters`
- VC_Fund: `vintage_year`, `fund_size`

#### Vincoli di Integrità

##### Vincoli di Base
- Ogni entità deve avere un `id` univoco
- Ogni entità deve avere un `name` non vuoto
- Gli importi monetari devono essere >= 0
- Le percentuali devono essere tra 0 e 100
- Le email devono avere formato valido
- Le URL devono avere formato valido

##### Vincoli di Cardinalità
- **1 VC_Firm : N VC_Fund**: Un VC Firm può gestire più fondi, ma ogni fondo appartiene a un solo VC Firm
- **1 Startup : N Founders**: Una startup può avere più fondatori, ma ogni relazione FOUNDED è unica per persona-startup
- **N Startup : M Investors**: Relazioni many-to-many per investimenti (INVESTS_IN, ANGEL_INVESTS_IN)
- **1 Person : N Employment**: Una persona può lavorare per più organizzazioni nel tempo, ma non simultaneamente nella stessa organizzazione

##### Vincoli Temporali
- **Coerenza Date Fondazione**: 
  - `FOUNDED.founding_date` >= `Startup.founded_year` (anno)
  - `FOUNDED.founding_date` <= data corrente
- **Coerenza Date Investimento**:
  - `INVESTS_IN.round_date` >= `Startup.founded_year` (anno)
  - `ANGEL_INVESTS_IN.investment_date` >= `Startup.founded_year` (anno)
  - Date di investimento <= data corrente
- **Coerenza Date Employment**:
  - `WORKS_AT.start_date` <= `WORKS_AT.end_date` (se end_date presente)
  - `WORKS_AT.end_date` <= data corrente
- **Coerenza Date VC Fund**:
  - `VC_Fund.vintage_year` >= `VC_Firm.founded_year`
  - `VC_Fund.first_close_date` <= `VC_Fund.final_close_date` (se entrambe presenti)
- **Coerenza Date Accelerazione**:
  - `ACCELERATED_BY.start_date` <= `ACCELERATED_BY.end_date` (se end_date presente)
  - `ACCELERATED_BY.start_date` >= `Startup.founded_year` (anno)
- **Coerenza Date Acquisizione**:
  - `ACQUIRED.acquisition_date` >= `Startup.founded_year` (anno)
  - `ACQUIRED.acquisition_date` <= data corrente

##### Vincoli di Business Logic
- **Equity Constraints**:
  - Somma di tutte le equity percentuali di una startup non può superare 100%
  - `FOUNDED.equity_percentage` + tutti gli `INVESTS_IN.equity_percentage` <= 100%
- **Investment Stage Progression**:
  - Gli stage di investimento devono essere logicamente coerenti nel tempo
  - pre_seed < seed < series_a < series_b < series_c < growth
- **Funding Coherence**:
  - `Startup.total_funding` dovrebbe essere >= somma di tutti gli investimenti ricevuti
  - `Startup.last_funding_date` dovrebbe corrispondere al round più recente
- **VC Fund Constraints**:
  - `VC_Fund.deployed_capital` <= `VC_Fund.fund_size`
  - `VC_Fund.fund_life` tipicamente tra 7-12 anni
  - `VC_Fund.investment_period` tipicamente tra 3-5 anni
- **Employment Constraints**:
  - Una persona non può essere `is_current=true` in più organizzazioni dello stesso tipo contemporaneamente
  - Se `WORKS_AT.is_current=true` allora `end_date` deve essere null
- **LP Participation Constraints**:
  - `PARTICIPATED_IN.commitment_amount` > 0
  - `PARTICIPATED_IN.commitment_date` >= `VC_Fund.vintage_year` (anno)

##### Vincoli di Status
- **Startup Status Logic**:
  - Se `status = 'acquired'` deve esistere relazione `ACQUIRED`
  - Se `status = 'closed'` deve avere `exit_date`
  - Se `status = 'ipo'` deve avere `exit_date` e `exit_value`
- **VC Fund Status Logic**:
  - Se `status = 'closed'` deve avere `final_close_date`
  - Se `status = 'investing'` deve avere `first_close_date`
- **Current Relationship Logic**:
  - Se `FOUNDED.is_current = false` deve avere `exit_date`
  - Se `WORKS_AT.is_current = false` deve avere `end_date`

##### Vincoli di Unicità
- **Nome Univoco per Tipo**: Nomi di entità devono essere univoci all'interno dello stesso tipo
- **Relazioni Uniche**: Alcune relazioni devono essere uniche per coppia di entità:
  - `MANAGES`: Un VC_Firm può gestire un VC_Fund solo una volta
  - `ACQUIRED`: Un Corporate può acquisire una Startup solo una volta
- **Email/LinkedIn Univoci**: Email e profili LinkedIn devono essere univoci tra le persone

#### Metriche Derivate
- **Network Centrality**: Per identificare i nodi più influenti
- **Investment Velocity**: Frequenza di investimenti per investor
- **Success Rate**: Tasso di successo per investor/accelerator
- **Portfolio Overlap**: Sovrapposizione di portfolio tra investor
- **Geographic Clustering**: Concentrazione geografica dell'ecosistema

---

### Casi d'Uso del Grafo

1. **Deal Flow Analysis**: Identificare pattern negli investimenti
2. **Network Analysis**: Mappare le connessioni chiave dell'ecosistema  
3. **Talent Mapping**: Tracciare il movimento di talenti tra organizzazioni
4. **Market Intelligence**: Analizzare trend settoriali e geografici
5. **Due Diligence**: Background check su persone e organizzazioni
6. **Partnership Discovery**: Identificare potenziali partner strategici
7. **Investment Opportunities**: Scoprire startup emergenti tramite network
8. **Ecosystem Health**: Monitorare la salute dell'ecosistema italiano

---

### Implementazione Vincoli nell'Applicazione

#### Validation Layer (Pydantic Models)
```python
# Esempio di validazioni a livello di modello
class Founding(BaseModel):
    founding_date: date
    startup_founded_year: int  # Per validazione
    
    @validator('founding_date')
    def validate_founding_date(cls, v, values):
        if 'startup_founded_year' in values:
            if v.year < values['startup_founded_year']:
                raise ValueError('Founding date cannot be earlier than startup foundation year')
        if v > date.today():
            raise ValueError('Founding date cannot be in the future')
        return v
```

#### Database Constraints (Neo4j)
```cypher
// Constraint per nomi univoci
CREATE CONSTRAINT unique_startup_name FOR (s:Startup) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT unique_person_email FOR (p:Person) REQUIRE p.email IS UNIQUE;

// Constraint per proprietà obbligatorie
CREATE CONSTRAINT startup_name_exists FOR (s:Startup) REQUIRE s.name IS NOT NULL;
CREATE CONSTRAINT person_name_exists FOR (p:Person) REQUIRE p.name IS NOT NULL;
```

#### Business Logic Validation
```python
# Esempio di validazione business logic
def validate_equity_distribution(startup_name: str, repo: Neo4jRepository):
    """Valida che la distribuzione di equity non superi 100%"""
    total_equity = repo.get_total_equity_for_startup(startup_name)
    if total_equity > 100:
        raise ValidationError(f"Total equity distribution ({total_equity}%) exceeds 100%")

def validate_investment_stage_progression(startup_name: str, new_stage: str, repo: Neo4jRepository):
    """Valida che gli stage di investimento siano progressivi"""
    stage_order = ['pre_seed', 'seed', 'series_a', 'series_b', 'series_c', 'growth']
    last_round = repo.get_latest_funding_round(startup_name)
    
    if last_round and stage_order.index(new_stage) < stage_order.index(last_round['stage']):
        raise ValidationError(f"Cannot add {new_stage} round after {last_round['stage']}")
```

#### Form Validation (Streamlit)
```python
# Esempio di validazione real-time nei form
def validate_investment_form(investor_data, startup_data, investment_data):
    errors = []
    
    # Validazione date
    if investment_data['round_date'].year < startup_data['founded_year']:
        errors.append("Investment date cannot be earlier than startup foundation")
    
    # Validazione importi
    if investment_data['amount'] <= 0:
        errors.append("Investment amount must be positive")
    
    # Validazione equity
    if investment_data.get('equity_percentage', 0) > 50:
        errors.append("Single investment cannot exceed 50% equity")
    
    return errors
```

---

### Note di Implementazione

#### Tecnologie Suggerite
- **Database**: Neo4j per il knowledge graph
- **API Layer**: GraphQL per query flessibili  
- **Data Ingestion**: Pipeline ETL per acquisire dati da fonti multiple
- **Visualization**: Gephi, D3.js o Cytoscape per visualizzazioni

#### Fonti Dati
- Crunchbase, PitchBook per dati startup/VC
- LinkedIn per dati professionali
- Registro Imprese per dati corporate
- Siti web e comunicati stampa per validation
- Survey dirette per completare informazioni mancanti