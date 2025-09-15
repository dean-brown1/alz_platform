from core.models.provider import ModelRunner
from core.schemas.case_bundle import CaseBundle
from med_stack.schemas.role_output import RoleOutput
def analyze(case: CaseBundle) -> dict:
    runner = ModelRunner()
    system = "You are a specialist AI. Respond in strict JSON with keys: findings, notes."
    relevant = [o.content for o in case.observations if o.modality == "pharma"]
    prompt = f"Role: pharmaco_ai\nModalities: {case.modalities}\nObservations: {relevant}"
    out = runner.chat_json(system, prompt)
    try:
        ro = RoleOutput.model_validate(out)
        return {"role": "pharmaco_ai", "raw": ro.model_dump()}
    except Exception:
        return {"role": "pharmaco_ai", "raw": out}
