import os
import logging
import json
import traceback
import boto3
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError
from decimal import Decimal
from typing import Dict, List, Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize the database service with DynamoDB connection"""
        try:
            # Get credentials from environment variables
            region = os.getenv('AWS_REGION', 'us-east-1')
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            # Configure boto3 session
            session_config = {
                'region_name': region
            }
            
            if access_key_id and secret_access_key:
                session_config['aws_access_key_id'] = access_key_id
                session_config['aws_secret_access_key'] = secret_access_key
            
            # Create DynamoDB resource and client
            self.session = boto3.Session(**session_config)
            self.dynamodb = self.session.resource('dynamodb')
            self.client = self.session.client('dynamodb')
            
            current_app.logger.info("✅ Database service initialized with DynamoDB connection")
        except Exception as e:
            error_msg = f"Failed to initialize DynamoDB client: {str(e)}"
            current_app.logger.error(error_msg)
            current_app.logger.error(traceback.format_exc())
            raise ValueError(error_msg)
    
    def get_records(self, table_name: str, query: Optional[Dict] = None, index_name: Optional[str] = None) -> List[Dict]:
        """
        Get records from a table with optional query
        
        Args:
            table_name: Name of the DynamoDB table
            query: Dict with 'key_condition' and/or 'filter_expression' for query, or 'filter_expression' for scan
            index_name: Name of GSI to query (optional)
        
        Examples:
            # Scan all records
            service.get_records('users')
            
            # Query with key condition (requires partition key)
            service.get_records('users', {'key_condition': 'id = :id', 'expression_values': {':id': 'user123'}})
            
            # Scan with filter
            service.get_records('users', {'filter_expression': 'age > :age', 'expression_values': {':age': 25}})
        """
        try:
            current_app.logger.info(f"Getting records from table: {table_name}")
            table = self.dynamodb.Table(table_name)
            
            if query and 'key_condition' in query:
                # Use Query operation (more efficient when you have a partition key)
                kwargs = {
                    'KeyConditionExpression': query['key_condition']
                }
                
                if 'expression_values' in query:
                    kwargs['ExpressionAttributeValues'] = query['expression_values']
                
                if 'expression_names' in query:
                    kwargs['ExpressionAttributeNames'] = query['expression_names']
                
                if 'filter_expression' in query:
                    kwargs['FilterExpression'] = query['filter_expression']
                
                if index_name:
                    kwargs['IndexName'] = index_name
                
                response = table.query(**kwargs)
            else:
                # Use Scan operation
                kwargs = {}
                
                if query and 'filter_expression' in query:
                    kwargs['FilterExpression'] = query['filter_expression']
                    
                    if 'expression_values' in query:
                        kwargs['ExpressionAttributeValues'] = query['expression_values']
                    
                    if 'expression_names' in query:
                        kwargs['ExpressionAttributeNames'] = query['expression_names']
                
                if index_name:
                    kwargs['IndexName'] = index_name
                
                response = table.scan(**kwargs)
            
            # Convert Decimal types back to float/int for JSON serialization
            items = self._deserialize_decimals(response['Items'])
            return items
            
        except Exception as e:
            current_app.logger.error(f"Failed to fetch records from {table_name}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise
    
    def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        try:
            current_app.logger.info(f"Creating record in table '{table_name}'")
            
            # Convert float values to Decimal for DynamoDB
            prepared_data = self._serialize_for_dynamodb(data)
            
            table = self.dynamodb.Table(table_name)
            response = table.put_item(Item=prepared_data)
            
            # DynamoDB put_item doesn't return the created item by default
            # Return the original data as confirmation
            return data
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            current_app.logger.error(f"Failed to create record in {table_name}: {error_type}: {error_msg}")
            current_app.logger.error(f"Traceback: {error_traceback}")
            
            # Re-raise with more details
            raise Exception(f"Database error ({error_type}): {error_msg}")
    
    def update_record(self, table_name: str, key: Dict[str, Any], data: Dict[str, Any], 
                     condition_expression: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a record by primary key
        
        Args:
            table_name: Name of the table
            key: Primary key of the record (e.g., {'id': 'value'} or {'pk': 'value', 'sk': 'value'})
            data: Fields to update
            condition_expression: Optional condition that must be satisfied for the update
        """
        try:
            current_app.logger.info(f"Updating record with key {key} in table '{table_name}'")
            
            # Prepare data for DynamoDB
            prepared_data = self._serialize_for_dynamodb(data)
            
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for i, (field, value) in enumerate(prepared_data.items()):
                if i > 0:
                    update_expression += ", "
                
                # Use attribute names to handle reserved keywords
                attr_name = f"#attr{i}"
                attr_value = f":val{i}"
                
                update_expression += f"{attr_name} = {attr_value}"
                expression_attribute_names[attr_name] = field
                expression_attribute_values[attr_value] = value
            
            table = self.dynamodb.Table(table_name)
            
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeNames': expression_attribute_names,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            response = table.update_item(**kwargs)
            updated_item = self._deserialize_decimals(response['Attributes'])
            
            return updated_item
            
        except Exception as e:
            current_app.logger.error(f"Failed to update record {key} in {table_name}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise
    
    def delete_record(self, table_name: str, key: Dict[str, Any], 
                     condition_expression: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a record by primary key
        
        Args:
            table_name: Name of the table
            key: Primary key of the record
            condition_expression: Optional condition that must be satisfied for the delete
        """
        try:
            current_app.logger.info(f"Deleting record with key {key} from table '{table_name}'")
            
            table = self.dynamodb.Table(table_name)
            
            kwargs = {
                'Key': key,
                'ReturnValues': 'ALL_OLD'
            }
            
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            response = table.delete_item(**kwargs)
            
            if 'Attributes' in response:
                deleted_item = self._deserialize_decimals(response['Attributes'])
                return deleted_item
            else:
                return {}
                
        except Exception as e:
            current_app.logger.error(f"Failed to delete record {key} from {table_name}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise
    
    def get_record_by_key(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single record by its primary key"""
        try:
            current_app.logger.info(f"Getting record with key {key} from table '{table_name}'")
            
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            
            if 'Item' in response:
                item = self._deserialize_decimals(response['Item'])
                return item
            else:
                return None
                
        except Exception as e:
            current_app.logger.error(f"Failed to get record {key} from {table_name}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise
    
    def _serialize_for_dynamodb(self, data: Any) -> Any:
        """Convert data types for DynamoDB (e.g., float to Decimal)"""
        if isinstance(data, dict):
            return {k: self._serialize_for_dynamodb(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_for_dynamodb(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        else:
            return data
    
    def _deserialize_decimals(self, data: Any) -> Any:
        """Convert Decimal types back to float for JSON serialization"""
        if isinstance(data, dict):
            return {k: self._deserialize_decimals(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deserialize_decimals(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the DynamoDB connection by listing tables"""
        try:
            # Try to list tables to test connection
            response = self.client.list_tables(Limit=1)
            
            return {
                "connected": True,
                "message": f"Successfully connected to DynamoDB in region {self.client.meta.region_name}",
                "table_count": len(response.get('TableNames', []))
            }
        except NoCredentialsError:
            error_msg = "AWS credentials not found"
            current_app.logger.error(error_msg)
            return {
                "connected": False,
                "message": error_msg
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = f"AWS error ({error_code}): {e.response['Error']['Message']}"
            current_app.logger.error(error_msg)
            current_app.logger.error(traceback.format_exc())
            return {
                "connected": False,
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Failed to connect to DynamoDB: {str(e)}"
            current_app.logger.error(error_msg)
            current_app.logger.error(traceback.format_exc())
            return {
                "connected": False,
                "message": error_msg
            }

# Utility functions for common DynamoDB operations
class DynamoDBQueryBuilder:
    """Helper class to build DynamoDB query expressions"""
    
    @staticmethod
    def key_condition(partition_key: str, partition_value: Any, sort_key: Optional[str] = None, 
                     sort_value: Optional[Any] = None, sort_operator: str = "=") -> Dict:
        """
        Build a key condition expression for DynamoDB Query
        
        Args:
            partition_key: Name of the partition key attribute
            partition_value: Value of the partition key
            sort_key: Name of the sort key attribute (optional)
            sort_value: Value of the sort key (optional)
            sort_operator: Comparison operator for sort key (=, <, >, <=, >=, BETWEEN, begins_with)
        """
        condition = f"{partition_key} = :pk_val"
        values = {":pk_val": partition_value}
        
        if sort_key and sort_value is not None:
            if sort_operator == "BETWEEN":
                condition += f" AND {sort_key} BETWEEN :sk_val1 AND :sk_val2"
                if isinstance(sort_value, (list, tuple)) and len(sort_value) == 2:
                    values[":sk_val1"] = sort_value[0]
                    values[":sk_val2"] = sort_value[1]
                else:
                    raise ValueError("BETWEEN operator requires a list/tuple of two values")
            elif sort_operator == "begins_with":
                condition += f" AND begins_with({sort_key}, :sk_val)"
                values[":sk_val"] = sort_value
            else:
                condition += f" AND {sort_key} {sort_operator} :sk_val"
                values[":sk_val"] = sort_value
        
        return {
            "key_condition": condition,
            "expression_values": values
        }
    
    @staticmethod
    def filter_expression(field: str, value: Any, operator: str = "=") -> Dict:
        """
        Build a filter expression for DynamoDB Scan/Query
        
        Args:
            field: Name of the attribute to filter on
            value: Value to compare against
            operator: Comparison operator (=, <>, <, >, <=, >=, BETWEEN, IN, contains, etc.)
        """
        if operator == "BETWEEN":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return {
                    "filter_expression": f"{field} BETWEEN :val1 AND :val2",
                    "expression_values": {":val1": value[0], ":val2": value[1]}
                }
            else:
                raise ValueError("BETWEEN operator requires a list/tuple of two values")
        elif operator == "IN":
            if isinstance(value, (list, tuple)):
                placeholders = [f":val{i}" for i in range(len(value))]
                return {
                    "filter_expression": f"{field} IN ({', '.join(placeholders)})",
                    "expression_values": {f":val{i}": v for i, v in enumerate(value)}
                }
            else:
                raise ValueError("IN operator requires a list/tuple of values")
        elif operator == "contains":
            return {
                "filter_expression": f"contains({field}, :val)",
                "expression_values": {":val": value}
            }
        else:
            return {
                "filter_expression": f"{field} {operator} :val",
                "expression_values": {":val": value}
            }