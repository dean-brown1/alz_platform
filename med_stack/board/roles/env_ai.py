from core.models.provider import ModelRunner
from core.schemas.case_bundle import CaseBundle
from med_stack.schemas.role_output import RoleOutput
def analyze(case: CaseBundle) -> dict:
    runner = ModelRunner()
    system = "You are a specialist AI. Respond in strict JSON with keys: findings, notes."
    relevant = [o.content for o in case.observations if o.modality == "environment"]
    prompt = f"Role: env_ai\nModalities: {case.modalities}\nObservations: {relevant}"
    out = runner.chat_json(system, prompt)
    try:
        ro = RoleOutput.model_validate(out)
        return {"role": "env_ai", "raw": ro.model_dump()}
    except Exception:
        return {"role": "env_ai", "raw": out}
