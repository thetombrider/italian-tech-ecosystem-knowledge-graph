import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from pathlib import Path
import io

from app.neo4j_repo import Neo4jRepository
from app.models import *

logger = logging.getLogger(__name__)

class CSVImporter:
    """CSV Importer for Italian Tech Ecosystem Graph"""
    
    def __init__(self, repo: Neo4jRepository):
        self.repo = repo
        
        # Entity type mappings
        self.entity_creators = {
            'Person': self.repo.create_person,
            'Startup': self.repo.create_startup,
            'VC_Firm': self.repo.create_vc_firm,
            'VC_Fund': self.repo.create_vc_fund,
            'Angel_Syndicate': self.repo.create_angel_syndicate,
            'Institution': self.repo.create_institution,
            'Corporate': self.repo.create_corporate
        }
        
        # Relationship type mappings
        self.relationship_creators = {
            'FOUNDED': self.repo.create_founded_relationship,
            'WORKS_AT': self.repo.create_employment_relationship,
            'ANGEL_INVESTS_IN': self.repo.create_angel_investment_relationship,
            'MANAGES': self.repo.create_fund_management_relationship,
            'INVESTS_IN': self.repo.create_investment_relationship,
            'PARTICIPATED_IN': self.repo.create_lp_participation_relationship,
            'ACCELERATED_BY': self.repo.create_acceleration_relationship,
            'ACQUIRED': self.repo.create_acquisition_relationship,
            'PARTNERS_WITH': self.repo.create_partnership_relationship,
            'MENTORS': self.repo.create_mentorship_relationship,
            'SPUN_OFF_FROM': self.repo.create_spinoff_relationship
        }
    
    def read_csv_file(self, uploaded_file) -> pd.DataFrame:
        """Read CSV file with automatic separator detection"""
        try:
            # Try to detect separator by reading first few lines
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            # Convert bytes to string if needed
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            # Check first line for separators
            first_line = content.split('\n')[0] if content else ""
            
            # Count occurrences of potential separators
            comma_count = first_line.count(',')
            semicolon_count = first_line.count(';')
            pipe_count = first_line.count('|')
            
            # Determine separator (prioritize pipe for C14 scraped files)
            if pipe_count > 0:
                separator = '|'
            elif semicolon_count > comma_count:
                separator = ';'
            else:
                separator = ','
            
            # Read CSV with detected separator
            uploaded_file.seek(0)  # Reset file pointer again
            df = pd.read_csv(uploaded_file, sep=separator)
            
            logger.info(f"CSV read successfully with separator '{separator}'")
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            # Fallback: try with comma separator
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, sep=',')
    
    def validate_csv_structure(self, df: pd.DataFrame, entity_type: str) -> List[str]:
        """Validate CSV structure for entity type"""
        errors = []
        
        # Required columns by entity type
        required_columns = {
            'Person': ['name'],
            'Startup': ['name'],
            'VC_Firm': ['name'],
            'VC_Fund': ['name'],
            'Angel_Syndicate': ['name'],
            'Institution': ['name'],
            'Corporate': ['name']
        }
        
        if entity_type in required_columns:
            for col in required_columns[entity_type]:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
        
        return errors
    
    def validate_relationship_csv(self, df: pd.DataFrame, relationship_type: str) -> List[str]:
        """Validate CSV structure for relationship type"""
        errors = []
        
        # Required columns by relationship type
        required_columns = {
            'FOUNDED': ['person_name', 'person_surname', 'startup_name', 'founding_date'],
            'WORKS_AT': ['person_name', 'org_name', 'org_type', 'role'],
            'ANGEL_INVESTS_IN': ['person_name', 'startup_name', 'investment_date'],
            'MANAGES': ['firm_name', 'fund_name', 'start_date'],
            'INVESTS_IN': ['investor_name', 'investor_type', 'startup_name'],
            'PARTICIPATED_IN': ['investor_name', 'investor_type', 'fund_name', 'commitment_date'],
            'ACCELERATED_BY': ['startup_name', 'institution_name', 'program_name', 'start_date'],
            'ACQUIRED': ['corporate_name', 'startup_name', 'acquisition_date'],
            'PARTNERS_WITH': ['corporate_name', 'partner_name', 'partner_type', 'start_date'],
            'MENTORS': ['mentor_name', 'mentee_name', 'start_date'],
            'SPUN_OFF_FROM': ['startup_name', 'parent_name', 'parent_type', 'spinoff_date']
        }
        
        if relationship_type in required_columns:
            for col in required_columns[relationship_type]:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
        
        return errors
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for import"""
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', None)
        
        return df
    
    def parse_date(self, date_str: Any) -> Optional[date]:
        """Parse date from various formats"""
        if pd.isna(date_str) or date_str is None:
            return None
        
        try:
            if isinstance(date_str, str):
                date_str = date_str.strip()
                
                # Handle year-only format (e.g., "2017" -> "2017-01-01")
                if date_str.isdigit() and len(date_str) == 4:
                    try:
                        year = int(date_str)
                        return date(year, 1, 1)
                    except ValueError:
                        pass
                
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
            elif isinstance(date_str, (datetime, pd.Timestamp)):
                return date_str.date()
            elif isinstance(date_str, date):
                return date_str
        except Exception as e:
            logger.warning(f"Could not parse date: {date_str} - {e}")
        
        return None
    
    def parse_boolean(self, value: Any) -> bool:
        """Parse boolean from various formats"""
        if pd.isna(value):
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'y', 'si', 'sì']
        
        return bool(value)
    
    def parse_number(self, value: Any, default: float = 0.0) -> float:
        """Parse number from various formats"""
        if pd.isna(value):
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def parse_employee_count(self, value: Any) -> Optional[int]:
        """Parse employee count, handling ranges like '11-50'"""
        if pd.isna(value) or not value:
            return None
        
        value_str = str(value).strip()
        
        # Handle ranges like "11-50"
        if '-' in value_str:
            parts = value_str.split('-')
            try:
                # Return the midpoint of the range
                min_val = int(parts[0].strip())
                max_val = int(parts[1].strip())
                return (min_val + max_val) // 2
            except (ValueError, IndexError):
                pass
        
        # Extract single number
        import re
        number_match = re.search(r'\d+', value_str)
        if number_match:
            try:
                return int(number_match.group())
            except ValueError:
                pass
        
        return None
    
    def import_entities(self, df: pd.DataFrame, entity_type: str) -> Dict[str, Any]:
        """Import entities from DataFrame"""
        results = {
            'total': len(df),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Validate structure
        validation_errors = self.validate_csv_structure(df, entity_type)
        if validation_errors:
            results['errors'].extend(validation_errors)
            return results
        
        # Clean data
        df = self.clean_data(df)
        
        # Get creator function
        creator_func = self.entity_creators.get(entity_type)
        if not creator_func:
            results['errors'].append(f"Unknown entity type: {entity_type}")
            return results
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Prepare entity data based on type
                entity_data = self._prepare_entity_data(row, entity_type)
                
                if entity_data:
                    success = creator_func(entity_data)
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Row {index + 1}: Failed to create {entity_type}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Row {index + 1}: Invalid data")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Row {index + 1}: {str(e)}")
        
        return results
    
    def import_relationships(self, df: pd.DataFrame, relationship_type: str) -> Dict[str, Any]:
        """Import relationships from DataFrame"""
        results = {
            'total': len(df),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Validate structure
        validation_errors = self.validate_relationship_csv(df, relationship_type)
        if validation_errors:
            results['errors'].extend(validation_errors)
            return results
        
        # Clean data
        df = self.clean_data(df)
        
        # Process each row
        for index, row in df.iterrows():
            try:
                success = self._create_relationship(row, relationship_type, index + 1)
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Row {index + 1}: Failed to create {relationship_type}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Row {index + 1}: {str(e)}")
        
        return results
    
    def _prepare_entity_data(self, row: pd.Series, entity_type: str) -> Optional[Dict[str, Any]]:
        """Prepare entity data from CSV row"""
        try:
            if entity_type == 'Person':
                return {
                    'name': row.get('name'),
                    'surname': row.get('surname'),
                    'role_type': row.get('role_type', 'other'),
                    'linkedin_url': row.get('linkedin_url'),
                    'twitter_handle': row.get('twitter_handle'),
                    'biography': row.get('biography'),
                    'location': row.get('location'),
                    'birth_year': self.parse_number(row.get('birth_year')) if row.get('birth_year') else None,
                    'education': row.get('education'),
                    'previous_experience': row.get('previous_experience'),
                    'specialization': row.get('specialization'),
                    'reputation_score': self.parse_number(row.get('reputation_score'), 0)
                }
            
            elif entity_type == 'Startup':
                return {
                    'name': row.get('name'),
                    'description': row.get('description'),
                    'website': row.get('website'),
                    'founded_year': self.parse_number(row.get('founded_year')) if row.get('founded_year') else None,
                    'stage': row.get('stage', 'unknown'),
                    'sector': row.get('sector'),
                    'business_model': row.get('business_model'),
                    'headquarters': row.get('headquarters'),
                    'employee_count': self.parse_employee_count(row.get('employee_count')),
                    'status': row.get('status', 'active'),
                    'total_funding': self.parse_number(row.get('total_funding')) if row.get('total_funding') else None,
                    'last_funding_date': self.parse_date(row.get('last_funding_date')),
                    'exit_date': self.parse_date(row.get('exit_date')),
                    'exit_value': self.parse_number(row.get('exit_value')) if row.get('exit_value') else None
                }
            
            elif entity_type == 'VC_Firm':
                return {
                    'name': row.get('name'),
                    'description': row.get('description'),
                    'website': row.get('website'),
                    'founded_year': self.parse_number(row.get('founded_year')) if row.get('founded_year') else None,
                    'headquarters': row.get('headquarters'),
                    'type': row.get('type', 'independent'),
                    'investment_focus': row.get('investment_focus'),
                    'stage_focus': row.get('stage_focus'),
                    'geographic_focus': row.get('geographic_focus'),
                    'team_size': self.parse_number(row.get('team_size')) if row.get('team_size') else None,
                    'assets_under_management': self.parse_number(row.get('assets_under_management')) if row.get('assets_under_management') else None,
                    'portfolio_companies_count': self.parse_number(row.get('portfolio_companies_count')) if row.get('portfolio_companies_count') else None
                }
            
            elif entity_type == 'VC_Fund':
                return {
                    'name': row.get('name'),
                    'fund_size': self.parse_number(row.get('fund_size')) if row.get('fund_size') else None,
                    'vintage_year': self.parse_number(row.get('vintage_year')) if row.get('vintage_year') else None,
                    'fund_number': row.get('fund_number'),
                    'status': row.get('status', 'unknown'),
                    'target_sectors': row.get('target_sectors'),
                    'target_stages': row.get('target_stages'),
                    'geographic_focus': row.get('geographic_focus'),
                    'first_close_date': self.parse_date(row.get('first_close_date')),
                    'final_close_date': self.parse_date(row.get('final_close_date')),
                    'investment_period': self.parse_number(row.get('investment_period')) if row.get('investment_period') else None,
                    'fund_life': self.parse_number(row.get('fund_life')) if row.get('fund_life') else None,
                    'deployed_capital': self.parse_number(row.get('deployed_capital')) if row.get('deployed_capital') else None
                }
            
            elif entity_type == 'Angel_Syndicate':
                return {
                    'name': row.get('name'),
                    'type': row.get('type', 'angel_syndicate'),
                    'description': row.get('description'),
                    'website': row.get('website'),
                    'founded_year': self.parse_number(row.get('founded_year')) if row.get('founded_year') else None,
                    'headquarters': row.get('headquarters'),
                    'members_count': self.parse_number(row.get('members_count')) if row.get('members_count') else None,
                    'investment_focus': row.get('investment_focus'),
                    'stage_focus': row.get('stage_focus'),
                    'ticket_size_min': self.parse_number(row.get('ticket_size_min')) if row.get('ticket_size_min') else None,
                    'ticket_size_max': self.parse_number(row.get('ticket_size_max')) if row.get('ticket_size_max') else None,
                    'total_investments': self.parse_number(row.get('total_investments')) if row.get('total_investments') else None
                }
            
            elif entity_type == 'Institution':
                return {
                    'name': row.get('name'),
                    'type': row.get('type', 'other'),
                    'description': row.get('description'),
                    'website': row.get('website'),
                    'founded_year': self.parse_number(row.get('founded_year')) if row.get('founded_year') else None,
                    'headquarters': row.get('headquarters'),
                    'program_duration': self.parse_number(row.get('program_duration')) if row.get('program_duration') else None,
                    'batch_size': self.parse_number(row.get('batch_size')) if row.get('batch_size') else None,
                    'sectors_focus': row.get('sectors_focus'),
                    'equity_taken': self.parse_number(row.get('equity_taken')) if row.get('equity_taken') else None,
                    'funding_provided': self.parse_number(row.get('funding_provided')) if row.get('funding_provided') else None,
                    'portfolio_companies_count': self.parse_number(row.get('portfolio_companies_count')) if row.get('portfolio_companies_count') else None,
                    'success_rate': self.parse_number(row.get('success_rate')) if row.get('success_rate') else None
                }
            
            elif entity_type == 'Corporate':
                return {
                    'name': row.get('name'),
                    'description': row.get('description'),
                    'website': row.get('website'),
                    'industry': row.get('industry'),
                    'founded_year': self.parse_number(row.get('founded_year')) if row.get('founded_year') else None,
                    'headquarters': row.get('headquarters'),
                    'revenue': self.parse_number(row.get('revenue')) if row.get('revenue') else None,
                    'employee_count': self.parse_employee_count(row.get('employee_count')),
                    'stock_exchange': row.get('stock_exchange'),
                    'ticker': row.get('ticker'),
                    'has_cvc_arm': self.parse_boolean(row.get('has_cvc_arm')),
                    'innovation_programs': row.get('innovation_programs')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error preparing {entity_type} data: {e}")
            return None
    
    def _create_relationship(self, row: pd.Series, relationship_type: str, row_num: int) -> bool:
        """Create relationship from CSV row"""
        try:
            if relationship_type == 'FOUNDED':
                data = {
                    'role': row.get('role', 'Founder'),
                    'founding_date': self.parse_date(row['founding_date']),
                    'equity_percentage': self.parse_number(row.get('equity_percentage')) if row.get('equity_percentage') else None,
                    'is_current': self.parse_boolean(row.get('is_current', True)),
                    'exit_date': self.parse_date(row.get('exit_date'))
                }
                return self.repo.create_founded_relationship(row['person_name'], row['person_surname'], row['startup_name'], data)
            
            elif relationship_type == 'WORKS_AT':
                data = {
                    'role': row['role'],
                    'start_date': self.parse_date(row.get('start_date')),
                    'end_date': self.parse_date(row.get('end_date')),
                    'seniority_level': row.get('seniority_level'),
                    'is_current': self.parse_boolean(row.get('is_current', True))
                }
                return self.repo.create_employment_relationship(row['person_name'], row['org_name'], row['org_type'], data)
            
            elif relationship_type == 'ANGEL_INVESTS_IN':
                data = {
                    'investment_date': self.parse_date(row['investment_date']),
                    'round_stage': row.get('round_stage', 'unknown'),
                    'amount': self.parse_number(row.get('amount', 0)),
                    'lead_investor': self.parse_boolean(row.get('lead_investor')),
                    'board_seat': self.parse_boolean(row.get('board_seat'))
                }
                return self.repo.create_angel_investment_relationship(row['person_name'], row['startup_name'], data)
            
            elif relationship_type == 'MANAGES':
                data = {
                    'management_fee': self.parse_number(row.get('management_fee')) if row.get('management_fee') else None,
                    'carried_interest': self.parse_number(row.get('carried_interest')) if row.get('carried_interest') else None,
                    'start_date': self.parse_date(row['start_date'])
                }
                return self.repo.create_fund_management_relationship(row['firm_name'], row['fund_name'], data)
            
            elif relationship_type == 'INVESTS_IN':
                data = {}
                
                # Only add properties that have actual values
                if pd.notna(row.get('round_stage')) and str(row.get('round_stage')).strip():
                    data['round_stage'] = str(row.get('round_stage')).strip()
                
                if pd.notna(row.get('round_date')) and str(row.get('round_date')).strip():
                    parsed_date = self.parse_date(row['round_date'])
                    if parsed_date:
                        data['round_date'] = parsed_date
                
                if pd.notna(row.get('amount')) and str(row.get('amount')).strip():
                    parsed_amount = self.parse_number(row.get('amount'))
                    if parsed_amount is not None and parsed_amount > 0:
                        data['amount'] = parsed_amount
                
                if pd.notna(row.get('valuation_pre')) and str(row.get('valuation_pre')).strip():
                    parsed_val = self.parse_number(row.get('valuation_pre'))
                    if parsed_val is not None and parsed_val > 0:
                        data['valuation_pre'] = parsed_val
                
                if pd.notna(row.get('valuation_post')) and str(row.get('valuation_post')).strip():
                    parsed_val = self.parse_number(row.get('valuation_post'))
                    if parsed_val is not None and parsed_val > 0:
                        data['valuation_post'] = parsed_val
                
                if pd.notna(row.get('is_lead_investor')) and str(row.get('is_lead_investor')).strip():
                    data['is_lead_investor'] = self.parse_boolean(row.get('is_lead_investor'))
                
                if pd.notna(row.get('board_seats')) and str(row.get('board_seats')).strip():
                    parsed_seats = self.parse_number(row.get('board_seats'))
                    if parsed_seats is not None and parsed_seats > 0:
                        data['board_seats'] = parsed_seats
                
                if pd.notna(row.get('equity_percentage')) and str(row.get('equity_percentage')).strip():
                    parsed_equity = self.parse_number(row.get('equity_percentage'))
                    if parsed_equity is not None and parsed_equity > 0:
                        data['equity_percentage'] = parsed_equity
                
                return self.repo.create_investment_relationship(row['investor_name'], row['investor_type'], row['startup_name'], data)
            
            elif relationship_type == 'PARTICIPATED_IN':
                data = {
                    'commitment_amount': self.parse_number(row.get('commitment_amount', 0)),
                    'commitment_date': self.parse_date(row['commitment_date']),
                    'investor_type': row.get('lp_category', 'institutional')
                }
                return self.repo.create_lp_participation_relationship(row['investor_name'], row['investor_type'], row['fund_name'], data)
            
            elif relationship_type == 'ACCELERATED_BY':
                data = {
                    'program_name': row['program_name'],
                    'batch_name': row.get('batch_name'),
                    'start_date': self.parse_date(row['start_date']),
                    'end_date': self.parse_date(row.get('end_date')),
                    'equity_taken': self.parse_number(row.get('equity_taken')) if row.get('equity_taken') else None,
                    'funding_received': self.parse_number(row.get('funding_received')) if row.get('funding_received') else None,
                    'demo_day_date': self.parse_date(row.get('demo_day_date'))
                }
                return self.repo.create_acceleration_relationship(row['startup_name'], row['institution_name'], data)
            
            elif relationship_type == 'ACQUIRED':
                data = {
                    'acquisition_date': self.parse_date(row['acquisition_date']),
                    'acquisition_value': self.parse_number(row.get('acquisition_value')) if row.get('acquisition_value') else None,
                    'acquisition_type': row.get('acquisition_type', 'full_acquisition'),
                    'strategic_rationale': row.get('strategic_rationale'),
                    'integration_status': row.get('integration_status')
                }
                return self.repo.create_acquisition_relationship(row['corporate_name'], row['startup_name'], data)
            
            elif relationship_type == 'PARTNERS_WITH':
                data = {
                    'partnership_type': row.get('partnership_type', 'strategic'),
                    'start_date': self.parse_date(row['start_date']),
                    'description': row.get('description'),
                    'is_active': self.parse_boolean(row.get('is_active', True))
                }
                return self.repo.create_partnership_relationship(row['corporate_name'], row['partner_name'], row['partner_type'], data)
            
            elif relationship_type == 'MENTORS':
                data = {
                    'start_date': self.parse_date(row['start_date']),
                    'end_date': self.parse_date(row.get('end_date')),
                    'relationship_type': row.get('relationship_type', 'informal'),
                    'context': row.get('context')
                }
                return self.repo.create_mentorship_relationship(row['mentor_name'], row['mentee_name'], data)
            
            elif relationship_type == 'SPUN_OFF_FROM':
                data = {
                    'spinoff_date': self.parse_date(row['spinoff_date']),
                    'technology_transferred': row.get('technology_transferred'),
                    'initial_equity': self.parse_number(row.get('initial_equity')) if row.get('initial_equity') else None,
                    'support_provided': row.get('support_provided')
                }
                return self.repo.create_spinoff_relationship(row['startup_name'], row['parent_name'], row['parent_type'], data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating {relationship_type} relationship at row {row_num}: {e}")
            return False
    
    def get_template_columns(self, data_type: str, entity_or_relationship: str) -> List[str]:
        """Get template columns for CSV import"""
        if data_type == 'entity':
            templates = {
                'Person': ['name', 'surname', 'role_type', 'linkedin_url', 'twitter_handle', 'biography', 'location', 'birth_year', 'education', 'previous_experience', 'specialization', 'reputation_score'],
                'Startup': ['name', 'description', 'website', 'founded_year', 'stage', 'sector', 'business_model', 'headquarters', 'employee_count', 'status', 'total_funding', 'last_funding_date', 'exit_date', 'exit_value'],
                'VC_Firm': ['name', 'description', 'website', 'founded_year', 'headquarters', 'type', 'investment_focus', 'stage_focus', 'geographic_focus', 'team_size', 'assets_under_management', 'portfolio_companies_count'],
                'VC_Fund': ['name', 'fund_size', 'vintage_year', 'fund_number', 'status', 'target_sectors', 'target_stages', 'geographic_focus', 'first_close_date', 'final_close_date', 'investment_period', 'fund_life', 'deployed_capital'],
                'Angel_Syndicate': ['name', 'type', 'description', 'website', 'founded_year', 'headquarters', 'members_count', 'investment_focus', 'stage_focus', 'ticket_size_min', 'ticket_size_max', 'total_investments'],
                'Institution': ['name', 'type', 'description', 'website', 'founded_year', 'headquarters', 'program_duration', 'batch_size', 'sectors_focus', 'equity_taken', 'funding_provided', 'portfolio_companies_count', 'success_rate'],
                'Corporate': ['name', 'description', 'website', 'industry', 'founded_year', 'headquarters', 'revenue', 'employee_count', 'stock_exchange', 'ticker', 'has_cvc_arm', 'innovation_programs']
            }
            return templates.get(entity_or_relationship, [])
        
        elif data_type == 'relationship':
            templates = {
                'FOUNDED': ['person_name', 'startup_name', 'role', 'founding_date', 'equity_percentage', 'is_current', 'exit_date'],
                'WORKS_AT': ['person_name', 'org_name', 'org_type', 'role', 'start_date', 'end_date', 'seniority_level', 'is_current'],
                'ANGEL_INVESTS_IN': ['person_name', 'startup_name', 'investment_date', 'round_stage', 'amount', 'lead_investor', 'board_seat'],
                'MANAGES': ['firm_name', 'fund_name', 'management_fee', 'carried_interest', 'start_date'],
                'INVESTS_IN': ['investor_name', 'investor_type', 'startup_name', 'round_stage', 'round_date', 'amount', 'valuation_pre', 'valuation_post', 'is_lead_investor', 'board_seats', 'equity_percentage'],
                'PARTICIPATED_IN': ['investor_name', 'investor_type', 'fund_name', 'commitment_amount', 'commitment_date', 'lp_category'],
                'ACCELERATED_BY': ['startup_name', 'institution_name', 'program_name', 'batch_name', 'start_date', 'end_date', 'equity_taken', 'funding_received', 'demo_day_date'],
                'ACQUIRED': ['corporate_name', 'startup_name', 'acquisition_date', 'acquisition_value', 'acquisition_type', 'strategic_rationale', 'integration_status'],
                'PARTNERS_WITH': ['corporate_name', 'partner_name', 'partner_type', 'partnership_type', 'start_date', 'description', 'is_active'],
                'MENTORS': ['mentor_name', 'mentee_name', 'start_date', 'end_date', 'relationship_type', 'context'],
                'SPUN_OFF_FROM': ['startup_name', 'parent_name', 'parent_type', 'spinoff_date', 'technology_transferred', 'initial_equity', 'support_provided']
            }
            return templates.get(entity_or_relationship, [])
        
        return []
