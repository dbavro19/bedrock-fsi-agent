import json
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests


#https://api.polygon.io/v2/aggs/ticker/{Symbol}/prev?adjusted=true&apiKey={API key}
#https://api.polygon.io/v2

def get_realtime_market_data(symbol: str) -> Dict[str, Any]:
    """
    Call the API
    """
    print("Calling the get_realtime_market_data Function")

    api_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey="
    response = requests.request("GET", api_url)

    # Parse the JSON response
    data = response.json()
    print("Response data:", data)

    results = data['results'][0]

    current_price = results['c']  # Current price
    print(f"current_price: {current_price}")
    volume = results['v']
    print(f"volume: {volume}")
    try:
        current_price = results['c']  # Current price
        volume = results['v']


        return {
            "symbol": symbol,
            "current_price": current_price,
            "volume": volume
        }
    except Exception as e:
        return {"error": str(e)}

def get_current_news(
    search_term: str
) -> Dict[str, Any]:
    """
    Gets news article
    """
    print("Calling get_current_news")

    api_url = f"https://api.polygon.io/v2/reference/news?ticker={search_term}&limit=3&apiKey="
    response = requests.request("GET", api_url)
    
    data = response.json()
    print("Response data:", data)

    results = data['results'][0]

    try:

        # TODO: Implement API call to news provider
        # Example response structure
        return {
            "search_term": search_term,
            "articles": results  
        }
    except Exception as e:
        return {"error": str(e)}

def validate_parameters(function: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate parameters based on function requirements
    """
    if function == "get_realtime_market_data":
        if not parameters.get("symbol"):
            return False, "Missing required parameter: symbol"
        return True, None
        
    elif function == "get_current_news":
        if not parameters.get("search_term"):
            return False, "Missing required parameter: search_term"
        return True, None
        
    return False, "Unknown function"

def format_response(data: Dict[str, Any], function: str) -> Dict[str, Any]:
    """
    Format the response according to Bedrock Agents requirements
    """
    return {
        "TEXT": {
            "body": json.dumps(data, indent=2)
        }
    }

def lambda_handler(event, context):
    print(event)

    try:
        # Extract basic information from event
        agent = event['agent']
        action_group = event['actionGroup']
        function = event['function']

        print(f"agent: {agent}")
        print(f"action_group: {action_group}")
        print(f"function: {function}")

        
        # Fix for parameters handling
        parameters = {}
        if 'parameters' in event and event['parameters']:
            # Convert the list of parameters to a dictionary
            for param in event['parameters']:
                parameters[param['name']] = param['value']
                print(f"param: name={param['name']}, value={param['value']}")

        # Validate parameters
        is_valid, error_message = validate_parameters(function, parameters)
        if not is_valid:
            raise ValueError(error_message)

        # Execute requested function
        if function == "get_realtime_market_data":
            result = get_realtime_market_data(
                symbol=parameters["symbol"]
            )
        elif function == "get_current_news":
            result = get_current_news(
                search_term=parameters["search_term"]
            )
        else:
            raise ValueError(f"Unknown function: {function}")


        # Format response
        response_body = format_response(result, function)

        # Build action response
        action_response = {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': response_body
            }
        }

        # Return final response
        return {
            'response': action_response,
            'messageVersion': event['messageVersion']
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        error_response = {
            "TEXT": {
                "body": f"Error executing {function}: {str(e)}"
            }
        }
        return {
            'response': {
                'actionGroup': event.get('actionGroup'),
                'function': event.get('function'),
                'functionResponse': {
                    'responseBody': error_response
                }
            },
            'messageVersion': event['messageVersion']
        }
