from exports.protocol_card_renderer import render_qrc_markdown, render_evidence_csv

SAMPLE = {
    "case_id": "patient-123",
    "stage": "MCI",
    "resilience_index": 0.67,
    "expected_life_expectancy_delta": -0.4,
    "candidate_protocols": [
        {"title": "Baseline Cognitive Support",
         "steps": ["Confirm diagnosis and stage", "Assess lifestyle factors"],
         "rationale": "Heuristic synthesis pending board consensus.",
         "risk_notes": "Monitor for GI side effects."}
    ],
    "evidence": [
        {"modality": "clinical", "source": "note-2024-03", "summary": "MoCA 20/30", "confidence": 0.7},
        {"modality": "imaging",  "source": "MRI-2021",     "summary": "Hippocampal atrophy", "confidence": 0.8},
    ],
    "limitations": ["Heuristic; boards not yet model-merged"],
    "reproducibility": {"modalities": ["clinical","imaging"], "hash": "abc123", "model": "meta-8b-longread"}
}

def test_qrc_basic():
    md = render_qrc_markdown(SAMPLE)
    assert "Protocol Card — Case patient-123" in md
    assert "Baseline Cognitive Support" in md
    assert "Resilience Index" in md
    assert "Reproducibility" in md

def test_csv_basic():
    csv_text = render_evidence_csv(SAMPLE)
    # header + 2 rows
    assert csv_text.count("\n") >= 3
    assert "clinical" in csv_text and "imaging" in csv_text
