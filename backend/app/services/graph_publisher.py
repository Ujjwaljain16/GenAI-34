from typing import List, Dict, Any
from neo4j import AsyncGraphDatabase


class GraphPublisher:
    """
    Publishes an approved knowledge graph from PostgreSQL into Neo4j using idempotent MERGE statements.
    """

    def __init__(self):
        from app.core.config import settings

        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    async def close(self):
        await self.driver.close()

    async def publish(
        self,
        graph_version_id: str,
        concepts: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> bool:
        """
        Publishes concepts and edges to Neo4j.
        """
        try:
            async with self.driver.session() as session:
                # 1. Merge all concepts (Nodes)
                for batch in self._chunk(concepts, 500):
                    await session.run(
                        """
                        UNWIND $batch AS concept
                        MERGE (c:Concept {id: concept.id})
                        SET c.name = concept.name,
                            c.summary = concept.summary,
                            c.difficulty_level = concept.difficulty_level,
                            c.graph_version_id = $version_id
                    """,
                        batch=batch,
                        version_id=graph_version_id,
                    )

                # 2. Merge all edges (Relationships)
                for batch in self._chunk(edges, 500):
                    await session.run(
                        """
                        UNWIND $batch AS edge
                        MATCH (source:Concept {id: edge.source_concept_id})
                        MATCH (target:Concept {id: edge.target_concept_id})
                        CALL apoc.create.relationship(source, edge.relationship_type, {
                            id: edge.id,
                            confidence: edge.confidence,
                            graph_version_id: $version_id
                        }, target) YIELD rel
                        RETURN count(rel)
                    """,
                        batch=batch,
                        version_id=graph_version_id,
                    )

            return True
        except Exception as e:
            print(f"Neo4j publishing failed for version {graph_version_id}: {e}")
            return False

    def _chunk(self, lst: List[Any], n: int):
        for i in range(0, len(lst), n):
            yield lst[i : i + n]
