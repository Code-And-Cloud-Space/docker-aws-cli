// ==============================================================================
// Cypher Query: Search All Media Type of Account
// Compatible with Neo4j, openCypher, Memgraph, and AWS Neptune Graph Databases
// ==============================================================================

// 1. Search All Media Type of Account (Match nodes with Type or Industry = 'Media')
MATCH (a:Account)
WHERE a.Type = 'Media'
   OR a.Industry = 'Media'
   OR toLower(a.Type) CONTAINS 'media'
   OR toLower(a.Industry) CONTAINS 'media'
   OR toLower(a.Name) CONTAINS 'media'
RETURN a.Id AS Id,
       a.Name AS Name,
       a.Type AS Type,
       a.Industry AS Industry,
       a.Phone AS Phone,
       a.AnnualRevenue AS AnnualRevenue,
       a.BillingCity AS BillingCity,
       a.LastModifiedDate AS LastModifiedDate
ORDER BY a.LastModifiedDate DESC
LIMIT 50;

// 2. Search All Media Related Accounts with Connected Contacts
MATCH (a:Account)-[:HAS_CONTACT]->(c:Contact)
WHERE a.Type = 'Media' OR a.Industry = 'Media'
RETURN a.Name AS AccountName, a.Type AS AccountType, c.FirstName + ' ' + c.LastName AS ContactName, c.Email AS Email;

// 3. Search All Media Related Accounts with Connected Opportunities
MATCH (a:Account)-[:HAS_OPPORTUNITY]->(o:Opportunity)
WHERE a.Type = 'Media' OR a.Industry = 'Media'
RETURN a.Name AS AccountName, o.Name AS OpportunityName, o.Amount AS Amount, o.StageName AS Stage;
