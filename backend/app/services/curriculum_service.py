"""
Curriculum + Daily Plan orchestration (System Design Section G).

Deterministic: the learning order and gating come entirely from the prerequisite
DAG + the learner's mastery state (curriculum_planner). The graph decides the
curriculum; this service just loads state, runs the planner, and persists.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import HTTPException

from app.models.curriculum import CurriculumPlan
from app.repositories.graph_repo import GraphRepository
from app.repositories.curriculum_repo import CurriculumRepository
from app.services import curriculum_planner as planner
from app.schemas.curriculum import CurriculumItemDTO, CurriculumDTO, DailyPlanDTO


class CurriculumService:
    def __init__(self, graph_repo: GraphRepository, curr_repo: CurriculumRepository):
        self.graph = graph_repo
        self.repo = curr_repo

    async def _load_items(self, user_id: str, book_id: str):
        if not await self.graph.is_enrolled(user_id, book_id):
            raise HTTPException(status_code=404, detail="Book not found in your library.")
        gv = await self.graph.active_graph_version(book_id)
        if gv is None:
            raise HTTPException(status_code=409, detail="Knowledge graph not built for this book yet.")
        concepts = await self.graph.concepts(book_id, gv)
        edges = await self.graph.prerequisite_edges(book_id, gv)
        states = await self.graph.node_states(user_id, book_id)
        masteries = {cid: score for cid, (score, _lr) in (await self.graph.masteries(user_id, book_id)).items()}

        concept_dicts = [
            {"id": str(c.id), "title": c.name, "estimated_minutes": c.estimated_minutes}
            for c in concepts
        ]
        edge_tuples = [(str(e.from_concept_id), str(e.to_concept_id)) for e in edges]
        items = planner.build_curriculum(concept_dicts, edge_tuples, states, masteries)
        return items

    @staticmethod
    def _item_dto(it: planner.CurriculumItem) -> CurriculumItemDTO:
        return CurriculumItemDTO(
            conceptId=it.concept_id, title=it.title, orderIndex=it.order_index,
            state=it.state, mastery=it.mastery, estimatedMinutes=it.estimated_minutes,
            unmetPrerequisites=it.unmet_prerequisites,
        )

    async def generate_curriculum(self, user_id: str, book_id: str) -> CurriculumDTO:
        items = await self._load_items(user_id, book_id)
        version = await self.repo.next_version(user_id, book_id)
        assessment_id = await self.repo.latest_assessment_id(user_id, book_id)
        curriculum_json = [asdict(it) for it in items]
        await self.repo.create_plan(CurriculumPlan(
            user_id=user_id, book_id=book_id, version=version,
            curriculum_json=curriculum_json, generated_from_assessment=assessment_id,
        ))
        return self._to_dto(book_id, version, items)

    async def get_curriculum(self, user_id: str, book_id: str) -> CurriculumDTO:
        plan = await self.repo.latest_plan(user_id, book_id)
        if plan is None:
            # Generate-on-read so the course view always has data post-assessment.
            return await self.generate_curriculum(user_id, book_id)
        items = [
            planner.CurriculumItem(
                concept_id=i["concept_id"], title=i["title"], order_index=i["order_index"],
                state=i["state"], mastery=i["mastery"], estimated_minutes=i["estimated_minutes"],
                unmet_prerequisites=i.get("unmet_prerequisites", []),
            )
            for i in plan.curriculum_json
        ]
        return self._to_dto(book_id, plan.version, items)

    async def get_daily_plan(self, user_id: str, book_id: str) -> DailyPlanDTO:
        items = await self._load_items(user_id, book_id)  # live state, not stale plan
        cap = await self.repo.daily_new_node_cap(user_id)
        dp = planner.build_daily_plan(items, cap)
        return DailyPlanDTO(
            bookId=book_id, mode=dp.mode,
            revise=[self._item_dto(it) for it in dp.revise],
            learn=[self._item_dto(it) for it in dp.learn],
            totalDue=len(dp.revise), totalNew=len(dp.learn),
            estimatedMinutes=dp.estimated_minutes,
        )

    def _to_dto(self, book_id: str, version: int, items) -> CurriculumDTO:
        mastered = sum(1 for it in items if it.state == "MASTERED")
        return CurriculumDTO(
            bookId=book_id, version=version, totalConcepts=len(items),
            masteredConcepts=mastered, items=[self._item_dto(it) for it in items],
        )
