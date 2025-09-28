import os
from typing import Optional, Dict, List, Any
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver: Optional[Driver] = None
        
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query and return results"""
        if not self.driver:
            raise Exception("Not connected to database")
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

class Neo4jRepository:
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    # --- ENTITY CREATION METHODS ---
    
    def create_person(self, person_data: Dict) -> bool:
        """Create a Person node (uses MERGE to avoid duplicates by name and surname)"""
        query = """
        MERGE (p:Person {name: $name, surname: $surname})
        ON CREATE SET 
            p.id = randomUUID(),
            p.role_type = $role_type,
            p.linkedin_url = $linkedin_url,
            p.twitter_handle = $twitter_handle,
            p.biography = $biography,
            p.location = $location,
            p.birth_year = $birth_year,
            p.education = $education,
            p.previous_experience = $previous_experience,
            p.specialization = $specialization,
            p.reputation_score = $reputation_score,
            p.created_at = datetime(),
            p.updated_at = datetime()
        ON MATCH SET
            p.role_type = $role_type,
            p.linkedin_url = $linkedin_url,
            p.twitter_handle = $twitter_handle,
            p.biography = $biography,
            p.location = $location,
            p.birth_year = $birth_year,
            p.education = $education,
            p.previous_experience = $previous_experience,
            p.specialization = $specialization,
            p.reputation_score = $reputation_score,
            p.updated_at = datetime()
        RETURN p.id as id
        """
        try:
            result = self.connection.execute_query(query, person_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create person: {e}")
            return False
    
    def create_startup(self, startup_data: Dict) -> bool:
        """Create a Startup node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (s:Startup {name: $name})
        ON CREATE SET 
            s.id = randomUUID(),
            s.description = $description,
            s.website = $website,
            s.founded_year = $founded_year,
            s.stage = $stage,
            s.sector = $sector,
            s.business_model = $business_model,
            s.headquarters = $headquarters,
            s.employee_count = $employee_count,
            s.status = $status,
            s.total_funding = $total_funding,
            s.last_funding_date = date($last_funding_date),
            s.exit_date = date($exit_date),
            s.exit_value = $exit_value,
            s.created_at = datetime(),
            s.updated_at = datetime()
        ON MATCH SET
            s.description = $description,
            s.website = $website,
            s.founded_year = $founded_year,
            s.stage = $stage,
            s.sector = $sector,
            s.business_model = $business_model,
            s.headquarters = $headquarters,
            s.employee_count = $employee_count,
            s.status = $status,
            s.total_funding = $total_funding,
            s.last_funding_date = CASE WHEN $last_funding_date IS NOT NULL THEN date($last_funding_date) ELSE s.last_funding_date END,
            s.exit_date = CASE WHEN $exit_date IS NOT NULL THEN date($exit_date) ELSE s.exit_date END,
            s.exit_value = $exit_value,
            s.updated_at = datetime()
        RETURN s.id as id
        """
        try:
            # Convert date strings to Neo4j date format
            if startup_data.get('last_funding_date'):
                startup_data['last_funding_date'] = str(startup_data['last_funding_date'])
            if startup_data.get('exit_date'):
                startup_data['exit_date'] = str(startup_data['exit_date'])
                
            result = self.connection.execute_query(query, startup_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create startup: {e}")
            return False
    
    def create_vc_firm(self, firm_data: Dict) -> bool:
        """Create a VC_Firm node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (f:VC_Firm {name: $name})
        ON CREATE SET 
            f.id = randomUUID(),
            f.description = $description,
            f.website = $website,
            f.founded_year = $founded_year,
            f.headquarters = $headquarters,
            f.type = $type,
            f.investment_focus = $investment_focus,
            f.stage_focus = $stage_focus,
            f.geographic_focus = $geographic_focus,
            f.team_size = $team_size,
            f.assets_under_management = $assets_under_management,
            f.portfolio_companies_count = $portfolio_companies_count,
            f.created_at = datetime(),
            f.updated_at = datetime()
        ON MATCH SET
            f.description = $description,
            f.website = $website,
            f.founded_year = $founded_year,
            f.headquarters = $headquarters,
            f.type = $type,
            f.investment_focus = $investment_focus,
            f.stage_focus = $stage_focus,
            f.geographic_focus = $geographic_focus,
            f.team_size = $team_size,
            f.assets_under_management = $assets_under_management,
            f.portfolio_companies_count = $portfolio_companies_count,
            f.updated_at = datetime()
        RETURN f.id as id
        """
        try:
            result = self.connection.execute_query(query, firm_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create VC firm: {e}")
            return False
    
    def create_vc_fund(self, fund_data: Dict) -> bool:
        """Create a VC_Fund node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (f:VC_Fund {name: $name})
        ON CREATE SET 
            f.id = randomUUID(),
            f.fund_size = $fund_size,
            f.vintage_year = $vintage_year,
            f.fund_number = $fund_number,
            f.status = $status,
            f.target_sectors = $target_sectors,
            f.target_stages = $target_stages,
            f.geographic_focus = $geographic_focus,
            f.first_close_date = date($first_close_date),
            f.final_close_date = date($final_close_date),
            f.investment_period = $investment_period,
            f.fund_life = $fund_life,
            f.deployed_capital = $deployed_capital,
            f.created_at = datetime(),
            f.updated_at = datetime()
        ON MATCH SET
            f.fund_size = $fund_size,
            f.vintage_year = $vintage_year,
            f.fund_number = $fund_number,
            f.status = $status,
            f.target_sectors = $target_sectors,
            f.target_stages = $target_stages,
            f.geographic_focus = $geographic_focus,
            f.first_close_date = CASE WHEN $first_close_date IS NOT NULL THEN date($first_close_date) ELSE f.first_close_date END,
            f.final_close_date = CASE WHEN $final_close_date IS NOT NULL THEN date($final_close_date) ELSE f.final_close_date END,
            f.investment_period = $investment_period,
            f.fund_life = $fund_life,
            f.deployed_capital = $deployed_capital,
            f.updated_at = datetime()
        RETURN f.id as id
        """
        try:
            # Convert date strings to Neo4j date format
            if fund_data.get('first_close_date'):
                fund_data['first_close_date'] = str(fund_data['first_close_date'])
            if fund_data.get('final_close_date'):
                fund_data['final_close_date'] = str(fund_data['final_close_date'])
                
            result = self.connection.execute_query(query, fund_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create VC fund: {e}")
            return False
    
    def create_angel_syndicate(self, syndicate_data: Dict) -> bool:
        """Create an Angel_Syndicate node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (a:Angel_Syndicate {name: $name})
        ON CREATE SET 
            a.id = randomUUID(),
            a.type = $type,
            a.description = $description,
            a.website = $website,
            a.founded_year = $founded_year,
            a.headquarters = $headquarters,
            a.members_count = $members_count,
            a.investment_focus = $investment_focus,
            a.stage_focus = $stage_focus,
            a.ticket_size_min = $ticket_size_min,
            a.ticket_size_max = $ticket_size_max,
            a.total_investments = $total_investments,
            a.created_at = datetime(),
            a.updated_at = datetime()
        ON MATCH SET
            a.type = $type,
            a.description = $description,
            a.website = $website,
            a.founded_year = $founded_year,
            a.headquarters = $headquarters,
            a.members_count = $members_count,
            a.investment_focus = $investment_focus,
            a.stage_focus = $stage_focus,
            a.ticket_size_min = $ticket_size_min,
            a.ticket_size_max = $ticket_size_max,
            a.total_investments = $total_investments,
            a.updated_at = datetime()
        RETURN a.id as id
        """
        try:
            result = self.connection.execute_query(query, syndicate_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create angel syndicate: {e}")
            return False
    
    def create_institution(self, institution_data: Dict) -> bool:
        """Create an Institution node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (i:Institution {name: $name})
        ON CREATE SET 
            i.id = randomUUID(),
            i.type = $type,
            i.description = $description,
            i.website = $website,
            i.founded_year = $founded_year,
            i.headquarters = $headquarters,
            i.program_duration = $program_duration,
            i.batch_size = $batch_size,
            i.sectors_focus = $sectors_focus,
            i.equity_taken = $equity_taken,
            i.funding_provided = $funding_provided,
            i.portfolio_companies_count = $portfolio_companies_count,
            i.success_rate = $success_rate,
            i.created_at = datetime(),
            i.updated_at = datetime()
        ON MATCH SET
            i.type = $type,
            i.description = $description,
            i.website = $website,
            i.founded_year = $founded_year,
            i.headquarters = $headquarters,
            i.program_duration = $program_duration,
            i.batch_size = $batch_size,
            i.sectors_focus = $sectors_focus,
            i.equity_taken = $equity_taken,
            i.funding_provided = $funding_provided,
            i.portfolio_companies_count = $portfolio_companies_count,
            i.success_rate = $success_rate,
            i.updated_at = datetime()
        RETURN i.id as id
        """
        try:
            result = self.connection.execute_query(query, institution_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create institution: {e}")
            return False
    
    def create_corporate(self, corporate_data: Dict) -> bool:
        """Create a Corporate node (uses MERGE to avoid duplicates by name)"""
        query = """
        MERGE (c:Corporate {name: $name})
        ON CREATE SET 
            c.id = randomUUID(),
            c.description = $description,
            c.website = $website,
            c.founded_year = $founded_year,
            c.headquarters = $headquarters,
            c.sector = $sector,
            c.size = $size,
            c.revenue = $revenue,
            c.employee_count = $employee_count,
            c.stock_exchange = $stock_exchange,
            c.ticker = $ticker,
            c.has_cvc_arm = $has_cvc_arm,
            c.innovation_programs = $innovation_programs,
            c.created_at = datetime(),
            c.updated_at = datetime()
        ON MATCH SET
            c.description = $description,
            c.website = $website,
            c.industry = $industry,
            c.founded_year = $founded_year,
            c.headquarters = $headquarters,
            c.revenue = $revenue,
            c.employee_count = $employee_count,
            c.stock_exchange = $stock_exchange,
            c.ticker = $ticker,
            c.has_cvc_arm = $has_cvc_arm,
            c.innovation_programs = $innovation_programs,
            c.updated_at = datetime()
        RETURN c.id as id
        """
        try:
            result = self.connection.execute_query(query, corporate_data)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create corporate: {e}")
            return False
    
    # --- RELATIONSHIP CREATION METHODS ---
    
    def create_investment_relationship(self, investor_name: str, investor_type: str, 
                                     startup_name: str, investment_data: Dict) -> bool:
        """Create INVESTS_IN relationship (uses MERGE to avoid duplicates by investor+startup)"""
        try:
            # Create basic relationship first
            query = f"""
            MATCH (investor:{investor_type} {{name: $investor_name}})
            MATCH (startup:Startup {{name: $startup_name}})
            MERGE (investor)-[r:INVESTS_IN]->(startup)
            RETURN r
            """
            
            params = {
                'investor_name': investor_name,
                'startup_name': startup_name
            }
            
            # Execute the basic merge
            result = self.connection.execute_query(query, params)
            
            if len(result) > 0:
                # Now update properties only for non-null values
                update_parts = []
                update_params = {
                    'investor_name': investor_name,
                    'startup_name': startup_name
                }
                
                for key, value in investment_data.items():
                    if value is not None:
                        if key == 'round_date':
                            update_parts.append(f"r.{key} = date($_{key})")
                            update_params[f'_{key}'] = str(value)
                        else:
                            update_parts.append(f"r.{key} = $_{key}")
                            update_params[f'_{key}'] = value
                
                if update_parts:
                    update_query = f"""
                    MATCH (investor:{investor_type} {{name: $investor_name}})
                    MATCH (startup:Startup {{name: $startup_name}})
                    MATCH (investor)-[r:INVESTS_IN]->(startup)
                    SET {', '.join(update_parts)}
                    RETURN r
                    """
                    self.connection.execute_query(update_query, update_params)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create investment relationship: {e}")
            return False
    
    def create_angel_investment_relationship(self, person_name: str, startup_name: str, 
                                           investment_data: Dict) -> bool:
        """Create ANGEL_INVESTS_IN relationship (uses MERGE to avoid duplicates by person+startup+date)"""
        
        query = """
        MATCH (person:Person {name: $first_name, surname: $last_name})
        MATCH (startup:Startup {name: $startup_name})
        MERGE (person)-[r:ANGEL_INVESTS_IN {
            investment_date: date($investment_date),
            round_stage: $round_stage
        }]->(startup)
        ON CREATE SET
            r.amount = $amount,
            r.lead_investor = $lead_investor,
            r.board_seat = $board_seat
        ON MATCH SET
            r.amount = $amount,
            r.lead_investor = $lead_investor,
            r.board_seat = $board_seat
        RETURN r
        """
        try:
            params = {
                'first_name': first_name,
                'last_name': last_name,
                'startup_name': startup_name,
                'investment_date': investment_data['investment_date'].isoformat(),
                'round_stage': investment_data['round_stage'],
                'amount': investment_data['amount'],
                'lead_investor': investment_data['lead_investor'],
                'board_seat': investment_data['board_seat']
            }
            result = self.connection.execute_query(query, params)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create angel investment relationship: {e}")
            return False
    
    def create_employment_relationship(self, person_name: str, org_name: str, 
                                     org_type: str, employment_data: Dict) -> bool:
        """Create WORKS_AT relationship (uses MERGE to avoid duplicates by person+org+role+start_date)"""
        query = f"""
        MATCH (person:Person {{name: $person_name}})
        MATCH (org:{org_type} {{name: $org_name}})
        MERGE (person)-[r:WORKS_AT {{
            role: $role,
            start_date: date($start_date)
        }}]->(org)
        ON CREATE SET
            r.end_date = date($end_date),
            r.seniority_level = $seniority_level,
            r.is_current = $is_current
        ON MATCH SET
            r.end_date = date($end_date),
            r.seniority_level = $seniority_level,
            r.is_current = $is_current
        RETURN r
        """
        try:
            params = {
                'person_name': person_name,
                'org_name': org_name,
                'start_date': str(employment_data['start_date']),
                'end_date': str(employment_data['end_date']) if employment_data.get('end_date') else None,
                **employment_data
            }
            result = self.connection.execute_query(query, params)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create employment relationship: {e}")
            return False
    
    def create_fund_management_relationship(self, firm_name: str, fund_name: str, 
                                          management_data: Dict) -> bool:
        """Create MANAGES relationship (uses MERGE to avoid duplicates by firm+fund)"""
        query = """
        MATCH (firm:VC_Firm {name: $firm_name})
        MATCH (fund:VC_Fund {name: $fund_name})
        MERGE (firm)-[r:MANAGES]->(fund)
        ON CREATE SET
            r.management_fee = $management_fee,
            r.carried_interest = $carried_interest,
            r.start_date = date($start_date)
        ON MATCH SET
            r.management_fee = $management_fee,
            r.carried_interest = $carried_interest,
            r.start_date = date($start_date)
        RETURN r
        """
        try:
            params = {
                'firm_name': firm_name,
                'fund_name': fund_name,
                'start_date': str(management_data['start_date']),
                **management_data
            }
            result = self.connection.execute_query(query, params)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create fund management relationship: {e}")
            return False
    
    def create_founded_relationship(self, person_name: str, person_surname: str, startup_name: str, 
                                  founding_data: Dict) -> bool:
        """Create FOUNDED relationship (uses MERGE to avoid duplicates by person+startup)"""
        first_name = person_name.strip()
        last_name = person_surname.strip()
        
        query = """
        MATCH (person:Person {name: $first_name, surname: $last_name})
        MATCH (startup:Startup {name: $startup_name})
        MERGE (person)-[r:FOUNDED]->(startup)
        ON CREATE SET
            r.role = $role,
            r.founding_date = CASE WHEN $founding_date IS NOT NULL THEN date($founding_date) ELSE null END,
            r.equity_percentage = $equity_percentage,
            r.is_current = $is_current,
            r.exit_date = CASE WHEN $exit_date IS NOT NULL THEN date($exit_date) ELSE null END
        ON MATCH SET
            r.role = $role,
            r.founding_date = CASE WHEN $founding_date IS NOT NULL THEN date($founding_date) ELSE null END,
            r.equity_percentage = $equity_percentage,
            r.is_current = $is_current,
            r.exit_date = CASE WHEN $exit_date IS NOT NULL THEN date($exit_date) ELSE null END
        RETURN r
        """
        try:
            params = {
                'first_name': first_name,
                'last_name': last_name,
                'startup_name': startup_name,
                'founding_date': str(founding_data['founding_date']) if founding_data.get('founding_date') else None,
                'exit_date': str(founding_data['exit_date']) if founding_data.get('exit_date') else None,
                **founding_data
            }
            result = self.connection.execute_query(query, params)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to create founded relationship: {e}")
            return False
    
    # --- UTILITY METHODS ---
    
    def get_all_entities_by_type(self, entity_type: str) -> List[Dict]:
        """Get all entities of a specific type"""
        query = f"MATCH (n:{entity_type}) RETURN n.name as name, n.id as id ORDER BY n.name"
        try:
            return self.connection.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get entities of type {entity_type}: {e}")
            return []
    
    def search_entities(self, entity_type: str, search_term: str) -> List[Dict]:
        """Search entities by name"""
        query = f"""
        MATCH (n:{entity_type}) 
        WHERE toLower(n.name) CONTAINS toLower($search_term)
        RETURN n.name as name, n.id as id 
        ORDER BY n.name
        """
        try:
            return self.connection.execute_query(query, {'search_term': search_term})
        except Exception as e:
            logger.error(f"Failed to search {entity_type}: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get basic database statistics"""
        queries = {
            'persons': "MATCH (n:Person) RETURN count(n) as count",
            'startups': "MATCH (n:Startup) RETURN count(n) as count",
            'vc_firms': "MATCH (n:VC_Firm) RETURN count(n) as count",
            'vc_funds': "MATCH (n:VC_Fund) RETURN count(n) as count",
            'angel_syndicates': "MATCH (n:Angel_Syndicate) RETURN count(n) as count",
            'institutions': "MATCH (n:Institution) RETURN count(n) as count",
            'corporates': "MATCH (n:Corporate) RETURN count(n) as count",
            'relationships': "MATCH ()-[r]-() RETURN count(r) as count"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = self.connection.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            except Exception as e:
                logger.error(f"Failed to get stats for {key}: {e}")
                stats[key] = 0
        
        return stats
    
    def clean_duplicates(self) -> Dict[str, int]:
        """Remove duplicate nodes and relationships - WARNING: Use with caution!"""
        cleanup_queries = {
            'duplicate_persons': """
                MATCH (n:Person)
                WITH n.name as name, collect(n) as nodes
                WHERE size(nodes) > 1
                UNWIND nodes[1..] as duplicate
                DETACH DELETE duplicate
                RETURN count(duplicate) as cleaned
            """,
            'duplicate_startups': """
                MATCH (n:Startup)
                WITH n.name as name, collect(n) as nodes
                WHERE size(nodes) > 1
                UNWIND nodes[1..] as duplicate
                DETACH DELETE duplicate
                RETURN count(duplicate) as cleaned
            """,
            'duplicate_vc_firms': """
                MATCH (n:VC_Firm)
                WITH n.name as name, collect(n) as nodes
                WHERE size(nodes) > 1
                UNWIND nodes[1..] as duplicate
                DETACH DELETE duplicate
                RETURN count(duplicate) as cleaned
            """,
            'duplicate_vc_funds': """
                MATCH (n:VC_Fund)
                WITH n.name as name, collect(n) as nodes
                WHERE size(nodes) > 1
                UNWIND nodes[1..] as duplicate
                DETACH DELETE duplicate
                RETURN count(duplicate) as cleaned
            """
        }
        
        results = {}
        for key, query in cleanup_queries.items():
            try:
                result = self.connection.execute_query(query)
                results[key] = result[0]['cleaned'] if result else 0
                logger.info(f"Cleaned {results[key]} {key}")
            except Exception as e:
                logger.error(f"Failed to clean {key}: {e}")
                results[key] = 0
        
        return results

    def create_lp_participation_relationship(self, investor_name: str, investor_type: str, 
                                           fund_name: str, participation_data: Dict) -> bool:
        """Create PARTICIPATED_IN relationship (Person/Institution/VC_Firm → VC_Fund)"""
        query = f"""
        MATCH (investor:{investor_type} {{name: $investor_name}})
        MATCH (fund:VC_Fund {{name: $fund_name}})
        MERGE (investor)-[r:PARTICIPATED_IN {{
            commitment_date: date($commitment_date)
        }}]->(fund)
        ON CREATE SET
            r.commitment_amount = $commitment_amount,
            r.investor_type = $investor_type
        ON MATCH SET
            r.commitment_amount = $commitment_amount,
            r.investor_type = $investor_type
        RETURN r
        """
        try:
            params = {
                'investor_name': investor_name,
                'fund_name': fund_name,
                'commitment_date': participation_data['commitment_date'].isoformat(),
                'commitment_amount': participation_data['commitment_amount'],
                'investor_type': participation_data['investor_type']
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create LP participation relationship: {e}")
            return False

    def create_acceleration_relationship(self, startup_name: str, institution_name: str, 
                                       acceleration_data: Dict) -> bool:
        """Create ACCELERATED_BY relationship (Startup → Institution)"""
        query = """
        MATCH (startup:Startup {name: $startup_name})
        MATCH (institution:Institution {name: $institution_name})
        MERGE (startup)-[r:ACCELERATED_BY {
            program_name: $program_name,
            start_date: date($start_date)
        }]->(institution)
        ON CREATE SET
            r.batch_name = $batch_name,
            r.end_date = CASE WHEN $end_date IS NOT NULL THEN date($end_date) ELSE NULL END,
            r.equity_taken = $equity_taken,
            r.funding_received = $funding_received,
            r.demo_day_date = CASE WHEN $demo_day_date IS NOT NULL THEN date($demo_day_date) ELSE NULL END
        ON MATCH SET
            r.batch_name = $batch_name,
            r.end_date = CASE WHEN $end_date IS NOT NULL THEN date($end_date) ELSE NULL END,
            r.equity_taken = $equity_taken,
            r.funding_received = $funding_received,
            r.demo_day_date = CASE WHEN $demo_day_date IS NOT NULL THEN date($demo_day_date) ELSE NULL END
        RETURN r
        """
        try:
            params = {
                'startup_name': startup_name,
                'institution_name': institution_name,
                'program_name': acceleration_data['program_name'],
                'start_date': acceleration_data['start_date'].isoformat(),
                'batch_name': acceleration_data.get('batch_name'),
                'end_date': acceleration_data.get('end_date').isoformat() if acceleration_data.get('end_date') else None,
                'equity_taken': acceleration_data.get('equity_taken'),
                'funding_received': acceleration_data.get('funding_received'),
                'demo_day_date': acceleration_data.get('demo_day_date').isoformat() if acceleration_data.get('demo_day_date') else None
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create acceleration relationship: {e}")
            return False

    def create_acquisition_relationship(self, corporate_name: str, startup_name: str, 
                                      acquisition_data: Dict) -> bool:
        """Create ACQUIRED relationship (Corporate → Startup)"""
        query = """
        MATCH (corporate:Corporate {name: $corporate_name})
        MATCH (startup:Startup {name: $startup_name})
        MERGE (corporate)-[r:ACQUIRED {
            acquisition_date: date($acquisition_date)
        }]->(startup)
        ON CREATE SET
            r.acquisition_value = $acquisition_value,
            r.acquisition_type = $acquisition_type,
            r.strategic_rationale = $strategic_rationale,
            r.integration_status = $integration_status
        ON MATCH SET
            r.acquisition_value = $acquisition_value,
            r.acquisition_type = $acquisition_type,
            r.strategic_rationale = $strategic_rationale,
            r.integration_status = $integration_status
        RETURN r
        """
        try:
            params = {
                'corporate_name': corporate_name,
                'startup_name': startup_name,
                'acquisition_date': acquisition_data['acquisition_date'].isoformat(),
                'acquisition_value': acquisition_data.get('acquisition_value'),
                'acquisition_type': acquisition_data['acquisition_type'],
                'strategic_rationale': acquisition_data.get('strategic_rationale'),
                'integration_status': acquisition_data.get('integration_status')
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create acquisition relationship: {e}")
            return False

    def create_partnership_relationship(self, corporate_name: str, partner_name: str, partner_type: str,
                                      partnership_data: Dict) -> bool:
        """Create PARTNERS_WITH relationship (Corporate → VC_Firm/Institution)"""
        query = f"""
        MATCH (corporate:Corporate {{name: $corporate_name}})
        MATCH (partner:{partner_type} {{name: $partner_name}})
        MERGE (corporate)-[r:PARTNERS_WITH {{
            partnership_type: $partnership_type,
            start_date: date($start_date)
        }}]->(partner)
        ON CREATE SET
            r.description = $description,
            r.is_active = $is_active
        ON MATCH SET
            r.description = $description,
            r.is_active = $is_active
        RETURN r
        """
        try:
            params = {
                'corporate_name': corporate_name,
                'partner_name': partner_name,
                'partnership_type': partnership_data['partnership_type'],
                'start_date': partnership_data['start_date'].isoformat(),
                'description': partnership_data.get('description'),
                'is_active': partnership_data.get('is_active', True)
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create partnership relationship: {e}")
            return False

    def create_mentorship_relationship(self, mentor_name: str, mentee_name: str, 
                                     mentorship_data: Dict) -> bool:
        """Create MENTORS relationship (Person → Person)"""
        query = """
        MATCH (mentor:Person {name: $mentor_name})
        MATCH (mentee:Person {name: $mentee_name})
        MERGE (mentor)-[r:MENTORS {
            start_date: date($start_date),
            relationship_type: $relationship_type
        }]->(mentee)
        ON CREATE SET
            r.end_date = CASE WHEN $end_date IS NOT NULL THEN date($end_date) ELSE NULL END,
            r.context = $context
        ON MATCH SET
            r.end_date = CASE WHEN $end_date IS NOT NULL THEN date($end_date) ELSE NULL END,
            r.context = $context
        RETURN r
        """
        try:
            params = {
                'mentor_name': mentor_name,
                'mentee_name': mentee_name,
                'start_date': mentorship_data['start_date'].isoformat(),
                'relationship_type': mentorship_data['relationship_type'],
                'end_date': mentorship_data.get('end_date').isoformat() if mentorship_data.get('end_date') else None,
                'context': mentorship_data.get('context')
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create mentorship relationship: {e}")
            return False

    def create_spinoff_relationship(self, startup_name: str, parent_name: str, parent_type: str,
                                  spinoff_data: Dict) -> bool:
        """Create SPUN_OFF_FROM relationship (Startup → Corporate/Institution)"""
        query = f"""
        MATCH (startup:Startup {{name: $startup_name}})
        MATCH (parent:{parent_type} {{name: $parent_name}})
        MERGE (startup)-[r:SPUN_OFF_FROM {{
            spinoff_date: date($spinoff_date)
        }}]->(parent)
        ON CREATE SET
            r.technology_transferred = $technology_transferred,
            r.initial_equity = $initial_equity,
            r.support_provided = $support_provided
        ON MATCH SET
            r.technology_transferred = $technology_transferred,
            r.initial_equity = $initial_equity,
            r.support_provided = $support_provided
        RETURN r
        """
        try:
            params = {
                'startup_name': startup_name,
                'parent_name': parent_name,
                'spinoff_date': spinoff_data['spinoff_date'].isoformat(),
                'technology_transferred': spinoff_data.get('technology_transferred'),
                'initial_equity': spinoff_data.get('initial_equity'),
                'support_provided': spinoff_data.get('support_provided')
            }
            result = self.connection.execute_query(query, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to create spinoff relationship: {e}")
            return False

    def get_graph_data(self, limit: int = 100) -> Dict[str, Any]:
        """Get graph data for visualization (nodes and relationships)"""
        try:
            # Get nodes with their labels and properties
            nodes_query = f"""
            MATCH (n)
            RETURN id(n) as id, labels(n)[0] as label, n.name as name, 
                   properties(n) as properties
            LIMIT {limit}
            """
            
            # Get relationships
            relationships_query = f"""
            MATCH (a)-[r]->(b)
            WHERE id(a) IN [n IN range(0, {limit}) | n] 
               OR id(b) IN [n IN range(0, {limit}) | n]
            RETURN id(a) as source, id(b) as target, type(r) as type,
                   properties(r) as properties
            LIMIT {limit * 2}
            """
            
            nodes_result = self.connection.execute_query(nodes_query)
            relationships_result = self.connection.execute_query(relationships_query)
            
            return {
                'nodes': nodes_result,
                'relationships': relationships_result
            }
            
        except Exception as e:
            logger.error(f"Failed to get graph data: {e}")
            return {'nodes': [], 'relationships': []}
