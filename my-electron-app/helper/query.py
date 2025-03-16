import sys
import json
import os
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://5f06d1b4.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Nk30WHZPhuWpLUeMRHyuspzr-xjoX7zWw1kcTm8JKlE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check for missing credentials
if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key is missing. Set it as an environment variable.")

# Connect to Neo4j
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)

# Initialize GPT-4o
llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=OPENAI_API_KEY)

qa_chain = GraphCypherQAChain.from_llm(
    llm, 
    graph=graph, 
    verbose=True, 
    allow_dangerous_requests=True
)

# 🔹 List of all defined relationships in the KG
POSSIBLE_RELATIONS = [
    "HAS_PRESCRIPTION", "UNDERWENT_TEST", "DIAGNOSED_WITH", "HAS_DOSAGE",
    "PRESCRIBED_BY", "HAS_ALLERGY_TO", "TREATED_WITH", "REQUIRES_TEST",
    "HAS_SEVERITY", "HAS_RESULT", "HAS_INSURANCE", "ADMITTED_TO",
    "DISCHARGED_TO", "BELONGS_TO_RACE", "HAS_GENDER", "HAS_AGE_GROUP"
]

def fetch_defined_relations():
    """ Retrieves all relationship types in the Neo4j Knowledge Graph. """
    query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
    results = graph.query(query)
    return [record['relationshipType'] for record in results]

def fetch_related_relations(user_query):
    """ Retrieves relationships linked to the latest user query. """
    query = """
    MATCH (p:Patient)-[r]->(x)
    RETURN DISTINCT type(r) AS relation
    """
    results = graph.query(query)
    return [record['relation'] for record in results]

def generate_summary(user_query, results):
    """ Uses GPT-4o to generate a short natural summary of the query results. """
    if not results:
        return f"Sorry, I couldn't find any relevant data for your query: '{user_query}'."

    formatted_results = "\n".join([f"- {item}" for item in results])

    summary_prompt = f"""
    You are a medical assistant. Summarize the answer to the following medical query based on the retrieved results.

    **User Query:** {user_query}

    **Results:**
    {formatted_results}

    Provide a **concise, clear response** as if answering a patient or doctor.
    """

    summary_response = llm.invoke(summary_prompt)
    return summary_response.content.strip()

def generate_recommendations(user_query, related_relations, results):
    """ Generates simple and relevant queries based on the latest query context and KG relationships. """
    
    recommendation_prompt = f"""
    The following relationships are directly linked to the latest query:
    {', '.join(related_relations)}

    The retrieved results were:
    {results}

    Based on this information, generate **3 to 5 simple and relevant** follow-up queries that utilize these relationships.

    **User Query:** {user_query}

    Format the recommendations as:
    - **Query:** <Query>
      (Relation: <Neo4j Relationship>)

    **Do not include Cypher queries. Only return formatted queries with their relationships.**
    """

    recommendations_response = llm.invoke(recommendation_prompt)
    return recommendations_response.content.strip()

def process_query(user_query):
    """ Converts a human text query to Cypher, retrieves data, and generates a summary + relationship-tagged recommendations. """
    try:
        print("\n🔍 Processing Query:", user_query)

        # Generate Cypher Query + Results
        response = qa_chain.invoke(user_query)

        # Check if response exists
        if not response:
            print("⚠️ No response received. Try again.")
            return None

        # Extract Cypher query and results
        cypher_query = response.get("query", "⚠️ No query generated!")
        results = response.get("result", [])

        print("\n🔹 Generated Cypher Query:")
        print(cypher_query)

        # Generate a natural language summary
        summary = generate_summary(user_query, results)

        print("\n✅ Answer:")
        print(summary)

        # Fetch dynamically related relationships
        related_relations = fetch_related_relations(user_query)

        # Generate updated follow-up recommendations
        recommendations = generate_recommendations(user_query, related_relations, results)

        print("\n🔄 Recommended Follow-Up Queries:")
        for line in recommendations.splitlines():
            print(line)

        return summary, recommendations, results  # Ensure results persist for next iteration

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    try:
        # Read the JSON input from Electron
        json_data = sys.argv[1]  # Read the first argument (JSON string)
        data = json.loads(json_data)  # Parse JSON
        results_history = []
        # Extract the "query" field
        query = data.get("query", "No query provided")

        # Process the query
        summary, recommendations, results = process_query(query)
        if results:
            results_history.append({"query": query, "results": results})

            # **Keep only the last 15 queries**
            results_history = results_history[-15:]

        print("\n📜 Query History (Latest 15 Queries):")
        for item in results_history:
            print(f"🔹 {item['query']}: {item['results']}")

        # Return the response as JSON
        print(json.dumps(results_history))  # Send JSON response back to Electron

    except Exception as e:
        # Handle errors and return as JSON
        print(json.dumps({"error": str(e)}))
