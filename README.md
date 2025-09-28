# Italian Tech Ecosystem Graph

Un sistema di data entry basato su Streamlit per popolare un knowledge graph Neo4j dell'ecosistema tech italiano.

## 🚀 Quick Start

### 1. Installare le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configurare Neo4j

1. Assicurati che Neo4j sia in esecuzione (Desktop o Server)
2. Copia `.env.example` in `.env`:
   ```bash
   cp .env.example .env
   ```
3. Modifica `.env` con le tue credenziali Neo4j

### 3. Avviare l'app

```bash
streamlit run streamlit_app.py
```

## 📊 Funzionalità

### ✅ Entità Supportate
- **👥 Person**: Founder, GP, LP, angel investor, ecc.
- **🚀 Startup**: Startup e scale-up italiane
- **🏢 VC Firm**: Società di venture capital
- **💰 VC Fund**: Singoli fondi delle VC firm
- **👼 Angel Syndicate**: Angel syndicate e family office
- **🏛️ Institution**: Incubatori, acceleratori, venture builder
- **🏭 Corporate**: Aziende corporate e parent di CVC

### ✅ Relazioni Supportate
- **INVESTS_IN**: Fondo → Startup
- **ANGEL_INVESTS_IN**: Persona → Startup  
- **WORKS_AT**: Persona → Organizzazione
- **MANAGES**: VC Firm → VC Fund

## 🎯 Interfaccia

### 📊 Dashboard
- Statistiche database
- Overview entità e relazioni

### ➕ Add Entity
- Form guidati per ogni tipo di entità
- Validazione automatica dei dati
- Campi obbligatori e opzionali

### 🔗 Add Relationship  
- Selezione dinamica da entità esistenti
- Form specifici per ogni tipo di relazione
- Validazione date e importi

### 🔍 Search & Browse
- Ricerca full-text nelle entità
- Browse di tutte le entità per tipo
- Risultati in formato tabellare

## 🏗️ Architettura

```
streamlit_app.py          # App principale Streamlit
app/
├── models.py             # Modelli Pydantic per validazione
└── neo4j_repo.py         # Repository per operazioni Neo4j
requirements.txt          # Dipendenze Python
.env.example             # Template configurazione
```

## 🔧 Configurazione

### Environment Variables (.env)
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
APP_TITLE=Italian Tech Ecosystem Graph
```

## 📝 Schema del Grafo

Il knowledge graph implementa lo schema definito in `ontology.md`:

- **7 tipi di entità** con attributi ricchi
- **11 tipi di relazioni** con proprietà specifiche
- **Relazioni derivate** ottenibili tramite query

## 🎨 Features Principali

### ⚡ Velocità
- UI immediata con Streamlit
- Form pre-validati con Pydantic
- Connessione persistente a Neo4j

### 🛡️ Validazione
- Type hints e enums per campi critici
- Validazione automatica date e importi
- Controllo integrità referenziale

### 🔄 Usabilità
- Selezione dinamica da entità esistenti
- Auto-complete per relazioni
- Feedback immediato su successo/errore

### 📈 Scalabilità
- Architettura modulare
- Repository pattern per DB operations
- Facile estensione con nuove entità

## 🎯 Prossimi Passi

1. **🔧 Setup**: Configura l'ambiente e testa la connessione
2. **📊 Populate**: Inizia ad aggiungere entità e relazioni
3. **🔍 Explore**: Usa il browser Neo4j per visualizzare il grafo
4. **📈 Analyze**: Esegui query per estrarre insights

## 🛠️ Troubleshooting

### Connection Issues
- Verifica che Neo4j sia in esecuzione
- Controlla le credenziali in `.env`
- Testa la connessione dal Neo4j Browser

### Import Errors
- Assicurati di aver installato tutte le dipendenze
- Usa un virtual environment Python
- Verifica la versione Python (>=3.8)

### Performance
- Per dataset grandi, considera l'uso di batch insert
- Ottimizza le query con indici appropriati
- Monitora l'uso memoria Neo4j

## 📚 Risorse

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Schema completo](ontology.md)

---

**Happy Graph Building!** 🎉
