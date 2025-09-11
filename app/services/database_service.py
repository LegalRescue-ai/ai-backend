import os
import logging
import json
import traceback
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Use the app-level DynamoDB client - zero initialization overhead"""
        self.client = current_app.config['DYNAMODB_CLIENT']
    
    def get_records(self, table_name, query=None):
        """Get records from a table with optional query"""
        try:
            table = self.client.Table(table_name)
            
            if query and isinstance(query, dict):
                # Build scan with filter expressions for simple key-value queries
                scan_kwargs = {}
                filter_expressions = []
                expression_values = {}
                
                for key, value in query.items():
                    filter_expressions.append(f"{key} = :{key}")
                    expression_values[f":{key}"] = value
                
                if filter_expressions:
                    scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
                    scan_kwargs['ExpressionAttributeValues'] = expression_values
                
                response = table.scan(**scan_kwargs)
            else:
                response = table.scan()
            
            return response['Items']
        except Exception as e:
            logger.error(f"Failed to fetch records from {table_name}: {str(e)}")
            raise
    
    def create_record(self, table_name, data):
        """Create a new record in the specified table - optimized for speed"""
        try:
            table = self.client.Table(table_name)
            response = table.put_item(Item=data, ReturnValues='ALL_OLD')
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"DynamoDB error: {response.error}")
            
            if not data:
                return [{'id': 'unknown'}]
            
            return [data]
            
        except Exception as e:
            logger.error(f"Database error in {table_name}: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def update_record(self, table_name, record_id, data):
        """Update a record by ID"""
        try:
            table = self.client.Table(table_name)
            
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for i, (field, value) in enumerate(data.items()):
                if i > 0:
                    update_expression += ", "
                
                # Use attribute names to handle reserved keywords
                attr_name = f"#attr{i}"
                attr_value = f":val{i}"
                
                update_expression += f"{attr_name} = {attr_value}"
                expression_attribute_names[attr_name] = field
                expression_attribute_values[attr_value] = value
            
            response = table.update_item(
                Key={'id': record_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            return response['Attributes']
        except Exception as e:
            logger.error(f"Failed to update record {record_id} in {table_name}: {str(e)}")
            raise
    
    def delete_record(self, table_name, record_id):
        """Delete a record by ID"""
        try:
            table = self.client.Table(table_name)
            response = table.delete_item(
                Key={'id': record_id},
                ReturnValues='ALL_OLD'
            )
            return response.get('Attributes', {})
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from {table_name}: {str(e)}")
            raise
    
    
    def test_connection(self):
        """Test the DynamoDB connection with a simple query"""
        try:
            response = self.client.list_tables(Limit=1)
            return {
                "connected": True,
                "message": "Successfully connected to DynamoDB"
            }
        except Exception as e:
            error_str = str(e)
            if "table" in error_str and "does not exist" in error_str:
                return {
                    "connected": True,
                    "message": "Connected to DynamoDB successfully (test table doesn't exist, but connection works)"
                }
            
            return {
                "connected": False,
                "message": f"Failed to connect to DynamoDB: {error_str}"
            }
