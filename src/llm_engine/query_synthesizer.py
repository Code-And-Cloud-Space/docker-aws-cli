from typing import List, Dict

class QuerySynthesizer:
    """
    Grammar-Guided Dual AST Query Synthesizer.
    Compiles validated abstract syntax into dialect-specific queries:
    1. Salesforce SOQL (with child-to-parent dot notation)
    2. openCypher (Neo4j / Memgraph / AWS Neptune with graph pattern matching)
    """

    @staticmethod
    def synthesize_soql(
        target_entity: str,
        fields_str: str,
        clauses: List[str],
        limit: int
    ) -> str:
        where_part = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        return f"SELECT {fields_str} FROM {target_entity}{where_part} ORDER BY LastModifiedDate DESC LIMIT {limit}"

    @staticmethod
    def synthesize_cypher(
        target_entity: str,
        fields_str: str,
        clauses: List[str],
        limit: int,
        has_account_relationship: bool
    ) -> str:
        var_name = target_entity[0].lower()
        fields_list = [f.strip() for f in fields_str.split(",") if f.strip()]
        where_part = f" WHERE {' AND '.join(clauses)}" if clauses else ""

        if has_account_relationship:
            match_clause = f"MATCH ({var_name}:{target_entity})-[:BELONGS_TO]->(a:Account)"
            cypher_fields = ", ".join([
                f"a.Name AS AccountName" if f == "Account.Name" else f"{var_name}.{f}"
                for f in fields_list
            ])
            return f"{match_clause}{where_part} RETURN {cypher_fields} ORDER BY {var_name}.LastModifiedDate DESC LIMIT {limit}"
        else:
            filtered_fields = []
            seen = set()
            for f in fields_list:
                item = f"{var_name}.AccountId" if f == "Account.Name" else f"{var_name}.{f}"
                if item not in seen:
                    seen.add(item)
                    filtered_fields.append(item)
            cypher_fields = ", ".join(filtered_fields)
            return f"MATCH ({var_name}:{target_entity}){where_part} RETURN {cypher_fields} ORDER BY {var_name}.LastModifiedDate DESC LIMIT {limit}"
