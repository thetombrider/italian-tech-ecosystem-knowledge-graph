import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any
import os

# Graph visualization imports
# from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx

# Import our custom modules
from app.models import *
from app.neo4j_repo import Neo4jConnection, Neo4jRepository
from app.csv_importer import CSVImporter

# Page configuration
st.set_page_config(
    page_title="Italian Tech Ecosystem Graph",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'neo4j_connected' not in st.session_state:
    st.session_state.neo4j_connected = False
if 'repo' not in st.session_state:
    st.session_state.repo = None

@st.cache_resource
def init_neo4j_connection():
    """Initialize Neo4j connection"""
    conn = Neo4jConnection()
    if conn.connect():
        return Neo4jRepository(conn)
    return None

def main():
    st.title("🇮🇹 Italian Tech Ecosystem Graph")
    st.markdown("### Data Entry & Management System")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Connection status
    if not st.session_state.neo4j_connected:
        st.sidebar.warning("⚠️ Not connected to Neo4j")
        if st.sidebar.button("Connect to Neo4j"):
            repo = init_neo4j_connection()
            if repo:
                st.session_state.repo = repo
                st.session_state.neo4j_connected = True
                st.sidebar.success("✅ Connected to Neo4j")
                st.rerun()
            else:
                st.sidebar.error("❌ Failed to connect to Neo4j")
    else:
        st.sidebar.success("✅ Connected to Neo4j")
    
    if not st.session_state.neo4j_connected:
        st.error("Please connect to Neo4j first using the sidebar.")
        st.markdown("""
        ### Setup Instructions:
        1. Make sure Neo4j is running
        2. Copy `.env.example` to `.env` and set your credentials
        3. Click 'Connect to Neo4j' in the sidebar
        """)
        return
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Dashboard", "📈 Analytics", "➕ Add Entity", "🔗 Add Relationship", "🔍 Search & Browse", "🌐 Graph Visualization", "📤 CSV Import", "🕷️ C14 Scraper"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "➕ Add Entity":
        show_add_entity()
    elif page == "🔗 Add Relationship":
        show_add_relationship()
    elif page == "🔍 Search & Browse":
        show_search_browse()
    elif page == "🌐 Graph Visualization":
        show_graph_visualization()
    elif page == "📤 CSV Import":
        show_csv_import()
    elif page == "🕷️ C14 Scraper":
        show_c14_scraper()

def show_dashboard():
    """Display database statistics and overview"""
    st.header("📊 Database Overview")
    
    if st.session_state.repo:
        # Get database stats
        with st.spinner("Loading database statistics..."):
            stats = st.session_state.repo.get_database_stats()
        
        # Display stats in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Persons", stats.get('persons', 0))
            st.metric("🏢 VC Firms", stats.get('vc_firms', 0))
        
        with col2:
            st.metric("🚀 Startups", stats.get('startups', 0))
            st.metric("💰 VC Funds", stats.get('vc_funds', 0))
        
        with col3:
            st.metric("👼 Angel Syndicates", stats.get('angel_syndicates', 0))
            st.metric("🏛️ Institutions", stats.get('institutions', 0))
        
        with col4:
            st.metric("🏭 Corporates", stats.get('corporates', 0))
            st.metric("🔗 Relationships", stats.get('relationships', 0))
        
        # Recent activity placeholder
        st.subheader("Recent Activity")
        st.info("Recent additions and updates will be shown here in future updates.")
        
        # Cleanup section
        st.subheader("🧹 Database Cleanup")
        st.warning("⚠️ Use cleanup tools with caution! They will permanently delete duplicate data.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Check for Duplicates"):
                duplicate_check_queries = {
                    'Duplicate Persons': "MATCH (n:Person) WITH n.name as name, count(n) as cnt WHERE cnt > 1 RETURN name, cnt ORDER BY cnt DESC",
                    'Duplicate Startups': "MATCH (n:Startup) WITH n.name as name, count(n) as cnt WHERE cnt > 1 RETURN name, cnt ORDER BY cnt DESC",
                    'Duplicate VC Firms': "MATCH (n:VC_Firm) WITH n.name as name, count(n) as cnt WHERE cnt > 1 RETURN name, cnt ORDER BY cnt DESC",
                    'Duplicate VC Funds': "MATCH (n:VC_Fund) WITH n.name as name, count(n) as cnt WHERE cnt > 1 RETURN name, cnt ORDER BY cnt DESC"
                }
                
                duplicates_found = False
                for check_name, query in duplicate_check_queries.items():
                    try:
                        result = st.session_state.repo.connection.execute_query(query)
                        if result:
                            st.error(f"❌ {check_name}: {len(result)} duplicates found")
                            for dup in result[:5]:  # Show first 5
                                st.text(f"  • {dup['name']}: {dup['cnt']} copies")
                            duplicates_found = True
                    except:
                        pass
                
                if not duplicates_found:
                    st.success("✅ No duplicates found!")
        
        with col2:
            if st.button("🧹 Clean Duplicates", type="secondary"):
                st.info("🔧 Duplicate cleaning feature will be available after app restart.")

def show_analytics():
    """Show interesting analytics and insights about the Italian tech ecosystem"""
    st.header("📈 Italian Tech Ecosystem Analytics")
    
    if st.session_state.repo:
        tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Investors", "💰 Investment Insights", "🚀 Startup Analysis", "🌐 Network Analysis"])
        
        with tab1:
            st.subheader("🏆 Most Active Investors")
            
            # Query for most active investors
            query_active_investors = """
            MATCH (investor)-[r:INVESTS_IN]->(startup:Startup)
            RETURN investor.name AS investor_name, 
                   labels(investor)[0] AS investor_type,
                   count(r) AS investments_count,
                   collect(startup.name)[0..5] AS sample_startups
            ORDER BY investments_count DESC
            LIMIT 10
            """
            
            with st.spinner("Loading top investors..."):
                try:
                    result = st.session_state.repo.connection.execute_query(query_active_investors)
                    if result:
                        df = pd.DataFrame(result)
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.dataframe(df[['investor_name', 'investor_type', 'investments_count']], 
                                       column_config={
                                           'investor_name': 'Investor Name',
                                           'investor_type': 'Type',
                                           'investments_count': 'Investments'
                                       }, use_container_width=True)
                        
                        with col2:
                            st.bar_chart(df.set_index('investor_name')['investments_count'])
                    else:
                        st.info("No investment data found.")
                except Exception as e:
                    st.error(f"Error loading investor data: {e}")
            
            # Distribution of investor types
            st.subheader("📊 Investor Type Distribution")
            query_investor_types = """
            MATCH (n)
            WHERE n:VC_Firm OR n:Angel_Syndicate OR n:Institution OR n:VC_Fund OR n:Corporate
            RETURN labels(n)[0] AS investor_type, count(n) AS count
            ORDER BY count DESC
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_investor_types)
                if result:
                    df_types = pd.DataFrame(result)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(df_types, use_container_width=True)
                    with col2:
                        st.pie_chart(df_types.set_index('investor_type')['count'])
            except Exception as e:
                st.error(f"Error loading investor types: {e}")
        
        with tab2:
            st.subheader("💰 Investment Round Analysis")
            
            # Funding rounds analysis
            query_funding_rounds = """
            MATCH (investor)-[r:INVESTS_IN]->(startup:Startup)
            WHERE r.round_type IS NOT NULL
            RETURN r.round_type AS round_type, 
                   count(r) AS count,
                   avg(toFloat(replace(replace(replace(r.amount, 'EUR', ''), 'USD', ''), '.', ''))) AS avg_amount
            ORDER BY count DESC
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_funding_rounds)
                if result:
                    df_rounds = pd.DataFrame(result)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Rounds by Type")
                        st.bar_chart(df_rounds.set_index('round_type')['count'])
                    
                    with col2:
                        st.subheader("Round Details")
                        st.dataframe(df_rounds, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading funding rounds: {e}")
            
            # Top funded startups
            st.subheader("🚀 Most Funded Startups")
            query_funded_startups = """
            MATCH (investor)-[r:INVESTS_IN]->(startup:Startup)
            WHERE r.amount IS NOT NULL AND r.amount <> ''
            RETURN startup.name AS startup_name,
                   startup.sector AS sector,
                   count(r) AS funding_rounds,
                   collect(DISTINCT r.round_type) AS round_types,
                   collect(DISTINCT investor.name)[0..3] AS top_investors
            ORDER BY funding_rounds DESC
            LIMIT 15
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_funded_startups)
                if result:
                    df_funded = pd.DataFrame(result)
                    st.dataframe(df_funded, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading funded startups: {e}")
        
        with tab3:
            st.subheader("🚀 Startup Ecosystem Overview")
            
            # Startups by sector
            query_sectors = """
            MATCH (s:Startup)
            WHERE s.sector IS NOT NULL AND s.sector <> ''
            RETURN s.sector AS sector, count(s) AS count
            ORDER BY count DESC
            LIMIT 20
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_sectors)
                if result:
                    df_sectors = pd.DataFrame(result)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Top Sectors")
                        st.bar_chart(df_sectors.set_index('sector')['count'])
                    
                    with col2:
                        st.subheader("Sector Distribution")
                        st.dataframe(df_sectors, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading sectors: {e}")
            
            # Startups by employee count
            st.subheader("👥 Company Size Distribution")
            query_employees = """
            MATCH (s:Startup)
            WHERE s.employee_count IS NOT NULL AND s.employee_count <> ''
            RETURN s.employee_count AS size, count(s) AS count
            ORDER BY 
                CASE s.employee_count
                    WHEN '1-10' THEN 1
                    WHEN '11-50' THEN 2
                    WHEN '51-200' THEN 3
                    WHEN '201-500' THEN 4
                    WHEN '501-1000' THEN 5
                    WHEN '1000+' THEN 6
                    ELSE 7
                END
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_employees)
                if result:
                    df_employees = pd.DataFrame(result)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.bar_chart(df_employees.set_index('size')['count'])
                    with col2:
                        st.dataframe(df_employees, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading employee data: {e}")
            
            # Top startups by founding year
            st.subheader("📅 Startup Founding Timeline")
            query_timeline = """
            MATCH (s:Startup)
            WHERE s.founding_year IS NOT NULL AND s.founding_year > 2000
            RETURN s.founding_year AS year, count(s) AS startups_founded
            ORDER BY year DESC
            LIMIT 15
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_timeline)
                if result:
                    df_timeline = pd.DataFrame(result)
                    st.line_chart(df_timeline.set_index('year')['startups_founded'])
                    st.dataframe(df_timeline, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading timeline data: {e}")
        
        with tab4:
            st.subheader("🌐 Network Insights")
            
            # Most connected founders
            query_founders = """
            MATCH (p:Person)-[r:FOUNDED]->(s:Startup)
            RETURN p.name AS founder_name, 
                   p.surname AS founder_surname,
                   count(r) AS startups_founded,
                   collect(s.name) AS startups
            ORDER BY startups_founded DESC
            LIMIT 10
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_founders)
                if result:
                    df_founders = pd.DataFrame(result)
                    st.subheader("🏅 Serial Entrepreneurs")
                    
                    # Show only multi-startup founders
                    multi_founders = df_founders[df_founders['startups_founded'] > 1]
                    if not multi_founders.empty:
                        st.dataframe(multi_founders[['founder_name', 'founder_surname', 'startups_founded']], 
                                   use_container_width=True)
                    else:
                        st.info("No serial entrepreneurs found (founders with multiple startups)")
            except Exception as e:
                st.error(f"Error loading founder data: {e}")
            
            # Co-investment analysis
            st.subheader("🤝 Co-Investment Patterns")
            query_coinvestment = """
            MATCH (i1)-[:INVESTS_IN]->(s:Startup)<-[:INVESTS_IN]-(i2)
            WHERE id(i1) < id(i2)
            RETURN i1.name AS investor1, i2.name AS investor2, 
                   count(s) AS co_investments,
                   collect(s.name)[0..3] AS sample_startups
            ORDER BY co_investments DESC
            LIMIT 10
            """
            
            try:
                result = st.session_state.repo.connection.execute_query(query_coinvestment)
                if result:
                    df_coinvest = pd.DataFrame(result)
                    # Show only pairs with multiple co-investments
                    frequent_pairs = df_coinvest[df_coinvest['co_investments'] > 1]
                    if not frequent_pairs.empty:
                        st.dataframe(frequent_pairs, use_container_width=True)
                    else:
                        st.info("No frequent co-investment patterns found")
            except Exception as e:
                st.error(f"Error loading co-investment data: {e}")
    
    else:
        st.error("No Neo4j connection available.")

def show_add_entity():
    """Show forms for adding new entities"""
    st.header("➕ Add New Entity")
    
    entity_type = st.selectbox(
        "Select entity type:",
        ["Person", "Startup", "VC Firm", "VC Fund", "Angel Syndicate", "Institution", "Corporate"]
    )
    
    if entity_type == "Person":
        show_person_form()
    elif entity_type == "Startup":
        show_startup_form()
    elif entity_type == "VC Firm":
        show_vc_firm_form()
    elif entity_type == "VC Fund":
        show_vc_fund_form()
    elif entity_type == "Angel Syndicate":
        show_angel_syndicate_form()
    elif entity_type == "Institution":
        show_institution_form()
    elif entity_type == "Corporate":
        show_corporate_form()

def show_person_form():
    """Form for adding a new person"""
    st.subheader("👥 Add New Person")
    
    with st.form("person_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", help="Full name")
            surname = st.text_input("Surname")
            role_type = st.selectbox("Role Type *", [e.value for e in PersonRoleType])
            linkedin_url = st.text_input("LinkedIn URL")
            twitter_handle = st.text_input("Twitter Handle")
            location = st.text_input("Location")
        
        with col2:
            biography = st.text_area("Biography")
            birth_year = st.number_input("Birth Year", min_value=1900, max_value=2010, value=None)
            education = st.text_area("Education")
            previous_experience = st.text_area("Previous Experience")
            specialization = st.text_input("Specialization")
            reputation_score = st.slider("Reputation Score", 1, 100, 50)
        
        submitted = st.form_submit_button("Add Person")
        
        if submitted and name:
            person_data = {
                'name': name,
                'surname': surname,
                'role_type': role_type,
                'linkedin_url': linkedin_url or None,
                'twitter_handle': twitter_handle or None,
                'biography': biography or None,
                'location': location or None,
                'birth_year': birth_year,
                'education': education or None,
                'previous_experience': previous_experience or None,
                'specialization': specialization or None,
                'reputation_score': reputation_score
            }
            
            if st.session_state.repo.create_person(person_data):
                st.success("✅ Person added successfully!")
            else:
                st.error("❌ Failed to add person")

def show_startup_form():
    """Form for adding a new startup"""
    st.subheader("🚀 Add New Startup")
    
    with st.form("startup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            description = st.text_area("Description")
            website = st.text_input("Website")
            founded_year = st.number_input("Founded Year", min_value=1990, max_value=2025, value=None)
            stage = st.selectbox("Stage", [None] + [e.value for e in StartupStage])
            sector = st.text_input("Sector")
        
        with col2:
            business_model = st.text_input("Business Model")
            headquarters = st.text_input("Headquarters")
            employee_count = st.number_input("Employee Count", min_value=0, value=None)
            status = st.selectbox("Status", [e.value for e in StartupStatus])
            total_funding = st.number_input("Total Funding (€)", min_value=0.0, value=None)
            last_funding_date = st.date_input("Last Funding Date", value=None)
        
        # Optional exit information
        st.subheader("Exit Information (if applicable)")
        col3, col4 = st.columns(2)
        with col3:
            exit_date = st.date_input("Exit Date", value=None)
        with col4:
            exit_value = st.number_input("Exit Value (€)", min_value=0.0, value=None)
        
        submitted = st.form_submit_button("Add Startup")
        
        if submitted and name:
            startup_data = {
                'name': name,
                'description': description or None,
                'website': website or None,
                'founded_year': founded_year,
                'stage': stage,
                'sector': sector or None,
                'business_model': business_model or None,
                'headquarters': headquarters or None,
                'employee_count': employee_count,
                'status': status,
                'total_funding': total_funding,
                'last_funding_date': last_funding_date,
                'exit_date': exit_date,
                'exit_value': exit_value
            }
            
            if st.session_state.repo.create_startup(startup_data):
                st.success("✅ Startup added successfully!")
            else:
                st.error("❌ Failed to add startup")

def show_vc_firm_form():
    """Form for adding a new VC firm"""
    st.subheader("🏢 Add New VC Firm")
    
    with st.form("vc_firm_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            description = st.text_area("Description")
            website = st.text_input("Website")
            founded_year = st.number_input("Founded Year", min_value=1900, max_value=2025, value=None)
            headquarters = st.text_input("Headquarters")
            firm_type = st.selectbox("Type *", [e.value for e in VCFirmType])
        
        with col2:
            investment_focus = st.text_input("Investment Focus")
            stage_focus = st.text_input("Stage Focus")
            geographic_focus = st.text_input("Geographic Focus")
            team_size = st.number_input("Team Size", min_value=1, value=None)
            aum = st.number_input("Assets Under Management (€)", min_value=0.0, value=None)
            portfolio_count = st.number_input("Portfolio Companies Count", min_value=0, value=None)
        
        submitted = st.form_submit_button("Add VC Firm")
        
        if submitted and name:
            firm_data = {
                'name': name,
                'description': description or None,
                'website': website or None,
                'founded_year': founded_year,
                'headquarters': headquarters or None,
                'type': firm_type,
                'investment_focus': investment_focus or None,
                'stage_focus': stage_focus or None,
                'geographic_focus': geographic_focus or None,
                'team_size': team_size,
                'assets_under_management': aum,
                'portfolio_companies_count': portfolio_count
            }
            
            if st.session_state.repo.create_vc_firm(firm_data):
                st.success("✅ VC Firm added successfully!")
            else:
                st.error("❌ Failed to add VC firm")

def show_vc_fund_form():
    """Form for adding a new VC fund"""
    st.subheader("💰 Add New VC Fund")
    
    with st.form("vc_fund_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Fund Name *")
            fund_size = st.number_input("Fund Size (€)", min_value=0.0, value=None)
            vintage_year = st.number_input("Vintage Year", min_value=2000, max_value=2030, value=None)
            fund_number = st.text_input("Fund Number (e.g., Fund I, Fund II)")
            status = st.text_input("Status")
            target_sectors = st.text_input("Target Sectors")
        
        with col2:
            target_stages = st.text_input("Target Stages")
            geographic_focus = st.text_input("Geographic Focus")
            first_close = st.date_input("First Close Date", value=None)
            final_close = st.date_input("Final Close Date", value=None)
            investment_period = st.number_input("Investment Period (years)", min_value=1, max_value=10, value=None)
            fund_life = st.number_input("Fund Life (years)", min_value=5, max_value=15, value=None)
        
        deployed_capital = st.number_input("Deployed Capital (€)", min_value=0.0, value=None)
        
        submitted = st.form_submit_button("Add VC Fund")
        
        if submitted and name:
            fund_data = {
                'name': name,
                'fund_size': fund_size,
                'vintage_year': vintage_year,
                'fund_number': fund_number or None,
                'status': status or None,
                'target_sectors': target_sectors or None,
                'target_stages': target_stages or None,
                'geographic_focus': geographic_focus or None,
                'first_close_date': first_close,
                'final_close_date': final_close,
                'investment_period': investment_period,
                'fund_life': fund_life,
                'deployed_capital': deployed_capital
            }
            
            if st.session_state.repo.create_vc_fund(fund_data):
                st.success("✅ VC Fund added successfully!")
            else:
                st.error("❌ Failed to add VC fund")

def show_angel_syndicate_form():
    """Form for adding a new angel syndicate"""
    st.subheader("👼 Add New Angel Syndicate")
    
    with st.form("angel_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            syndicate_type = st.selectbox("Type *", ["angel_syndicate", "family_office", "crowdfunding_platform", "other"])
            description = st.text_area("Description")
            website = st.text_input("Website")
            founded_year = st.number_input("Founded Year", min_value=1990, max_value=2025, value=None)
            headquarters = st.text_input("Headquarters")
        
        with col2:
            members_count = st.number_input("Members Count", min_value=1, value=None)
            investment_focus = st.text_input("Investment Focus")
            stage_focus = st.text_input("Stage Focus")
            ticket_min = st.number_input("Min Ticket Size (€)", min_value=0.0, value=None)
            ticket_max = st.number_input("Max Ticket Size (€)", min_value=0.0, value=None)
            total_investments = st.number_input("Total Investments", min_value=0, value=None)
        
        submitted = st.form_submit_button("Add Angel Syndicate")
        
        if submitted and name:
            syndicate_data = {
                'name': name,
                'type': syndicate_type,
                'description': description or None,
                'website': website or None,
                'founded_year': founded_year,
                'headquarters': headquarters or None,
                'members_count': members_count,
                'investment_focus': investment_focus or None,
                'stage_focus': stage_focus or None,
                'ticket_size_min': ticket_min,
                'ticket_size_max': ticket_max,
                'total_investments': total_investments
            }
            
            if st.session_state.repo.create_angel_syndicate(syndicate_data):
                st.success("✅ Angel Syndicate added successfully!")
            else:
                st.error("❌ Failed to add angel syndicate")

def show_institution_form():
    """Form for adding a new institution"""
    st.subheader("🏛️ Add New Institution")
    
    with st.form("institution_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            inst_type = st.selectbox("Type *", [e.value for e in InstitutionType])
            description = st.text_area("Description")
            website = st.text_input("Website")
            founded_year = st.number_input("Founded Year", min_value=1900, max_value=2025, value=None)
            headquarters = st.text_input("Headquarters")
        
        with col2:
            program_duration = st.number_input("Program Duration (months)", min_value=1, max_value=24, value=None)
            batch_size = st.number_input("Batch Size", min_value=1, value=None)
            sectors_focus = st.text_input("Sectors Focus")
            equity_taken = st.slider("Equity Taken (%)", 0.0, 100.0, 0.0)
            funding_provided = st.number_input("Funding Provided (€)", min_value=0.0, value=None)
            portfolio_count = st.number_input("Portfolio Companies Count", min_value=0, value=None)
        
        success_rate = st.slider("Success Rate (%)", 0.0, 100.0, 0.0)
        
        submitted = st.form_submit_button("Add Institution")
        
        if submitted and name:
            institution_data = {
                'name': name,
                'type': inst_type,
                'description': description or None,
                'website': website or None,
                'founded_year': founded_year,
                'headquarters': headquarters or None,
                'program_duration': program_duration,
                'batch_size': batch_size,
                'sectors_focus': sectors_focus or None,
                'equity_taken': equity_taken if equity_taken > 0 else None,
                'funding_provided': funding_provided,
                'portfolio_companies_count': portfolio_count,
                'success_rate': success_rate if success_rate > 0 else None
            }
            
            if st.session_state.repo.create_institution(institution_data):
                st.success("✅ Institution added successfully!")
            else:
                st.error("❌ Failed to add institution")

def show_corporate_form():
    """Form for adding a new corporate"""
    st.subheader("🏭 Add New Corporate")
    
    with st.form("corporate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            description = st.text_area("Description")
            website = st.text_input("Website")
            founded_year = st.number_input("Founded Year", min_value=1800, max_value=2025, value=None)
            headquarters = st.text_input("Headquarters")
            sector = st.text_input("Sector")
        
        with col2:
            size = st.selectbox("Size", [None, "startup", "sme", "large_enterprise", "multinational"])
            revenue = st.number_input("Revenue (€)", min_value=0.0, value=None)
            employee_count = st.number_input("Employee Count", min_value=1, value=None)
            stock_exchange = st.text_input("Stock Exchange")
            ticker = st.text_input("Ticker")
        
        col3, col4 = st.columns(2)
        with col3:
            has_cvc_arm = st.checkbox("Has CVC Arm")
        with col4:
            innovation_programs = st.checkbox("Has Innovation Programs")
        
        submitted = st.form_submit_button("Add Corporate")
        
        if submitted and name:
            corporate_data = {
                'name': name,
                'description': description or None,
                'website': website or None,
                'founded_year': founded_year,
                'headquarters': headquarters or None,
                'sector': sector or None,
                'size': size,
                'revenue': revenue,
                'employee_count': employee_count,
                'stock_exchange': stock_exchange or None,
                'ticker': ticker or None,
                'has_cvc_arm': has_cvc_arm,
                'innovation_programs': innovation_programs
            }
            
            if st.session_state.repo.create_corporate(corporate_data):
                st.success("✅ Corporate added successfully!")
            else:
                st.error("❌ Failed to add corporate")

def show_add_relationship():
    """Show forms for adding relationships"""
    st.header("🔗 Add New Relationship")
    
    relationship_type = st.selectbox(
        "Select relationship type:",
        ["Founding (Person → Startup)", "Investment (Fund → Startup)", "Angel Investment (Person → Startup)", 
         "Employment (Person → Organization)", "Fund Management (Firm → Fund)",
         "LP Participation (Investor → Fund)", "Acceleration (Startup → Institution)",
         "Acquisition (Corporate → Startup)", "Partnership (Corporate → Organization)",
         "Mentorship (Person → Person)", "Spin-off (Startup → Organization)"]
    )
    
    if relationship_type == "Founding (Person → Startup)":
        show_founding_form()
    elif relationship_type == "Investment (Fund → Startup)":
        show_investment_form()
    elif relationship_type == "Angel Investment (Person → Startup)":
        show_angel_investment_form()
    elif relationship_type == "Employment (Person → Organization)":
        show_employment_form()
    elif relationship_type == "Fund Management (Firm → Fund)":
        show_fund_management_form()
    elif relationship_type == "LP Participation (Investor → Fund)":
        show_lp_participation_form()
    elif relationship_type == "Acceleration (Startup → Institution)":
        show_acceleration_form()
    elif relationship_type == "Acquisition (Corporate → Startup)":
        show_acquisition_form()
    elif relationship_type == "Partnership (Corporate → Organization)":
        show_partnership_form()
    elif relationship_type == "Mentorship (Person → Person)":
        show_mentorship_form()
    elif relationship_type == "Spin-off (Startup → Organization)":
        show_spinoff_form()

def show_investment_form():
    """Form for adding investment relationships"""
    st.subheader("💰 Add Investment Relationship")
    
    # Get available entities
    funds = st.session_state.repo.get_all_entities_by_type("VC_Fund")
    angel_syndicates = st.session_state.repo.get_all_entities_by_type("Angel_Syndicate")
    corporates = st.session_state.repo.get_all_entities_by_type("Corporate")
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    
    with st.form("investment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            investor_type = st.selectbox("Investor Type", ["VC_Fund", "Angel_Syndicate", "Corporate"])
            
            if investor_type == "VC_Fund":
                investor_options = [f"{fund['name']}" for fund in funds]
            elif investor_type == "Angel_Syndicate":
                investor_options = [f"{syndicate['name']}" for syndicate in angel_syndicates]
            else:
                investor_options = [f"{corp['name']}" for corp in corporates]
            
            investor_name = st.selectbox("Investor", investor_options)
            startup_name = st.selectbox("Startup", [startup['name'] for startup in startups])
            
            round_stage = st.selectbox("Round Stage", [e.value for e in StartupStage])
            round_date = st.date_input("Round Date")
            amount = st.number_input("Amount (€)", min_value=0.0)
        
        with col2:
            valuation_pre = st.number_input("Pre-money Valuation (€)", min_value=0.0, value=None)
            valuation_post = st.number_input("Post-money Valuation (€)", min_value=0.0, value=None)
            is_lead = st.checkbox("Lead Investor")
            board_seats = st.number_input("Board Seats", min_value=0, value=0)
            equity_pct = st.number_input("Equity Percentage", min_value=0.0, max_value=100.0, value=None)
        
        submitted = st.form_submit_button("Add Investment")
        
        if submitted and investor_name and startup_name and amount > 0:
            investment_data = {
                'round_stage': round_stage,
                'round_date': round_date,
                'amount': amount,
                'valuation_pre': valuation_pre,
                'valuation_post': valuation_post,
                'is_lead_investor': is_lead,
                'board_seats': board_seats,
                'equity_percentage': equity_pct
            }
            
            if st.session_state.repo.create_investment_relationship(
                investor_name, investor_type, startup_name, investment_data
            ):
                st.success("✅ Investment relationship added successfully!")
            else:
                st.error("❌ Failed to add investment relationship")

def show_angel_investment_form():
    """Form for adding angel investment relationships"""
    st.subheader("👼 Add Angel Investment Relationship")
    
    persons = st.session_state.repo.get_all_entities_by_type("Person")
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    
    if not persons or not startups:
        st.warning("Please add some People and Startups first.")
        return
    
    with st.form("angel_investment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            person_name = st.selectbox("Person", [person['name'] for person in persons])
            startup_name = st.selectbox("Startup", [startup['name'] for startup in startups])
            investment_date = st.date_input("Investment Date")
            round_stage = st.selectbox("Round Stage", [e.value for e in StartupStage])
        
        with col2:
            amount = st.number_input("Amount (€)", min_value=0.0)
            lead_investor = st.checkbox("Lead Investor")
            board_seat = st.checkbox("Board Seat")
        
        submitted = st.form_submit_button("Add Angel Investment")
        
        if submitted:
            if not person_name:
                st.error("❌ Please select a person")
            elif not startup_name:
                st.error("❌ Please select a startup")
            elif amount <= 0:
                st.error("❌ Investment amount must be greater than 0")
            else:
                try:
                    from app.models import AngelInvestment
                    
                    investment = AngelInvestment(
                        investment_date=investment_date,
                        round_stage=round_stage,
                        amount=amount,
                        lead_investor=lead_investor,
                        board_seat=board_seat
                    )
                    
                    success = st.session_state.repo.create_angel_investment_relationship(
                        person_name, startup_name, investment.model_dump()
                    )
                    
                    if success:
                        st.success("✅ Angel investment relationship added successfully!")
                    else:
                        st.error("❌ Failed to add angel investment relationship")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

def show_employment_form():
    """Form for adding employment relationships"""
    st.subheader("👔 Add Employment Relationship")
    
    persons = st.session_state.repo.get_all_entities_by_type("Person")
    vc_firms = st.session_state.repo.get_all_entities_by_type("VC_Firm")
    institutions = st.session_state.repo.get_all_entities_by_type("Institution")
    corporates = st.session_state.repo.get_all_entities_by_type("Corporate")
    
    with st.form("employment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            person_name = st.selectbox("Person", [person['name'] for person in persons])
            org_type = st.selectbox("Organization Type", ["VC_Firm", "Institution", "Corporate"])
            
            if org_type == "VC_Firm":
                org_options = [firm['name'] for firm in vc_firms]
            elif org_type == "Institution":
                org_options = [inst['name'] for inst in institutions]
            else:
                org_options = [corp['name'] for corp in corporates]
            
            org_name = st.selectbox("Organization", org_options)
            role = st.text_input("Role")
        
        with col2:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date", value=None)
            seniority_level = st.text_input("Seniority Level")
            is_current = st.checkbox("Current Position", value=True)
        
        submitted = st.form_submit_button("Add Employment")
        
        if submitted and person_name and org_name and role:
            employment_data = {
                'role': role,
                'start_date': start_date,
                'end_date': end_date,
                'seniority_level': seniority_level or None,
                'is_current': is_current
            }
            
            if st.session_state.repo.create_employment_relationship(
                person_name, org_name, org_type, employment_data
            ):
                st.success("✅ Employment relationship added successfully!")
            else:
                st.error("❌ Failed to add employment relationship")

def show_fund_management_form():
    """Form for adding fund management relationships"""
    st.subheader("🏢 Add Fund Management Relationship")
    
    firms = st.session_state.repo.get_all_entities_by_type("VC_Firm")
    funds = st.session_state.repo.get_all_entities_by_type("VC_Fund")
    
    with st.form("fund_management_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            firm_name = st.selectbox("VC Firm", [firm['name'] for firm in firms])
            fund_name = st.selectbox("VC Fund", [fund['name'] for fund in funds])
            start_date = st.date_input("Start Date")
        
        with col2:
            management_fee = st.number_input("Management Fee (%)", min_value=0.0, max_value=10.0, value=2.0)
            carried_interest = st.number_input("Carried Interest (%)", min_value=0.0, max_value=50.0, value=20.0)
        
        submitted = st.form_submit_button("Add Fund Management")
        
        if submitted and firm_name and fund_name:
            management_data = {
                'management_fee': management_fee,
                'carried_interest': carried_interest,
                'start_date': start_date
            }
            
            if st.session_state.repo.create_fund_management_relationship(
                firm_name, fund_name, management_data
            ):
                st.success("✅ Fund management relationship added successfully!")
            else:
                st.error("❌ Failed to add fund management relationship")

def show_founding_form():
    """Form for adding founding relationships"""
    st.subheader("🚀 Add Founding Relationship")
    
    persons = st.session_state.repo.get_all_entities_by_type("Person")
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    
    with st.form("founding_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            person_name = st.selectbox("Founder", [person['name'] for person in persons])
            startup_name = st.selectbox("Startup", [startup['name'] for startup in startups])
            role = st.selectbox("Role", ["CEO", "CTO", "Co-founder", "Founder", "Other"])
            founding_date = st.date_input("Founding Date")
        
        with col2:
            equity_percentage = st.number_input("Initial Equity (%)", min_value=0.0, max_value=100.0, value=None)
            is_current = st.checkbox("Still Active", value=True)
            exit_date = st.date_input("Exit Date (if applicable)", value=None)
        
        submitted = st.form_submit_button("Add Founding Relationship")
        
        if submitted and person_name and startup_name and role:
            founding_data = {
                'role': role,
                'founding_date': founding_date,
                'equity_percentage': equity_percentage,
                'is_current': is_current,
                'exit_date': exit_date
            }
            
            if st.session_state.repo.create_founded_relationship(
                person_name, startup_name, founding_data
            ):
                st.success("✅ Founding relationship added successfully!")
            else:
                st.error("❌ Failed to add founding relationship")

def show_search_browse():
    """Show search and browse functionality"""
    st.header("🔍 Search & Browse")
    
    search_type = st.selectbox(
        "Search in:",
        ["Person", "Startup", "VC_Firm", "VC_Fund", "Angel_Syndicate", "Institution", "Corporate"]
    )
    
    search_term = st.text_input("Search term (leave empty to show all)")
    
    if st.button("Search") or search_term == "":
        if search_term:
            results = st.session_state.repo.search_entities(search_type, search_term)
        else:
            results = st.session_state.repo.get_all_entities_by_type(search_type)
        
        if results:
            st.success(f"Found {len(results)} results:")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No results found.")

def show_lp_participation_form():
    """Form for adding LP participation relationships"""
    st.subheader("🏦 Add LP Participation")
    
    # Get available entities
    people = st.session_state.repo.get_all_entities_by_type("Person")
    institutions = st.session_state.repo.get_all_entities_by_type("Institution")
    vc_firms = st.session_state.repo.get_all_entities_by_type("VC_Firm")
    funds = st.session_state.repo.get_all_entities_by_type("VC_Fund")
    
    if (not people and not institutions and not vc_firms) or not funds:
        st.warning("Please add some Investors (People, Institutions, or VC Firms) and VC Funds first.")
        return
    
    # Select investor type OUTSIDE the form to allow dynamic updates
    investor_entity_type = st.selectbox("Select Investor Type:", 
                                      ["Person", "Institution", "VC_Firm"],
                                      key="lp_investor_type")
    
    # Get the appropriate list of investors based on type
    if investor_entity_type == "Person":
        available_investors = people if people else []
        investor_label = "Select Person (LP):"
    elif investor_entity_type == "Institution":
        available_investors = institutions if institutions else []
        investor_label = "Select Institution (LP):"
    else:  # VC_Firm
        available_investors = vc_firms if vc_firms else []
        investor_label = "Select VC Firm (LP):"
    
    if not available_investors:
        st.warning(f"No {investor_entity_type}s available. Please add some first.")
        return
    
    with st.form("lp_participation_form"):
        # Now select specific investor
        investor_name = st.selectbox(investor_label, [inv['name'] for inv in available_investors])
        fund_name = st.selectbox("Select VC Fund:", [f['name'] for f in funds])
        
        commitment_amount = st.number_input("Commitment Amount (€):", min_value=0.0, step=10000.0)
        commitment_date = st.date_input("Commitment Date:")
        
        # LP category (different from entity type)
        lp_category = st.selectbox("LP Category:", 
                                 ["institutional", "hnwi", "family_office", "corporate", "government", "pension_fund", "sovereign_fund", "other"])
        
        submitted = st.form_submit_button("Add LP Participation")
        
        if submitted:
            from app.models import LPParticipation
            try:
                participation = LPParticipation(
                    commitment_amount=commitment_amount,
                    commitment_date=commitment_date,
                    investor_type=lp_category
                )
                success = st.session_state.repo.create_lp_participation_relationship(
                    investor_name, investor_entity_type, fund_name, participation.model_dump()
                )
                if success:
                    st.success("✅ LP participation added successfully!")
                else:
                    st.error("❌ Failed to add LP participation")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_acceleration_form():
    """Form for adding acceleration relationships"""
    st.subheader("🚀 Add Acceleration Program")
    
    # Get available entities
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    institutions = st.session_state.repo.get_all_entities_by_type("Institution")
    
    if not startups or not institutions:
        st.warning("Please add some Startups and Institutions first.")
        return
    
    with st.form("acceleration_form"):
        startup_name = st.selectbox("Select Startup:", [s['name'] for s in startups])
        institution_name = st.selectbox("Select Institution (Accelerator):", [i['name'] for i in institutions])
        
        program_name = st.text_input("Program Name:", placeholder="e.g., TechStars Milano 2024")
        batch_name = st.text_input("Batch Name (optional):", placeholder="e.g., Batch 15")
        start_date = st.date_input("Program Start Date:")
        end_date = st.date_input("Program End Date (optional):", value=None)
        
        col1, col2 = st.columns(2)
        with col1:
            equity_taken = st.number_input("Equity Taken (%):", min_value=0.0, max_value=100.0, step=0.1)
        with col2:
            funding_received = st.number_input("Funding Received (€):", min_value=0.0, step=1000.0)
        
        demo_day_date = st.date_input("Demo Day Date (optional):", value=None)
        
        submitted = st.form_submit_button("Add Acceleration")
        
        if submitted:
            from app.models import Acceleration
            try:
                acceleration = Acceleration(
                    program_name=program_name,
                    batch_name=batch_name if batch_name else None,
                    start_date=start_date,
                    end_date=end_date,
                    equity_taken=equity_taken if equity_taken > 0 else None,
                    funding_received=funding_received if funding_received > 0 else None,
                    demo_day_date=demo_day_date
                )
                success = st.session_state.repo.create_acceleration_relationship(
                    startup_name, institution_name, acceleration.model_dump()
                )
                if success:
                    st.success("✅ Acceleration program added successfully!")
                else:
                    st.error("❌ Failed to add acceleration program")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_acquisition_form():
    """Form for adding acquisition relationships"""
    st.subheader("🏢 Add Acquisition")
    
    # Get available entities
    corporates = st.session_state.repo.get_all_entities_by_type("Corporate")
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    
    if not corporates or not startups:
        st.warning("Please add some Corporates and Startups first.")
        return
    
    with st.form("acquisition_form"):
        corporate_name = st.selectbox("Select Corporate (Acquirer):", [c['name'] for c in corporates])
        startup_name = st.selectbox("Select Startup (Target):", [s['name'] for s in startups])
        
        acquisition_date = st.date_input("Acquisition Date:")
        acquisition_value = st.number_input("Acquisition Value (€, optional):", min_value=0.0, step=1000000.0)
        acquisition_type = st.selectbox("Acquisition Type:", 
                                      ["full_acquisition", "majority_stake", "minority_stake"])
        
        strategic_rationale = st.text_area("Strategic Rationale (optional):", 
                                         placeholder="e.g., Technology acquisition for AI capabilities")
        integration_status = st.selectbox("Integration Status (optional):", 
                                        ["", "planned", "in_progress", "completed", "standalone"])
        
        submitted = st.form_submit_button("Add Acquisition")
        
        if submitted:
            from app.models import Acquisition
            try:
                acquisition = Acquisition(
                    acquisition_date=acquisition_date,
                    acquisition_value=acquisition_value if acquisition_value > 0 else None,
                    acquisition_type=acquisition_type,
                    strategic_rationale=strategic_rationale if strategic_rationale else None,
                    integration_status=integration_status if integration_status else None
                )
                success = st.session_state.repo.create_acquisition_relationship(
                    corporate_name, startup_name, acquisition.model_dump()
                )
                if success:
                    st.success("✅ Acquisition added successfully!")
                else:
                    st.error("❌ Failed to add acquisition")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_partnership_form():
    """Form for adding partnership relationships"""
    st.subheader("🤝 Add Partnership")
    
    # Get available entities
    corporates = st.session_state.repo.get_all_entities_by_type("Corporate")
    vc_firms = st.session_state.repo.get_all_entities_by_type("VC_Firm")
    institutions = st.session_state.repo.get_all_entities_by_type("Institution")
    
    if not corporates or (not vc_firms and not institutions):
        st.warning("Please add some Corporates and VC Firms/Institutions first.")
        return
    
    # Select partner type OUTSIDE the form to allow dynamic updates
    partner_type = st.selectbox("Partner Type:", ["VC_Firm", "Institution"],
                               key="partnership_partner_type")
    
    # Get the appropriate list of partners based on type
    if partner_type == "VC_Firm":
        available_partners = vc_firms if vc_firms else []
        partner_label = "Select VC Firm:"
    else:  # Institution
        available_partners = institutions if institutions else []
        partner_label = "Select Institution:"
    
    if not available_partners:
        st.warning(f"No {partner_type}s available. Please add some first.")
        return
    
    with st.form("partnership_form"):
        corporate_name = st.selectbox("Select Corporate:", [c['name'] for c in corporates])
        partner_name = st.selectbox(partner_label, [p['name'] for p in available_partners])
        
        partnership_type = st.selectbox("Partnership Type:", 
                                      ["strategic", "commercial", "investment", "program"])
        start_date = st.date_input("Partnership Start Date:")
        description = st.text_area("Description (optional):", 
                                 placeholder="e.g., Joint venture for fintech innovation")
        is_active = st.checkbox("Partnership is active", value=True)
        
        submitted = st.form_submit_button("Add Partnership")
        
        if submitted:
            from app.models import Partnership
            try:
                partnership = Partnership(
                    partnership_type=partnership_type,
                    start_date=start_date,
                    description=description if description else None,
                    is_active=is_active
                )
                success = st.session_state.repo.create_partnership_relationship(
                    corporate_name, partner_name, partner_type, partnership.model_dump()
                )
                if success:
                    st.success("✅ Partnership added successfully!")
                else:
                    st.error("❌ Failed to add partnership")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_mentorship_form():
    """Form for adding mentorship relationships"""
    st.subheader("🎯 Add Mentorship")
    
    # Get available entities
    people = st.session_state.repo.get_all_entities_by_type("Person")
    
    if not people or len(people) < 2:
        st.warning("Please add at least 2 People first.")
        return
    
    with st.form("mentorship_form"):
        mentor_name = st.selectbox("Select Mentor:", [p['name'] for p in people])
        mentee_name = st.selectbox("Select Mentee:", [p['name'] for p in people if p['name'] != mentor_name])
        
        relationship_type = st.selectbox("Relationship Type:", 
                                       ["formal_mentor", "advisor", "informal"])
        start_date = st.date_input("Mentorship Start Date:")
        end_date = st.date_input("Mentorship End Date (optional):", value=None)
        context = st.text_area("Context (optional):", 
                             placeholder="e.g., Startup acceleration program, industry networking")
        
        submitted = st.form_submit_button("Add Mentorship")
        
        if submitted:
            if mentor_name == mentee_name:
                st.error("❌ Mentor and mentee cannot be the same person")
                return
                
            from app.models import Mentorship
            try:
                mentorship = Mentorship(
                    start_date=start_date,
                    end_date=end_date,
                    relationship_type=relationship_type,
                    context=context if context else None
                )
                success = st.session_state.repo.create_mentorship_relationship(
                    mentor_name, mentee_name, mentorship.model_dump()
                )
                if success:
                    st.success("✅ Mentorship added successfully!")
                else:
                    st.error("❌ Failed to add mentorship")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_spinoff_form():
    """Form for adding spin-off relationships"""
    st.subheader("🌱 Add Spin-off")
    
    # Get available entities
    startups = st.session_state.repo.get_all_entities_by_type("Startup")
    corporates = st.session_state.repo.get_all_entities_by_type("Corporate")
    institutions = st.session_state.repo.get_all_entities_by_type("Institution")
    
    if not startups or (not corporates and not institutions):
        st.warning("Please add some Startups and Corporates/Institutions first.")
        return
    
    # Select parent type OUTSIDE the form to allow dynamic updates
    parent_type = st.selectbox("Parent Type:", ["Corporate", "Institution"],
                              key="spinoff_parent_type")
    
    # Get the appropriate list of parents based on type
    if parent_type == "Corporate":
        available_parents = corporates if corporates else []
        parent_label = "Select Corporate Parent:"
    else:  # Institution
        available_parents = institutions if institutions else []
        parent_label = "Select Institution Parent:"
    
    if not available_parents:
        st.warning(f"No {parent_type}s available. Please add some first.")
        return
    
    with st.form("spinoff_form"):
        startup_name = st.selectbox("Select Startup (Spin-off):", [s['name'] for s in startups])
        parent_name = st.selectbox(parent_label, [p['name'] for p in available_parents])
        
        spinoff_date = st.date_input("Spin-off Date:")
        technology_transferred = st.text_area("Technology Transferred (optional):", 
                                            placeholder="e.g., AI algorithms, patent portfolio")
        initial_equity = st.number_input("Initial Equity Retained by Parent (%):", 
                                       min_value=0.0, max_value=100.0, step=0.1)
        support_provided = st.text_area("Support Provided (optional):", 
                                      placeholder="e.g., Seed funding, office space, mentoring")
        
        submitted = st.form_submit_button("Add Spin-off")
        
        if submitted:
            from app.models import SpinOff
            try:
                spinoff = SpinOff(
                    spinoff_date=spinoff_date,
                    technology_transferred=technology_transferred if technology_transferred else None,
                    initial_equity=initial_equity if initial_equity > 0 else None,
                    support_provided=support_provided if support_provided else None
                )
                success = st.session_state.repo.create_spinoff_relationship(
                    startup_name, parent_name, parent_type, spinoff.model_dump()
                )
                if success:
                    st.success("✅ Spin-off added successfully!")
                else:
                    st.error("❌ Failed to add spin-off")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_graph_visualization():
    """Show interactive graph visualization"""
    st.header("🌐 Graph Visualization")
    st.markdown("Interactive visualization of the Italian Tech Ecosystem")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.slider("Number of nodes to display:", min_value=10, max_value=200, value=50, step=10)
    
    with col2:
        layout_type = st.selectbox("Layout Type:", 
                                 ["spring", "circular", "kamada_kawai", "random"])
    
    with col3:
        show_labels = st.checkbox("Show node labels", value=True)
    
    # Get graph data
    if st.button("🔄 Refresh Graph") or 'graph_data' not in st.session_state:
        with st.spinner("Loading graph data..."):
            graph_data = st.session_state.repo.get_graph_data(limit=limit)
            st.session_state.graph_data = graph_data
    
    graph_data = st.session_state.get('graph_data', {'nodes': [], 'relationships': []})
    
    if not graph_data['nodes']:
        st.warning("No data found. Please add some entities and relationships first.")
        return
    
    # Create NetworkX graph for layout calculation
    G = nx.Graph()
    
    # Node colors by type
    node_colors = {
        'Person': '#FF6B6B',
        'Startup': '#4ECDC4', 
        'VC_Firm': '#45B7D1',
        'VC_Fund': '#96CEB4',
        'Angel_Syndicate': '#FECA57',
        'Institution': '#FF9FF3',
        'Corporate': '#54A0FF'
    }
    
    # Create nodes
    nodes = []
    node_positions = {}
    
    for node_data in graph_data['nodes']:
        node_id = str(node_data['id'])
        node_label = node_data['label']
        node_name = node_data.get('name', f'{node_label}_{node_id}')
        
        # Add to NetworkX for layout
        G.add_node(node_id, label=node_label, name=node_name)
        
        # Create streamlit-agraph Node
        color = node_colors.get(node_label, '#95A5A6')
        size = 20 if node_label == 'Startup' else 15
        
        display_label = node_name if show_labels else ""
        
        nodes.append(Node(
            id=node_id,
            label=display_label,
            size=size,
            color=color,
            title=f"{node_label}: {node_name}"  # Tooltip
        ))
    
    # Create edges
    edges = []
    for rel_data in graph_data['relationships']:
        source_id = str(rel_data['source'])
        target_id = str(rel_data['target'])
        rel_type = rel_data['type']
        
        # Add to NetworkX
        if G.has_node(source_id) and G.has_node(target_id):
            G.add_edge(source_id, target_id, type=rel_type)
            
            # Edge colors by relationship type
            edge_colors = {
                'FOUNDED': '#E74C3C',
                'WORKS_AT': '#3498DB',
                'INVESTS_IN': '#2ECC71',
                'ANGEL_INVESTS_IN': '#F39C12',
                'MANAGES': '#9B59B6',
                'PARTICIPATED_IN': '#1ABC9C',
                'ACCELERATED_BY': '#E67E22',
                'ACQUIRED': '#34495E',
                'PARTNERS_WITH': '#16A085',
                'MENTORS': '#8E44AD',
                'SPUN_OFF_FROM': '#D35400'
            }
            
            edge_color = edge_colors.get(rel_type, '#95A5A6')
            
            edges.append(Edge(
                source=source_id,
                target=target_id,
                color=edge_color,
                label=rel_type if len(rel_type) < 15 else rel_type[:12] + "...",
                title=f"Relationship: {rel_type}"
            ))
    
    # Calculate layout
    if len(G.nodes()) > 0:
        if layout_type == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(G)
        elif layout_type == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:  # random
            pos = nx.random_layout(G)
        
        # Apply positions to nodes
        for node in nodes:
            if node.id in pos:
                # Scale positions for better visibility
                x, y = pos[node.id]
                node.x = x * 500
                node.y = y * 500
    
    # Graph configuration
    config = Config(
        width=800,
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7DC6F",
        collapsible=False,
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label'}
    )
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nodes", len(nodes))
    with col2:
        st.metric("Relationships", len(edges))
    with col3:
        st.metric("Node Types", len(set(node['label'] for node in graph_data['nodes'])))
    with col4:
        st.metric("Relationship Types", len(set(rel['type'] for rel in graph_data['relationships'])))
    
    # Display the graph
    if nodes:
        return_value = agraph(nodes=nodes, edges=edges, config=config)
        
        # Show selected node info
        if return_value:
            st.subheader("Selected Node Information")
            selected_nodes = return_value.get('nodes', [])
            if selected_nodes:
                selected_node_id = selected_nodes[0]
                # Find the selected node data
                for node_data in graph_data['nodes']:
                    if str(node_data['id']) == selected_node_id:
                        st.json(node_data['properties'])
                        break
    else:
        st.error("No nodes to display")
    
    # Legend
    st.subheader("🎨 Legend")
    
    # Node types legend
    st.markdown("**Node Types:**")
    legend_cols = st.columns(4)
    node_types = list(node_colors.keys())
    
    for i, (node_type, color) in enumerate(node_colors.items()):
        col_idx = i % 4
        with legend_cols[col_idx]:
            st.markdown(f"🔵 **{node_type}**", help=f"Color: {color}")
    
    # Relationship types legend
    st.markdown("**Relationship Types:**")
    rel_types = set(rel['type'] for rel in graph_data['relationships'])
    if rel_types:
        rel_text = ", ".join(sorted(rel_types))
        st.markdown(f"Relations: {rel_text}")

def show_csv_import():
    """Show CSV import interface"""
    st.header("📤 CSV Import")
    st.markdown("Import entities and relationships from CSV files")
    
    # Initialize CSV importer
    if 'csv_importer' not in st.session_state:
        st.session_state.csv_importer = CSVImporter(st.session_state.repo)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Import Data", "📝 Templates", "📚 Documentation"])
    
    with tab1:
        # Import type selection
        import_type = st.radio("What do you want to import?", 
                             ["Entities", "Relationships"])
        
        if import_type == "Entities":
            show_entity_import()
        else:
            show_relationship_import()
    
    with tab2:
        show_csv_templates()
    
    with tab3:
        show_import_documentation()

def show_entity_import():
    """Show entity import interface"""
    st.subheader("📊 Import Entities")
    
    # Entity type selection
    entity_type = st.selectbox("Select entity type:", 
                              ["Person", "Startup", "VC_Firm", "VC_Fund", 
                               "Angel_Syndicate", "Institution", "Corporate"])
    
    # File upload
    uploaded_file = st.file_uploader(
        f"Upload {entity_type} CSV file:",
        type=['csv'],
        help=f"Upload a CSV file containing {entity_type} data. Supports both comma (,) and semicolon (;) separators."
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV with automatic separator detection
            importer = st.session_state.csv_importer
            df = importer.read_csv_file(uploaded_file)
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Empty Rows", df.isnull().all(axis=1).sum())
            
            # Validation
            importer = st.session_state.csv_importer
            validation_errors = importer.validate_csv_structure(df, entity_type)
            
            if validation_errors:
                st.error("❌ Validation Errors:")
                for error in validation_errors:
                    st.write(f"• {error}")
            else:
                st.success("✅ CSV structure is valid!")
                
                # Import options
                st.subheader("⚙️ Import Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    skip_duplicates = st.checkbox("Skip duplicate names", value=True)
                    show_progress = st.checkbox("Show detailed progress", value=True)
                
                with col2:
                    batch_size = st.number_input("Batch size:", min_value=1, max_value=1000, value=100)
                
                # Import button
                if st.button(f"🚀 Import {len(df)} {entity_type}s", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Perform import
                    with st.spinner(f"Importing {entity_type}s..."):
                        results = importer.import_entities(df, entity_type)
                    
                    # Show results
                    st.subheader("📊 Import Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Processed", results['total'])
                    with col2:
                        st.metric("Successful", results['successful'])
                    with col3:
                        st.metric("Failed", results['failed'])
                    
                    # Show errors if any
                    if results['errors']:
                        st.subheader("❌ Errors")
                        for error in results['errors'][:20]:  # Show first 20 errors
                            st.write(f"• {error}")
                        
                        if len(results['errors']) > 20:
                            st.write(f"... and {len(results['errors']) - 20} more errors")
                    
                    # Success message
                    if results['successful'] > 0:
                        st.success(f"✅ Successfully imported {results['successful']} {entity_type}s!")
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {e}")

def show_relationship_import():
    """Show relationship import interface"""
    st.subheader("🔗 Import Relationships")
    
    # Relationship type selection
    relationship_type = st.selectbox("Select relationship type:", 
                                   ["AUTO_DETECT", "FOUNDED", "WORKS_AT", "ANGEL_INVESTS_IN", "MANAGES", 
                                    "INVESTS_IN", "PARTICIPATED_IN", "ACCELERATED_BY", 
                                    "ACQUIRED", "PARTNERS_WITH", "MENTORS", "SPUN_OFF_FROM"])
    
    # File upload
    uploaded_file = st.file_uploader(
        f"Upload {relationship_type} CSV file:",
        type=['csv'],
        help=f"Upload a CSV file containing {relationship_type} relationships. Supports both comma (,) and semicolon (;) separators."
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV with automatic separator detection
            importer = st.session_state.csv_importer
            df = importer.read_csv_file(uploaded_file)
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Empty Rows", df.isnull().all(axis=1).sum())
            
            # Validation
            importer = st.session_state.csv_importer
            validation_errors = importer.validate_relationship_csv(df, relationship_type)
            
            if validation_errors:
                st.error("❌ Validation Errors:")
                for error in validation_errors:
                    st.write(f"• {error}")
            else:
                st.success("✅ CSV structure is valid!")
                
                # Import button
                if st.button(f"🚀 Import {len(df)} {relationship_type} relationships", type="primary"):
                    # Perform import
                    with st.spinner(f"Importing {relationship_type} relationships..."):
                        results = importer.import_relationships(df, relationship_type)
                    
                    # Show results
                    st.subheader("📊 Import Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Processed", results['total'])
                    with col2:
                        st.metric("Successful", results['successful'])
                    with col3:
                        st.metric("Failed", results['failed'])
                    
                    # Show errors if any
                    if results['errors']:
                        st.subheader("❌ Errors")
                        for error in results['errors'][:20]:  # Show first 20 errors
                            st.write(f"• {error}")
                        
                        if len(results['errors']) > 20:
                            st.write(f"... and {len(results['errors']) - 20} more errors")
                    
                    # Success message
                    if results['successful'] > 0:
                        st.success(f"✅ Successfully imported {results['successful']} {relationship_type} relationships!")
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {e}")

def show_csv_templates():
    """Show CSV templates for download"""
    st.subheader("📝 CSV Templates")
    st.markdown("Download CSV templates with the correct column structure")
    
    # Template type selection
    template_type = st.radio("Template type:", ["Entities", "Relationships"])
    
    if template_type == "Entities":
        st.markdown("### Entity Templates")
        
        entity_types = ["Person", "Startup", "VC_Firm", "VC_Fund", 
                       "Angel_Syndicate", "Institution", "Corporate"]
        
        for entity_type in entity_types:
            with st.expander(f"{entity_type} Template"):
                importer = st.session_state.csv_importer
                columns = importer.get_template_columns('entity', entity_type)
                
                if columns:
                    # Create sample CSV
                    sample_df = pd.DataFrame(columns=columns)
                    sample_df.loc[0] = [''] * len(columns)  # Add empty row
                    
                    st.dataframe(sample_df, use_container_width=True)
                    
                    # Download button
                    csv = sample_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {entity_type} Template",
                        data=csv,
                        file_name=f"{entity_type.lower()}_template.csv",
                        mime="text/csv"
                    )
    
    else:
        st.markdown("### Relationship Templates")
        
        relationship_types = ["FOUNDED", "WORKS_AT", "ANGEL_INVESTS_IN", "MANAGES", 
                             "INVESTS_IN", "PARTICIPATED_IN", "ACCELERATED_BY", 
                             "ACQUIRED", "PARTNERS_WITH", "MENTORS", "SPUN_OFF_FROM"]
        
        for rel_type in relationship_types:
            with st.expander(f"{rel_type} Template"):
                importer = st.session_state.csv_importer
                columns = importer.get_template_columns('relationship', rel_type)
                
                if columns:
                    # Create sample CSV
                    sample_df = pd.DataFrame(columns=columns)
                    sample_df.loc[0] = [''] * len(columns)  # Add empty row
                    
                    st.dataframe(sample_df, use_container_width=True)
                    
                    # Download button
                    csv = sample_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {rel_type} Template",
                        data=csv,
                        file_name=f"{rel_type.lower()}_template.csv",
                        mime="text/csv"
                    )

def show_import_documentation():
    """Show import documentation"""
    st.subheader("📚 CSV Import Documentation")
    
    st.markdown("""
    ### How to Use CSV Import
    
    1. **Choose Import Type**: Select whether you want to import entities or relationships
    2. **Select Type**: Choose the specific entity or relationship type
    3. **Download Template**: Use the Templates tab to get the correct CSV format
    4. **Prepare Data**: Fill in your CSV file with the data
    5. **Upload and Import**: Upload your file and click import
    
    ### Data Format Guidelines
    
    #### CSV Separators
    - **Automatic Detection**: The system automatically detects whether your CSV uses comma (`,`) or semicolon (`;`) separators
    - **Comma separated**: Standard international format `name,type,location`
    - **Semicolon separated**: European format `name;type;location`
    - **Mixed files**: Choose one separator consistently throughout the file
    
    #### Dates
    - Supported formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`
    - Examples: `2024-06-15`, `15/06/2024`, `06/15/2024`
    
    #### Boolean Values
    - Supported formats: `true/false`, `1/0`, `yes/no`, `si/no`
    - Examples: `true`, `1`, `yes`, `si`
    
    #### Numbers
    - Use decimal point (not comma): `1000.50`
    - Currency amounts in euros: `5000000` for 5M€
    
    #### Required Fields
    - **All entities**: `name` (must be unique)
    - **Relationships**: Depend on type, see templates
    
    ### Tips for Success
    
    - **Clean Data**: Remove empty rows and ensure consistent formatting
    - **Unique Names**: Entity names should be unique within their type
    - **Existing Entities**: For relationships, referenced entities must already exist
    - **Batch Size**: Large files can be processed in batches
    - **Error Handling**: Review error messages and fix data accordingly
    
    ### Common Errors
    
    - **Missing Required Columns**: Download the correct template
    - **Invalid Dates**: Use supported date formats
    - **Referenced Entity Not Found**: Import entities before relationships
    - **Duplicate Names**: Each entity name must be unique
    """)

def show_c14_scraper():
    """C14.so scraper interface"""
    st.header("🕷️ C14.so Startup Database Scraper")
    
    st.markdown("""
    ### Scrape Italian Startups from C14.so
    
    C14.so è un database open-source di startup italiane. Questo strumento ti permette di:
    - Estrarre automaticamente dati delle startup italiane
    - Convertire i dati nel formato compatibile con il nostro sistema
    - Importare direttamente nel knowledge graph
    """)
    
    with st.expander("⚙️ Configurazione Scraping"):
        col1, col2 = st.columns(2)
        
        with col1:
            max_pages = st.number_input(
                "Massimo numero di pagine",
                min_value=1,
                max_value=20,
                value=3,
                help="Ogni pagina contiene ~25 startup"
            )
            
            delay = st.slider(
                "Delay tra richieste (secondi)",
                min_value=0.5,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="Rate limiting per essere rispettosi del server"
            )
        
        with col2:
            max_startups = st.number_input(
                "Massimo numero di startup",
                min_value=1,
                max_value=500,
                value=50,
                help="Limita il numero totale di startup da scrapare"
            )
            
            output_filename = st.text_input(
                "Nome file output",
                value="c14_startups_scraped.csv",
                help="Nome del file CSV di output"
            )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Avvia Scraping", type="primary"):
            try:
                from app.c14_scraper import C14Scraper
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Inizializzazione scraper...")
                scraper = C14Scraper(delay=delay)
                
                status_text.text("Recupero lista startup...")
                progress_bar.progress(10)
                
                with st.spinner("Scraping in corso... Questo potrebbe richiedere alcuni minuti."):
                    startups = scraper.scrape_all_startups(
                        max_pages=max_pages,
                        max_startups=max_startups
                    )
                
                progress_bar.progress(80)
                status_text.text("Salvataggio dati...")
                
                if startups:
                    filename = scraper.save_to_csv(startups, output_filename)
                    progress_bar.progress(100)
                    status_text.text("✅ Scraping completato!")
                    
                    st.success(f"🎉 Scraped con successo {len(startups)} startup!")
                    
                    # Show preview
                    st.subheader("📋 Preview dei dati")
                    df = pd.read_csv(filename)
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Download button
                    with open(filename, 'rb') as file:
                        st.download_button(
                            label="📥 Scarica CSV",
                            data=file.read(),
                            file_name=filename,
                            mime="text/csv"
                        )
                    
                    # Import option
                    st.subheader("📤 Importa nel Database")
                    if st.button("Importa startup nel Neo4j", type="secondary"):
                        importer = CSVImporter(st.session_state.repo)
                        
                        with st.spinner("Importazione in corso..."):
                            results = importer.import_entities(df, 'Startup')
                        
                        # Show results
                        if results['successful'] > 0:
                            st.success(f"✅ Importate {results['successful']} startup su {results['total']}")
                        
                        if results['failed'] > 0:
                            st.warning(f"⚠️ {results['failed']} import falliti")
                            
                        if results['errors']:
                            with st.expander("Errori di importazione"):
                                for error in results['errors'][:10]:  # Show first 10 errors
                                    st.error(error)
                
                else:
                    st.error("❌ Nessuna startup trovata. Verifica la configurazione.")
                    
            except ImportError:
                st.error("❌ Modulo scraper non trovato. Installa le dipendenze necessarie.")
            except Exception as e:
                st.error(f"❌ Errore durante lo scraping: {str(e)}")
    
    with col2:
        if st.button("📊 Test Connessione C14"):
            try:
                import requests
                response = requests.get("https://www.c14.so", timeout=10)
                if response.status_code == 200:
                    st.success("✅ C14.so è raggiungibile")
                else:
                    st.warning(f"⚠️ C14.so risponde con status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Errore di connessione: {str(e)}")
    
    with col3:
        if st.button("📖 Visualizza Template"):
            # Show template structure
            st.subheader("📋 Template CSV Output")
            template_data = {
                'name': ['Esempio Startup', 'Another Company'],
                'description': ['Descrizione della startup', 'Altra descrizione'],
                'website': ['https://example.com', 'https://another.com'],
                'founded_year': [2020, 2019],
                'stage': ['Seed', 'Series A'],
                'sector': ['FinTech', 'HealthTech'],
                'headquarters': ['Milano, Italy', 'Roma, Italy'],
                'employee_count': [10, 25],
                'status': ['active', 'active']
            }
            st.dataframe(pd.DataFrame(template_data), use_container_width=True)
    
    st.markdown("""
    ### ℹ️ Informazioni
    
    **Cosa viene estratto:**
    - Nome e descrizione della startup
    - Sito web e profilo LinkedIn
    - Informazioni di base (location, anno fondazione, team size)
    - Settore di attività
    - Stato di finanziamento
    - Team members (quando disponibili)
    - Investitori (quando disponibili)
    
    **Note:**
    - I dati vengono estratti rispettando i rate limits del server
    - Alcuni campi potrebbero essere vuoti se non disponibili su C14
    - Il processo può richiedere diversi minuti per grandi quantità di dati
    - I dati vengono salvati in formato CSV compatibile con il nostro sistema di import
    """)

if __name__ == "__main__":
    main()
