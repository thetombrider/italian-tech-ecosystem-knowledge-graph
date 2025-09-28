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

#### 6. **PARTICIPATED_IN** (Person | Institution | VC_Firm → VC_Fund)
**Descrizione**: Investitore partecipa come LP (Limited Partner) in un fondo

**Attributi**:
- `commitment_amount`: Importo committed (€)
- `commitment_date`: Data del commitment
- `investor_type`: Categoria LP (institutional, hnwi, family_office, corporate, government, pension_fund, sovereign_fund, etc.)

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
- Ogni entità deve avere un `id` univoco
- Le date devono essere validate (no date future per eventi passati)
- Gli importi monetari devono essere >= 0
- Le percentuali devono essere tra 0 e 100

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