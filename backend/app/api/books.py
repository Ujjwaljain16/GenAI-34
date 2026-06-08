from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user_id
from app.repositories.book_repo import BookRepository
from app.services.book_service import BookService, mock_process_book_job
from app.schemas.book import UploadResponse, JobStatusDTO, BookDTO, BookCreate, BookStatusDTO, BookDetailDTO, GraphDTO, BookSummaryDTO
from app.schemas.graph_reveal import PersonalGraphDTO
from app.repositories.graph_repo import GraphRepository
from app.services.graph_reveal_service import GraphRevealService
from app.core.db import AsyncSessionLocal

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(session: AsyncSession = Depends(get_db)) -> BookService:
    return BookService(BookRepository(session))

@router.post("", response_model=dict, status_code=201)
async def create_book(
    data: BookCreate,
    user_id: str = Depends(get_current_user_id),
    service: BookService = Depends(get_book_service),
    session: AsyncSession = Depends(get_db)
):
    # This matches the frontend expectation: { book: BookDetailDTO }
    # For now we reuse BookDTO as BookDetailDTO
    book_dto = await service.create_book(user_id, data.title, data.author or "", data.description or "", data.is_public)
    await session.commit()
    return {"book": book_dto}

@router.post("/{book_id}/upload", response_model=JobStatusDTO, status_code=202)
async def upload_book_file(
    book_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: BookService = Depends(get_book_service),
    session: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith((".pdf", ".epub", ".txt")):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    job_status = await service.upload_book_file(book_id, user_id, file)
    await session.commit()
    
    # We no longer spawn a background task here because the separate ingestion_worker.py
    # daemon polling the graph_build_jobs table will pick up this QUEUED job.
    
    return job_status

@router.get("/{book_id}/status", response_model=BookStatusDTO)
async def get_book_status(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    service: BookService = Depends(get_book_service)
):
    status = await service.get_book_processing_status(book_id)
    if not status:
        raise HTTPException(status_code=404, detail="Book processing status not found")
    return status

@router.get("/{book_id}/graph", response_model=GraphDTO)
async def get_book_graph(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db)
):
    from sqlalchemy import text
    
    # Verify ownership
    check = await session.execute(text(
        'SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid'
    ), {"uid": user_id, "bid": book_id})
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
    
    service = BookService(BookRepository(session))
    return await service.get_book_graph(book_id)

@router.post("/{book_id}/graph/sync-neo4j")
async def sync_graph_to_neo4j(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Project this book's graph + the caller's mastery state into Neo4j.
    Postgres remains the source of truth; this is a best-effort projection."""
    from app.services.neo4j_projection import project_book_graph, project_user_state

    repo = GraphRepository(session)
    if not await repo.is_enrolled(user_id, book_id):
        raise HTTPException(status_code=404, detail="Book not found in your library")
    gv = await repo.active_graph_version(book_id)
    if gv is None:
        raise HTTPException(status_code=409, detail="Knowledge graph not built yet")

    concepts = await repo.concepts(book_id, gv)
    edges = await repo.prerequisite_edges(book_id, gv)
    states = await repo.node_states(user_id, book_id)
    masteries = await repo.masteries(user_id, book_id)

    concept_dicts = [{"id": str(c.id), "name": c.name, "difficulty": c.difficulty_level} for c in concepts]
    edge_tuples = [(str(e.from_concept_id), str(e.to_concept_id)) for e in edges]
    mastery_rows = [{"concept_id": cid, "score": score, "state": states.get(cid, "")}
                    for cid, (score, _lr) in masteries.items()]
    in_progress = [cid for cid, st in states.items() if st == "IN_PROGRESS"]

    book_ok = await project_book_graph(book_id, concept_dicts, edge_tuples)
    user_ok = await project_user_state(user_id, mastery_rows, in_progress)
    return {"bookProjected": book_ok, "userProjected": user_ok,
            "concepts": len(concept_dicts), "edges": len(edge_tuples)}


@router.get("/{book_id}/knowledge-graph", response_model=PersonalGraphDTO)
async def get_personal_knowledge_graph(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Personalized graph reveal: nodes + edges overlaid with this user's
    per-concept state and mastery (four-state coloring for the map view)."""
    service = GraphRevealService(GraphRepository(session))
    return await service.get_personal_graph(user_id, book_id)


@router.post("/{book_id}/graph/confirm")
async def confirm_book_graph(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db)
):
    from sqlalchemy import text
    
    # 1. Update book status to READY
    await session.execute(text('''
        UPDATE books SET status = 'READY' WHERE id = :bid
    '''), {"bid": book_id})
    
    # 2. Seed the initial graph reveal: root concepts (no unmet prerequisite)
    #    start AVAILABLE, everything downstream starts LOCKED. The assessment
    #    refines these afterwards. (Seeding everything LOCKED would leave the
    #    graph fully gated with no entry point before assessment.)
    await session.execute(text('''
        INSERT INTO user_concept_state (user_id, concept_id, graph_version, state)
        SELECT :uid, c.id, c.graph_version,
               (CASE WHEN NOT EXISTS (
                        SELECT 1 FROM concept_edges e
                        WHERE e.to_concept_id = c.id
                          AND e.edge_type = 'PREREQUISITE'
                          AND e.book_id = c.book_id
                          AND e.graph_version = c.graph_version
                     ) THEN 'AVAILABLE' ELSE 'LOCKED' END)::node_state
        FROM concepts c
        WHERE c.book_id = :bid
        ON CONFLICT (user_id, concept_id, graph_version) DO NOTHING
    '''), {"uid": user_id, "bid": book_id})

    await session.commit()
    return {"success": True}

@router.post("/{book_id}/graph/nodes", status_code=201)
async def create_graph_node(
    book_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Create a new concept node in the book's knowledge graph."""
    from sqlalchemy import text
    import uuid
 
    # Verify ownership
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    # Get active graph version
    gv_row = await session.execute(
        text("SELECT graph_version FROM concepts WHERE book_id = :bid LIMIT 1"),
        {"bid": book_id},
    )
    gv = gv_row.scalar()
    if gv is None:
        raise HTTPException(status_code=409, detail="Knowledge graph not built yet")
 
    node_id = str(uuid.uuid4())
    await session.execute(
        text("""
            INSERT INTO concepts (id, book_id, graph_version, name, summary, difficulty_level, section_name, order_index)
            VALUES (:id, :book_id, :gv, :name, :summary, :difficulty, :section, 0)
        """),
        {
            "id": node_id,
            "book_id": book_id,
            "gv": gv,
            "name": data.get("title", "New Concept"),
            "summary": data.get("summary", ""),
            "difficulty": data.get("difficultyTier", "beginner"),
            "section": data.get("sectionName", None),
        },
    )
    await session.commit()
    return {"node": {"id": node_id, "title": data.get("title"), "summary": data.get("summary")}}
 
 
@router.patch("/{book_id}/graph/nodes/{node_id}")
async def update_graph_node(
    book_id: str,
    node_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update an existing concept node's title, summary, or difficulty."""
    from sqlalchemy import text
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    updates = []
    params = {"node_id": node_id, "book_id": book_id}
    if "title" in data:
        updates.append("name = :name")
        params["name"] = data["title"]
    if "summary" in data:
        updates.append("summary = :summary")
        params["summary"] = data["summary"]
    if "difficultyTier" in data:
        updates.append("difficulty_level = :difficulty")
        params["difficulty"] = data["difficultyTier"]
    if "sectionName" in data:
        updates.append("section_name = :section")
        params["section"] = data["sectionName"]
 
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
 
    await session.execute(
        text(f"UPDATE concepts SET {', '.join(updates)} WHERE id = :node_id AND book_id = :book_id"),
        params,
    )
    await session.commit()
    return {"node": {"id": node_id, **data}}
 
 
@router.delete("/{book_id}/graph/nodes/{node_id}", status_code=200)
async def delete_graph_node(
    book_id: str,
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Delete a concept node and all its edges."""
    from sqlalchemy import text
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    # Delete edges first (foreign key safety)
    await session.execute(
        text("DELETE FROM concept_edges WHERE from_concept_id = :nid OR to_concept_id = :nid"),
        {"nid": node_id},
    )
    await session.execute(
        text("DELETE FROM concepts WHERE id = :nid AND book_id = :bid"),
        {"nid": node_id, "bid": book_id},
    )
    await session.commit()
    return {"success": True}
 
 
# ── Edge CRUD ─────────────────────────────────────────────────────────────────
 
@router.post("/{book_id}/graph/edges", status_code=201)
async def create_graph_edge(
    book_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Add a prerequisite edge between two nodes. Rejects if it creates a cycle."""
    from sqlalchemy import text
    import uuid
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    from_id = data.get("fromNodeId")
    to_id = data.get("toNodeId")
    if not from_id or not to_id:
        raise HTTPException(status_code=400, detail="fromNodeId and toNodeId are required")
 
    # Cycle check: if to_id can already reach from_id, adding this edge creates a cycle
    cycle_check = await session.execute(
        text("""
            WITH RECURSIVE reachable AS (
                SELECT to_concept_id AS node_id FROM concept_edges WHERE from_concept_id = :to_id AND book_id = :bid
                UNION
                SELECT e.to_concept_id FROM concept_edges e
                JOIN reachable r ON e.from_concept_id = r.node_id
                WHERE e.book_id = :bid
            )
            SELECT 1 FROM reachable WHERE node_id = :from_id
        """),
        {"to_id": to_id, "from_id": from_id, "bid": book_id},
    )
    if cycle_check.fetchone():
        raise HTTPException(status_code=409, detail="This edge would create a cycle in the prerequisite graph")
 
    # Get graph version
    gv_row = await session.execute(
        text("SELECT graph_version FROM concepts WHERE id = :nid LIMIT 1"),
        {"nid": from_id},
    )
    gv = gv_row.scalar()
 
    edge_id = str(uuid.uuid4())
    await session.execute(
        text("""
            INSERT INTO concept_edges (id, book_id, graph_version, from_concept_id, to_concept_id, edge_type, weight, confidence)
            VALUES (:id, :book_id, :gv, :from_id, :to_id, :edge_type, 1.0, :confidence)
        """),
        {
            "id": edge_id,
            "book_id": book_id,
            "gv": gv,
            "from_id": from_id,
            "to_id": to_id,
            "edge_type": data.get("type", "PREREQUISITE").upper(),
            "confidence": data.get("confidence", 0.8),
        },
    )
    await session.commit()
    return {"edge": {"id": edge_id, "fromNodeId": from_id, "toNodeId": to_id}}
 
 
@router.patch("/{book_id}/graph/edges/{edge_id}")
async def update_graph_edge(
    book_id: str,
    edge_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update an edge's type or confidence score."""
    from sqlalchemy import text
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    updates = []
    params = {"edge_id": edge_id, "book_id": book_id}
    if "type" in data:
        updates.append("edge_type = :edge_type")
        params["edge_type"] = data["type"].upper()
    if "confidence" in data:
        updates.append("confidence = :confidence")
        params["confidence"] = data["confidence"]
 
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
 
    await session.execute(
        text(f"UPDATE concept_edges SET {', '.join(updates)} WHERE id = :edge_id AND book_id = :book_id"),
        params,
    )
    await session.commit()
    return {"edge": {"id": edge_id, **data}}
 
 
@router.delete("/{book_id}/graph/edges/{edge_id}", status_code=200)
async def delete_graph_edge(
    book_id: str,
    edge_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Remove an edge from the knowledge graph."""
    from sqlalchemy import text
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    await session.execute(
        text("DELETE FROM concept_edges WHERE id = :eid AND book_id = :bid"),
        {"eid": edge_id, "bid": book_id},
    )
    await session.commit()
    return {"success": True}
 
 
# ── Chat-based editing ────────────────────────────────────────────────────────
 
@router.post("/{book_id}/graph/chat")
async def graph_chat_edit(
    book_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Parse a plain-English edit command and return a proposed change.
    The frontend shows this to the user for confirmation before applying.
 
    Example inputs:
    - "delete the node about Recursion"
    - "add an edge from Arrays to Sorting"
    - "rename 'Linked List' to 'Singly Linked List'"
    - "merge Binary Search and Linear Search into Searching Algorithms"
    """
    from sqlalchemy import text
    from google import genai
 
    message = data.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
 
    check = await session.execute(
        text("SELECT 1 FROM user_books WHERE user_id = :uid AND book_id = :bid"),
        {"uid": user_id, "bid": book_id},
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Book not found in your library")
 
    # Fetch current nodes and edges to give the LLM context
    nodes_result = await session.execute(
        text("SELECT id, name, summary FROM concepts WHERE book_id = :bid ORDER BY order_index"),
        {"bid": book_id},
    )
    nodes = [{"id": str(r.id), "title": r.name, "summary": r.summary} for r in nodes_result]
 
    edges_result = await session.execute(
        text("""
            SELECT e.id, e.from_concept_id, e.to_concept_id, e.edge_type, e.confidence,
                   cf.name as from_name, ct.name as to_name
            FROM concept_edges e
            JOIN concepts cf ON cf.id = e.from_concept_id
            JOIN concepts ct ON ct.id = e.to_concept_id
            WHERE e.book_id = :bid
        """),
        {"bid": book_id},
    )
    edges = [
        {
            "id": str(r.id),
            "fromNodeId": str(r.from_concept_id),
            "toNodeId": str(r.to_concept_id),
            "fromTitle": r.from_name,
            "toTitle": r.to_name,
            "type": r.edge_type,
        }
        for r in edges_result
    ]
 
    import os, json
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
 
    prompt = f"""You are a knowledge graph editor assistant.
 
The user wants to edit a knowledge graph. Given their instruction and the current graph,
return a JSON object describing what change to make.
 
Current nodes (id, title):
{json.dumps([{"id": n["id"], "title": n["title"]} for n in nodes], indent=2)}
 
Current edges (id, fromTitle -> toTitle):
{json.dumps([{"id": e["id"], "from": e["fromTitle"], "to": e["toTitle"]} for e in edges], indent=2)}
 
User instruction: "{message}"
 
Respond ONLY with a JSON object in this exact format (no markdown, no explanation):
{{
  "action": "delete_node" | "update_node" | "delete_edge" | "create_edge" | "rename_node",
  "description": "Human-readable summary of what will change",
  "nodeId": "uuid if action involves a node",
  "edgeId": "uuid if action involves an edge",  
  "fromNodeId": "uuid if creating an edge",
  "toNodeId": "uuid if creating an edge",
  "newTitle": "new title if renaming",
  "newSummary": "new summary if updating"
}}
 
If you cannot match the instruction to any node or edge, return:
{{"action": "unknown", "description": "Could not find matching nodes or edges. Please be more specific."}}
"""
 
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        proposal = json.loads(raw.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM parsing failed: {str(e)}")
 
    return {"proposal": proposal}
 
 
@router.get("", response_model=dict)
async def get_user_books(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db)
):
    service = BookService(BookRepository(session))
    books = await service.book_repo.get_books_by_user(user_id)
    summaries = []
    for b in books:
        status_str = getattr(b, 'status', 'UPLOADING').lower()
        if status_str == 'uploading':
            status_str = 'uploaded'
            
        summaries.append(BookSummaryDTO(
            id=str(b.id),
            title=b.title,
            author=b.author,
            coverUrl=None,
            status=status_str,
            progress=0,
            totalNodes=0,
            masteredNodes=0,
            dueToday=0,
            lastStudied=None,
            createdAt=b.created_at.isoformat()
        ).model_dump(by_alias=True))
        
    return {"books": summaries}

@router.get("/{book_id}", response_model=dict)
async def get_book(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db)
):
    service = BookService(BookRepository(session))
    # Ownership check
    user_book = await service.book_repo.get_user_book(user_id, book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in your library")
        
    book = await service.book_repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    from sqlalchemy import text
    states = await session.execute(text('''
        SELECT ucs.concept_id, ucs.state 
        FROM user_concept_state ucs
        JOIN concepts c ON c.id = ucs.concept_id
        WHERE ucs.user_id = :uid AND c.book_id = :bid
    '''), {"uid": user_id, "bid": book_id})
    
    nodes = []
    for r in states:
        nodes.append({
            "id": str(r.concept_id),
            "userNodeStates": [{
                "nodeId": str(r.concept_id),
                "state": r.state
            }]
        })
        
    return {
        "book": BookDetailDTO(
            id=str(book.id),
            title=book.title,
            author=book.author,
            description=book.description,
            source_type=book.source_type,
            file_url=book.file_url,
            created_at=book.created_at,
            nodes=nodes
        ).model_dump()
    }

@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db)
):
    from sqlalchemy import text
    
    # Verify ownership via user_books
    result = await session.execute(text('''
        SELECT ub.id, b.owner_id
        FROM user_books ub
        JOIN books b ON b.id = ub.book_id
        WHERE ub.user_id = :uid AND ub.book_id = :bid
    '''), {"uid": user_id, "bid": book_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Book not found in your library")
    
    user_book_id, owner_id = row
    
    # Remove from user's library
    await session.execute(
        text('DELETE FROM user_books WHERE id = :id'),
        {"id": str(user_book_id)}
    )
    
    # If this user owns the book, delete it entirely (cascades to all children)
    if str(owner_id) == user_id:
        await session.execute(
            text('DELETE FROM books WHERE id = :id'),
            {"id": book_id}
        )
    
    await session.commit()
    return None
