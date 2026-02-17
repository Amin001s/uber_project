import os
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()


client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL")
)

def get_gold_schema():

    try:

        db_connection_str = os.getenv("DB_CONNECTION_STRING")
        engine = create_engine(db_connection_str)


        schema_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'gold' AND table_name = 'dataset';
        """)

        with engine.connect() as conn:
            result = conn.execute(schema_query)
            columns = result.fetchall()

        if not columns:
            return "Error"


        schema_text = "Target Table: gold.dataset\nColumns:\n"
        for col in columns:
            schema_text += f"- {col[0]} ({col[1]})\n"
            
        return schema_text

    except Exception as e:
        return f"Error fetching schema from database: {str(e)}"

def get_sql_response(user_question):
    

    gold_schema = get_gold_schema()
    

    if "Error" in gold_schema:
        return gold_schema


    system_prompt = f"""
    You are an expert PostgreSQL Data Analyst.
    Your task is to convert the user's question into a valid SQL query.
    
    ### DATABASE SCHEMA:
    {gold_schema}

    ### CRITICAL RULES:
    
    2. **READ ONLY:** Generate ONLY 'SELECT' statements.
    3. **PROHIBITED:** NO INSERT, UPDATE, DELETE, DROP, ALTER.
    4. **LIMIT:** Always add 'LIMIT 10' to the end of the query if no limit is specified.
    5. **OUTPUT:** Return ONLY the raw SQL code. No markdown, no explanations.
    """

    try:
        response = client.chat.completions.create(
            model="openai-gpt-oss-20b", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0, 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error : {str(e)}"