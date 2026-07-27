// ============================================================================
// Context-Dependent Risk Filtering (Algorithm 1, Section 4.3)
// ============================================================================
// Adds 6 deployment properties (P1-P6), their possible values, and
// ELIMINATES / MITIGATES / AGGRAVATES relationships to Risk nodes.
//
// Run AFTER import.cypher (requires Risk nodes to exist).
// ============================================================================

// ---------------------------------------------------------------------------
// 1. Property nodes (6 deployment properties)
// ---------------------------------------------------------------------------

CREATE (:Property {id: 'P1', name: 'Architecture type',     description: 'RAG pipeline variant'})
CREATE (:Property {id: 'P2', name: 'Ingestion control',     description: 'Who can contribute documents'})
CREATE (:Property {id: 'P3', name: 'Network exposure',      description: 'Who can reach the system'})
CREATE (:Property {id: 'P4', name: 'Conversational memory', description: 'Whether session memory is enabled'})
CREATE (:Property {id: 'P5', name: 'LLM hosting location',  description: 'Where the LLM runs'})
CREATE (:Property {id: 'P6', name: 'Agentic capability',    description: 'Whether the system can execute actions'});

// ---------------------------------------------------------------------------
// 2. PropertyValue nodes (13 values across 6 properties)
// ---------------------------------------------------------------------------

// P1: Architecture type (3 values)
CREATE (:PropertyValue {property: 'P1', value: 'TEXTUAL',    description: 'Text-only RAG (Naive, Advanced, Modular)'})
CREATE (:PropertyValue {property: 'P1', value: 'GRAPHRAG',   description: 'Knowledge graph RAG (adds S-GRAPH surface)'})
CREATE (:PropertyValue {property: 'P1', value: 'MULTIMODAL', description: 'Multimodal RAG (adds S-MULTI surface)'});

// P2: Ingestion control (3 values)
CREATE (:PropertyValue {property: 'P2', value: 'INTERNAL',      description: 'Only internal trusted sources'})
CREATE (:PropertyValue {property: 'P2', value: 'AUTHENTICATED', description: 'External but authenticated contributors'})
CREATE (:PropertyValue {property: 'P2', value: 'OPEN',          description: 'Publicly writable / open ingestion'});

// P3: Network exposure (3 values)
CREATE (:PropertyValue {property: 'P3', value: 'ISOLATED', description: 'Air-gapped or strictly isolated network'})
CREATE (:PropertyValue {property: 'P3', value: 'INTERNAL', description: 'Corporate/internal network only'})
CREATE (:PropertyValue {property: 'P3', value: 'PUBLIC',   description: 'Internet-facing'});

// P4: Conversational memory (2 values)
CREATE (:PropertyValue {property: 'P4', value: 'true',  description: 'Session memory enabled (S-MEM surface active)'})
CREATE (:PropertyValue {property: 'P4', value: 'false', description: 'No conversational memory'});

// P5: LLM hosting location (3 values)
CREATE (:PropertyValue {property: 'P5', value: 'ON_PREMISE', description: 'LLM hosted on own infrastructure'})
CREATE (:PropertyValue {property: 'P5', value: 'CLOUD',      description: 'LLM hosted by third-party provider'})
CREATE (:PropertyValue {property: 'P5', value: 'HYBRID',     description: 'Mixed deployment'});

// P6: Agentic capability (2 values)
CREATE (:PropertyValue {property: 'P6', value: 'true',  description: 'System can execute actions (adds S-ORCH surface)'})
CREATE (:PropertyValue {property: 'P6', value: 'false', description: 'No action execution capability'});

// ---------------------------------------------------------------------------
// 3. Link PropertyValue -> Property
// ---------------------------------------------------------------------------

MATCH (pv:PropertyValue), (p:Property)
WHERE pv.property = p.id
CREATE (pv)-[:VALUE_OF]->(p);

// ---------------------------------------------------------------------------
// 4. ELIMINATES relationships (risk is structurally impossible)
// ---------------------------------------------------------------------------

// P1 = TEXTUAL eliminates GRAPHRAG-exclusive and MULTIMODAL-exclusive risks
MATCH (pv:PropertyValue {property: 'P1', value: 'TEXTUAL'})
MATCH (r:Risk) WHERE r.id IN ['R17']
CREATE (pv)-[:ELIMINATES {reason: 'GRAPHRAG-exclusive risk; S-GRAPH surface not present'}]->(r);

MATCH (pv:PropertyValue {property: 'P1', value: 'TEXTUAL'})
MATCH (r:Risk) WHERE r.id IN ['R24', 'R25', 'R29', 'R39']
CREATE (pv)-[:ELIMINATES {reason: 'MULTIMODAL-exclusive risk; S-MULTI surface not present'}]->(r);

// P1 = GRAPHRAG eliminates MULTIMODAL-exclusive risks
MATCH (pv:PropertyValue {property: 'P1', value: 'GRAPHRAG'})
MATCH (r:Risk) WHERE r.id IN ['R24', 'R25', 'R29', 'R39']
CREATE (pv)-[:ELIMINATES {reason: 'MULTIMODAL-exclusive risk; S-MULTI surface not present'}]->(r);

// P1 = MULTIMODAL eliminates GRAPHRAG-exclusive risks
MATCH (pv:PropertyValue {property: 'P1', value: 'MULTIMODAL'})
MATCH (r:Risk) WHERE r.id IN ['R17']
CREATE (pv)-[:ELIMINATES {reason: 'GRAPHRAG-exclusive risk; S-GRAPH surface not present'}]->(r);

// P3 = ISOLATED eliminates network-dependent risks
MATCH (pv:PropertyValue {property: 'P3', value: 'ISOLATED'})
MATCH (r:Risk) WHERE r.id IN ['R22', 'R40']
CREATE (pv)-[:ELIMINATES {reason: 'Risk requires external network access'}]->(r);

// P3 = INTERNAL eliminates network-dependent risks
MATCH (pv:PropertyValue {property: 'P3', value: 'INTERNAL'})
MATCH (r:Risk) WHERE r.id IN ['R22', 'R40']
CREATE (pv)-[:ELIMINATES {reason: 'Risk requires external network access'}]->(r);

// P4 = false eliminates memory-dependent risks
MATCH (pv:PropertyValue {property: 'P4', value: 'false'})
MATCH (r:Risk) WHERE r.id IN ['R16']
CREATE (pv)-[:ELIMINATES {reason: 'Risk requires conversational memory (S-MEM surface)'}]->(r);

// ---------------------------------------------------------------------------
// 5. MITIGATES relationships (risk likelihood reduced)
// ---------------------------------------------------------------------------

// P2 = INTERNAL mitigates external poisoning risks
MATCH (pv:PropertyValue {property: 'P2', value: 'INTERNAL'})
MATCH (r:Risk) WHERE r.id IN ['R8', 'R11', 'R19', 'R20']
CREATE (pv)-[:MITIGATES {reason: 'Internal-only ingestion limits external poisoning vectors'}]->(r);

// P2 = AUTHENTICATED mitigates external poisoning risks
MATCH (pv:PropertyValue {property: 'P2', value: 'AUTHENTICATED'})
MATCH (r:Risk) WHERE r.id IN ['R8', 'R11', 'R19', 'R20']
CREATE (pv)-[:MITIGATES {reason: 'Authenticated ingestion reduces but does not eliminate poisoning risk'}]->(r);

// ---------------------------------------------------------------------------
// 6. AGGRAVATES relationships (risk impact increased)
// ---------------------------------------------------------------------------

// P5 = CLOUD aggravates confidentiality risks (data transit to third party)
MATCH (pv:PropertyValue {property: 'P5', value: 'CLOUD'})
MATCH (r:Risk) WHERE r.id IN ['R2', 'R6', 'R7']
CREATE (pv)-[:AGGRAVATES {reason: 'Cloud LLM implies data transit, increasing confidentiality exposure'}]->(r);

// P5 = HYBRID aggravates confidentiality risks
MATCH (pv:PropertyValue {property: 'P5', value: 'HYBRID'})
MATCH (r:Risk) WHERE r.id IN ['R2', 'R6', 'R7']
CREATE (pv)-[:AGGRAVATES {reason: 'Hybrid deployment implies partial data transit to third party'}]->(r);

// ---------------------------------------------------------------------------
// Filtering queries are available in cypher_queries.txt
// ---------------------------------------------------------------------------
