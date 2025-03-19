# app/services/database_service.py
import os
import logging
import json
import traceback
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize the database service with direct Supabase connection"""
        try:
            # Get credentials from environment variables
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing Supabase credentials in environment variables")
            
            # Create a direct connection to Supabase
            self.client = create_client(supabase_url, supabase_key)
            logger.info("✅ Database service initialized with direct Supabase connection")
        except Exception as e:
            error_msg = f"Failed to initialize Supabase client: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ValueError(error_msg)
    
    def get_records(self, table_name, query=None):
        """Get records from a table with optional query"""
        try:
            logger.info(f"Getting records from table: {table_name}")
            db_query = self.client.table(table_name).select("*")
            
            # Apply filters if provided
            if query and isinstance(query, dict):
                for key, value in query.items():
                    db_query = db_query.eq(key, value)
            
            logger.info(f"Executing query on table '{table_name}'")
            response = db_query.execute()
            logger.info(f"Query returned {len(response.data)} records")
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch records from {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def create_record(self, table_name, data):
        """Create a new record in the specified table"""
        try:
            logger.info(f"Creating record in table '{table_name}'")
            
            # Log data being inserted, but limit size for large payloads
            data_str = json.dumps(data)
            if len(data_str) > 1000:
                logger.info(f"Data to insert: {data_str[:1000]}... (truncated)")
            else:
                logger.info(f"Data to insert: {data_str}")
            
            # Convert Python lists to PostgreSQL array format
           
            
            # Try with unquoted table name
            response = self.client.table(table_name).insert(data).execute()
            
            # Check for errors
            if hasattr(response, 'error') and response.error:
                error_details = str(response.error)
                logger.error(f"Error from Supabase: {error_details}")
                
                # Log additional response details if available
                if hasattr(response, 'data'):
                    logger.error(f"Response data: {response.data}")
                if hasattr(response, 'status_code'):
                    logger.error(f"Status code: {response.status_code}")
                
                raise Exception(f"Supabase error: {error_details}")
            
            # Check for empty data response
            if not response.data:
                logger.warning("No data returned from Supabase insert operation")
                return [{'id': 'unknown'}]
            
            logger.info(f"Record created successfully with ID: {response.data[0]['id'] if response.data else 'unknown'}")
            return response.data
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            logger.error(f"Failed to create record in {table_name}: {error_type}: {error_msg}")
            logger.error(f"Traceback: {error_traceback}")
            
            # Re-raise with more details
            raise Exception(f"Database error ({error_type}): {error_msg}")
    
    def update_record(self, table_name, record_id, data):
        """Update a record by ID"""
        try:
            logger.info(f"Updating record {record_id} in table '{table_name}'")
            
            # Convert Python lists to PostgreSQL array format
            clean_data = self._prepare_data_for_postgres(data)
            
            response = self.client.table(table_name).update(clean_data).eq('id', record_id).execute()
            logger.info(f"Record updated successfully")
            return response.data
        except Exception as e:
            logger.error(f"Failed to update record {record_id} in {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def delete_record(self, table_name, record_id):
        """Delete a record by ID"""
        try:
            logger.info(f"Deleting record {record_id} from table '{table_name}'")
            
            response = self.client.table(table_name).delete().eq('id', record_id).execute()
            logger.info(f"Record deleted successfully")
            return response.data
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _prepare_data_for_postgres(self, data):
        """
        Prepare data for PostgreSQL by ensuring arrays are properly formatted
        for PostgreSQL's array format.
        
        PostgreSQL expects arrays in the format: '{item1,item2,item3}'
        """
        if not isinstance(data, dict):
            return data
        
        clean_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                # For varchar[] columns, convert Python list to Postgres array format
                # We need to convert the values to strings and then format as Postgres array
                pg_array_values = []
                for item in value:
                    # Escape single quotes and replace with two single quotes (PostgreSQL syntax)
                    if item is None:
                        pg_array_values.append("NULL")
                    else:
                        item_str = str(item).replace("'", "''")
                        pg_array_values.append(f"'{item_str}'")
                
                # Format as PostgreSQL array literal: '{value1,value2,value3}'
                clean_data[key] = "{" + ",".join(pg_array_values) + "}"
            else:
                clean_data[key] = value
        
        return clean_data
    
    def test_connection(self):
        """Test the Supabase connection with a simple query"""
        try:
            # Try a simple query that should work even if table doesn't exist
            # We'll use a LIMIT 1 to minimize data transfer
            response = self.client.from_("_test_connection").select("*").limit(1).execute()
            return {
                "connected": True,
                "message": "Successfully connected to Supabase"
            }
        except Exception as e:
            # Check if the error is just about the table not existing (which is fine)
            error_str = str(e)
            if "relation" in error_str and "does not exist" in error_str:
                return {
                    "connected": True,
                    "message": "Connected to Supabase successfully (test table doesn't exist, but connection works)"
                }
            
            error_msg = f"Failed to connect to Supabase: {error_str}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "connected": False,
                "message": error_msg
            }