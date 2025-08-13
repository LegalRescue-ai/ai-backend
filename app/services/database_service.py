# app/services/database_service.py
import os
import logging
import json
import traceback
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Use the app-level Supabase client - zero initialization overhead"""
        self.client = current_app.config['SUPABASE_CLIENT']
    
    def get_records(self, table_name, query=None):
        """Get records from a table with optional query"""
        try:
            db_query = self.client.table(table_name).select("*")
            
            if query and isinstance(query, dict):
                for key, value in query.items():
                    db_query = db_query.eq(key, value)
            
            response = db_query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch records from {table_name}: {str(e)}")
            raise
    
    def create_record(self, table_name, data):
        """Create a new record in the specified table - optimized for speed"""
        try:
            response = self.client.table(table_name).insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase error: {response.error}")
            
            if not response.data:
                return [{'id': 'unknown'}]
            
            return response.data
            
        except Exception as e:
            logger.error(f"Database error in {table_name}: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def update_record(self, table_name, record_id, data):
        """Update a record by ID"""
        try:
            response = self.client.table(table_name).update(data).eq('id', record_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to update record {record_id} in {table_name}: {str(e)}")
            raise
    
    def delete_record(self, table_name, record_id):
        """Delete a record by ID"""
        try:
            response = self.client.table(table_name).delete().eq('id', record_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from {table_name}: {str(e)}")
            raise
    
    def test_connection(self):
        """Test the Supabase connection with a simple query"""
        try:
            response = self.client.from_("_test_connection").select("*").limit(1).execute()
            return {
                "connected": True,
                "message": "Successfully connected to Supabase"
            }
        except Exception as e:
            error_str = str(e)
            if "relation" in error_str and "does not exist" in error_str:
                return {
                    "connected": True,
                    "message": "Connected to Supabase successfully (test table doesn't exist, but connection works)"
                }
            
            return {
                "connected": False,
                "message": f"Failed to connect to Supabase: {error_str}"
            }