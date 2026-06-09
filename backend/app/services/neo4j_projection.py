"""
Neo4j projection (AGENT.md Knowledge Graph Contract).

Postgres is the source of truth; Neo4j is a PROJECTION used for relationship
traversals (prerequisite paths, recommendations). This service mirrors the
authoritative Postgres state into Neo4j:

  (:Concept)-[:PREREQUISITE_OF]->(:Concept)     # graph structure
  (:Student)-[:HAS_MASTERY {score,state}]->(:Concept)
  (:Student)-[:CURRENTLY_LEARNING]->(:Concept)

All writes are best-effort and run in a thread (the neo4j driver is sync). A
Neo4j outage must never break the Postgres-backed flows, so callers wrap these
in try/except and log failures (eventually-consistent per AGENT.md).
"""

from __future__ import annotations

import asyncio
import logging
from typing import List, Tuple

from app.core.neo4j import Neo4jDriver

logger = logging.getLogger(__name__)


def _project_book_sync(
    book_id: str, concepts: List[dict], edges: List[Tuple[str, str]]
) -> None:
    driver = Neo4jDriver.get_driver()
    with driver.session() as s:
        # Upsert concept nodes (mirror of Postgres concepts).
        s.run(
            """
            UNWIND $concepts AS c
            MERGE (n:Concept {id: c.id})
            SET n.name = c.name, n.book_id = $book_id, n.difficulty = c.difficulty
            """,
            concepts=concepts,
            book_id=book_id,
        )
        # Replace this book's prerequisite edges to match Postgres exactly.
        s.run(
            """
            MATCH (:Concept {book_id: $book_id})-[r:PREREQUISITE_OF]->(:Concept {book_id: $book_id})
            DELETE r
            """,
            book_id=book_id,
        )
        s.run(
            """
            UNWIND $edges AS e
            MATCH (a:Concept {id: e.from}), (b:Concept {id: e.to})
            MERGE (a)-[:PREREQUISITE_OF]->(b)
            """,
            edges=[{"from": f, "to": t} for f, t in edges],
        )


def _project_user_sync(
    user_id: str, masteries: List[dict], in_progress: List[str]
) -> None:
    driver = Neo4jDriver.get_driver()
    with driver.session() as s:
        s.run("MERGE (:Student {id: $uid})", uid=user_id)
        # Refresh HAS_MASTERY edges for this student.
        s.run("MATCH (:Student {id: $uid})-[r:HAS_MASTERY]->() DELETE r", uid=user_id)
        s.run(
            """
            UNWIND $rows AS m
            MATCH (st:Student {id: $uid}), (c:Concept {id: m.concept_id})
            MERGE (st)-[r:HAS_MASTERY]->(c)
            SET r.score = m.score, r.state = m.state
            """,
            uid=user_id,
            rows=masteries,
        )
        s.run(
            "MATCH (:Student {id: $uid})-[r:CURRENTLY_LEARNING]->() DELETE r",
            uid=user_id,
        )
        s.run(
            """
            UNWIND $ids AS cid
            MATCH (st:Student {id: $uid}), (c:Concept {id: cid})
            MERGE (st)-[:CURRENTLY_LEARNING]->(c)
            """,
            uid=user_id,
            ids=in_progress,
        )


async def project_book_graph(
    book_id: str, concepts: List[dict], edges: List[Tuple[str, str]]
) -> bool:
    try:
        await asyncio.to_thread(_project_book_sync, book_id, concepts, edges)
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("Neo4j book projection failed (book=%s): %s", book_id, e)
        return False


async def project_user_state(
    user_id: str, masteries: List[dict], in_progress: List[str]
) -> bool:
    try:
        await asyncio.to_thread(_project_user_sync, user_id, masteries, in_progress)
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("Neo4j user projection failed (user=%s): %s", user_id, e)
        return False
