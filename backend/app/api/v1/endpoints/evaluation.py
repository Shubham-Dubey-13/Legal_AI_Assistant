"""
Evaluation endpoint — runs the LegalAI system against the curated eval set
and returns retrieval, citation, and answer quality metrics.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from app.core.security import get_current_user
import json, os, re, time

router = APIRouter()

EVAL_SET_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../../../data/eval/eval_set.json"
)


@router.get("/metrics")
async def get_evaluation_metrics(current_user: dict = Depends(get_current_user)):
    """
    Return pre-computed evaluation metrics.
    Run /evaluation/run first to generate fresh results.
    """
    results_path = os.path.join(os.path.dirname(EVAL_SET_PATH), "eval_results.json")
    if os.path.exists(results_path):
        with open(results_path) as f:
            return json.load(f)

    return {
        "status": "not_run",
        "message": "Run POST /api/v1/evaluation/run to generate metrics",
        "metrics": {
            "section_recall": None,
            "keyword_coverage": None,
            "abstain_rate": None,
            "total_questions": 50,
        }
    }


@router.post("/run")
async def run_evaluation(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    max_questions: int = 10,
):
    """
    Run evaluation on the eval set (background task).
    max_questions: limit for quick testing (default 10, max 50).
    """
    max_questions = min(max_questions, 50)
    background_tasks.add_task(_run_eval_background, max_questions)
    return {
        "status": "started",
        "message": f"Evaluation running on {max_questions} questions in background. Check /evaluation/metrics for results.",
        "max_questions": max_questions,
    }


async def _run_eval_background(max_questions: int):
    """Run eval and save results to disk."""
    from ai_services.agents.orchestrator import LegalOrchestrator

    if not os.path.exists(EVAL_SET_PATH):
        return

    with open(EVAL_SET_PATH) as f:
        data = json.load(f)

    questions = data["eval_set"][:max_questions]
    orchestrator = LegalOrchestrator()

    results = []
    section_hits = 0
    keyword_hits = 0
    total_sections = 0
    total_keywords = 0
    abstain_count = 0

    for q in questions:
        t0 = time.time()
        try:
            result = await orchestrator.process_query(
                query=q["question"],
                user_id="eval-system",
                language="en",
            )
            response = result.get("response", "")
            elapsed = int((time.time() - t0) * 1000)

            # Check if abstained
            if "Insufficient Evidence" in response or "Out of Scope" in response:
                abstain_count += 1

            # Section recall: how many expected sections appear in response
            expected_sections = q.get("expected_sections", [])
            found_sections = []
            for sec in expected_sections:
                # Normalize: "BNS 316" matches "BNS 316" or "BNS Section 316"
                num = re.search(r'\d+', sec)
                if num and num.group() in response:
                    found_sections.append(sec)
                    section_hits += 1
            total_sections += len(expected_sections)

            # Keyword coverage: how many expected keywords appear in response
            expected_kw = q.get("expected_keywords", [])
            found_kw = [kw for kw in expected_kw if kw.lower() in response.lower()]
            keyword_hits += len(found_kw)
            total_keywords += len(expected_kw)

            results.append({
                "id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "sections_found": found_sections,
                "sections_expected": expected_sections,
                "keywords_found": found_kw,
                "keywords_expected": expected_kw,
                "abstained": "Insufficient Evidence" in response,
                "response_length": len(response),
                "latency_ms": elapsed,
                "confidence": result.get("confidence_score", 0),
            })
        except Exception as e:
            results.append({
                "id": q["id"],
                "category": q["category"],
                "error": str(e),
            })

    # Compute aggregate metrics
    section_recall = round(section_hits / total_sections, 3) if total_sections > 0 else 0
    keyword_coverage = round(keyword_hits / total_keywords, 3) if total_keywords > 0 else 0
    abstain_rate = round(abstain_count / len(questions), 3) if questions else 0
    avg_latency = round(
        sum(r.get("latency_ms", 0) for r in results) / len(results), 1
    ) if results else 0

    # Category breakdown
    cat_stats = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "section_hits": 0, "total_sections": 0}
        cat_stats[cat]["count"] += 1

    output = {
        "status": "completed",
        "run_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "questions_evaluated": len(results),
        "metrics": {
            "section_recall": section_recall,
            "keyword_coverage": keyword_coverage,
            "abstain_rate": abstain_rate,
            "avg_latency_ms": avg_latency,
        },
        "interpretation": {
            "section_recall": f"{section_recall*100:.1f}% of expected IPC/BNS sections found in responses",
            "keyword_coverage": f"{keyword_coverage*100:.1f}% of expected legal keywords present",
            "abstain_rate": f"{abstain_rate*100:.1f}% of queries triggered abstain/out-of-scope response",
        },
        "per_question_results": results,
    }

    results_path = os.path.join(os.path.dirname(EVAL_SET_PATH), "eval_results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Evaluation complete: section_recall={section_recall}, keyword_coverage={keyword_coverage}")
