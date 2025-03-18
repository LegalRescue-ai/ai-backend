# app/services/database_service.py
from flask import current_app
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.client = current_app.config.get('SUPABASE_CLIENT')
        if not self.client:
            logger.error("Supabase client not initialized")
            raise ValueError("Supabase client not initialized")
        logger.info("Database service initialized")

    def get_records(self, table_name, query=None):
        """Get records from a table with optional query"""
        try:
            # Use quotes around table name to handle names with spaces
            logger.info(f"Getting records from table: {table_name}")
            db_query = self.client.table(f'"{table_name}"').select("*")
            
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
            raise

    def create_record(self, table_name, data):
        """Create a new record in the specified table"""
        try:
            logger.info(f"Creating record in table '{table_name}'")
            logger.info(f"Data to insert: {json.dumps(data)}")
            
            # Use quotes around table name to handle names with spaces
            response = self.client.table(f'"{table_name}"').insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error from Supabase: {response.error}")
                raise Exception(f"Supabase error: {response.error}")
                
            if not response.data:
                logger.error("No data returned from Supabase insert operation")
                # Return empty list with placeholder to avoid None access
                return [{'id': 'unknown'}]
                
            logger.info(f"Record created successfully with ID: {response.data[0]['id'] if response.data else 'unknown'}")
            return response.data
        except Exception as e:
            logger.error(f"Failed to create record in {table_name}: {str(e)}")
            raise

    def update_record(self, table_name, record_id, data):
        """Update a record by ID"""
        try:
            logger.info(f"Updating record {record_id} in table '{table_name}'")
            # Use quotes around table name to handle names with spaces
            response = self.client.table(f'"{table_name}"').update(data).eq('id', record_id).execute()
            logger.info(f"Record updated successfully")
            return response.data
        except Exception as e:
            logger.error(f"Failed to update record {record_id} in {table_name}: {str(e)}")
            raise

    def delete_record(self, table_name, record_id):
        """Delete a record by ID"""
        try:
            logger.info(f"Deleting record {record_id} from table '{table_name}'")
            # Use quotes around table name to handle names with spaces
            response = self.client.table(f'"{table_name}"').delete().eq('id', record_id).execute()
            logger.info(f"Record deleted successfully")
            return response.data
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from {table_name}: {str(e)}")
            raise