# 🇮🇹 Italian Tech Ecosystem Graph - Todo List

## ✅ COMPLETATO: Ecosistema C14.so
- 346 Startup importate ✅
- 195 Person nodes (con deduplicazione nome+cognome) ✅
- 79 Investors importati ✅
- 517 Founding relationships importate ✅
- 138 Investment relationships importate senza errori ✅

**Precedenti errori risolti:**
- Row 42, 74, 97: Failed to create INVESTS_IN ✅ **RISOLTO** (problemi tipo investitore B4I e Azimut Libera Impresa)

## ✅ COMPLETATO: Italian Founders Fund
- 14 Startup estratte ✅
- 29 Founders estratti ✅
- 29 Founding relationships ✅
- 14 Investment relationships (IFF come investitore) ✅
- 1 Nuovo investitore aggiunto (Italian Founders Fund) ✅
- **File CSV pronti per import Neo4j**

## ✅ COMPLETATO: Primo Capital
- 49 Startup estratte ✅
- 49 Investment relationships (Primo Capital come investitore) ✅
- 1 Nuovo investitore aggiunto (Primo Capital) ✅
- **Settori principali**: Space & Aerospace (9), HealthTech (8), FinTech (5), Enterprise Software (5)
- **File CSV pronti per import Neo4j**

## ✅ COMPLETATO: Prana Ventures
- 13 Startup estratte ✅
- 13 Investment relationships (Prana Ventures come investitore) ✅
- 1 Nuovo investitore aggiunto (Prana Ventures) ✅
- **Focus**: Operational VC, Seed & Post-Seed, ticket €250K-€750K
- **Settori principali**: Enterprise Software (3), Consumer Tech (2), Retail & E-commerce (2)
- **Business model**: SaaS dominante (10/13 companies)
- **File CSV pronti per import Neo4j**

## ✅ COMPLETATO: CDP Venture Capital
- 150 Startup estratte (investimenti diretti) ✅
- 41 VC Funds estratti (fondi supportati come LP) ✅
- 150 Investment relationships (CDP -> Startups) ✅
- 41 Fund relationships (CDP come LP nei fondi) ✅
- 1 Nuovo investitore aggiunto (CDP Venture Capital) ✅
- **Ruolo**: Government VC (Cassa Depositi e Prestiti)
- **Focus**: Ecosistema innovazione italiano, Direct investments + Fund of Funds
- **Settori principali**: Technology (74), HealthTech (32), InfraTech & Mobility (14), IndustryTech (13)
- **Veicoli**: VenturItaly Fund of Funds, Digital Transition NRRP Fund, Green Transition NRRP Fund, International Fund of Funds
- **File CSV pronti per import Neo4j**

## 🎯 NEXT STEPS

### 🔧 Miglioramenti Sistema
- [ ] **Aggiornare funzioni di check duplicati** - Le funzioni attuali nella UI non sono aggiornate e potrebbero non funzionare correttamente
- [ ] **Migliorare performance query analytics** - Ottimizzare le query Neo4j per grandi dataset
- [ ] **Aggiungere caching** - Implementare cache per query frequenti
- [ ] **Installare streamlit-agraph** - Per visualizzazioni grafiche avanzate

### 📊 Importazione Dati Aggiuntivi
Importare dati di altri player importanti dell'ecosistema italiano:

- [ ] **IAG (Italian Angels for Growth)** - Principale network di angel investor italiani
- [ ] **IBAN (Italian Business Angel Network)** - Network angel investor  
- [ ] **Club degli Investitori** - Community di investitori privati
- [ ] **B4I (Bocconi for Innovation)** - Hub di innovazione Bocconi
- [ ] **Berkeley SkyDeck** - Acceleratore con presenza italiana
- [ ] **Vento Venture Building** - Venture builder italiano
- [ ] **Nana Bianca** - Acceleratore/incubatore
- [ ] **Plug and Play**
- [x] **Italian Founders Fund** ✅ **COMPLETATO** - 14 startup, 29 founder, 14 investment relationships estratte

### 🕷️ Nuovi Scraper da Sviluppare
- [x] **Italian Founders Fund Scraper** ✅ **COMPLETATO** - Portfolio scraper funzionante
- [ ] **Scraper per siti degli acceleratori/incubatori** - Estrarre portfolio companies
- [ ] **Scraper per network di angel investor** - Estrarre membri e investimenti
- [ ] **Scraper LinkedIn** - Estrarre network e connessioni (rispettando ToS)
- [ ] **Integrazione Crunchbase** - API a pagamento per dati internazionali

### 🌐 Espansione Funzionalità
- [ ] **Export formato standard** - JSON-LD, GraphML per interoperabilità
- [ ] **API REST** - Endpoint per accesso programmatico ai dati
- [ ] **Dashboard avanzati** - Metriche KPI specifiche per VC/startup
- [ ] **Alert system** - Notifiche per nuovi round, acquisizioni, etc.
- [ ] **Graph visualization** - Visualizzazione interattiva del network

### 🔍 Analytics da Implementare
- [ ] **Analisi sentiment** - Sentiment analysis su news e comunicati
- [ ] **Trend analysis** - Analisi trend settoriali e temporali
- [ ] **Network centrality** - Identificare nodi più influenti
- [ ] **Prediction models** - Modelli predittivi per successo startup

---

## 📈 Stato Attuale Database
- **Startup**: 346
- **Persone**: 511
- **Investitori**: 79
- **Relazioni Founding**: 517
- **Relazioni Investment**: 138
- **Coverage**: Principalmente C14.so (startup italiane emergenti)


- fare un frontend react decente