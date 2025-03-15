import sys
import json
import os
# from langchain.chains import GraphCypherQAChain
# from langchain.graphs import Neo4jGraph
# from langchain.chat_models import ChatOpenAI
# from dotenv import load_dotenv

# Load environment variables from .env file (if available)
# load_dotenv()


def process_query(user_query):
    """ Converts a human text query to Cypher, retrieves data, and returns results. """
    
    # NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://5f06d1b4.databases.neo4j.io")
    # NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    # NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Nk30WHZPhuWpLUeMRHyuspzr-xjoX7zWw1kcTm8JKlE")
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # # Check for missing credentials
    # if not OPENAI_API_KEY:
    #     raise ValueError(" OpenAI API Key is missing. Set it as an environment variable.")

    # # Connect to Neo4j
    # graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)

    # # Initialize OpenAI model (GPT-4o)
    # llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=OPENAI_API_KEY)

    # # Allow execution of Cypher queries
    # qa_chain = GraphCypherQAChain.from_llm(
    #     llm, 
    #     graph=graph, 
    #     verbose=True, 
    #     allow_dangerous_requests=True
    # )
    try:
        
        # # Convert text to Cypher and fetch data
        # response = qa_chain.run(user_query)
        
        # print("\n🔹 Cypher Query Generated:")
        # print(response['cypher_query'])  # Debug: Print generated Cypher query
        
        # print("\nQuery Results:")
        # print(response['results'])  # Display results
        
        # return response['results']
        return "Happy happy"
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    try:
        # Read the JSON input from Electron
        json_data = sys.argv[1]  # Read the first argument (JSON string)
        data = json.loads(json_data)  # Parse JSON

        # Extract the "query" field
        query = data.get("query", "No query provided")

        # Process the query
        response = process_query(query)

        # Return the response as JSON
        print(json.dumps(response))  # Send JSON response back to Electron

    except Exception as e:
        # Handle errors and return as JSON
        print(json.dumps({"error": str(e)}))
