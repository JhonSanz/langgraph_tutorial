"""
Estado del equipo de desarrollo de software.
Define toda la información que fluye entre los diferentes roles.
"""

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime


class Epic(TypedDict):
    """Una épica que agrupa user stories relacionadas"""

    id: str
    name: str
    business_objective: str
    user_stories: List[str]  # IDs de las user stories
    success_metrics: List[str]
    dependencies: List[str]


class TechnicalContext(TypedDict):
    """Contexto técnico de una user story"""

    stack: str  # "Backend", "Frontend", "Both", "Infrastructure"
    components: List[str]  # Módulos o componentes afectados
    apis_endpoints: List[str]  # URLs y métodos HTTP
    data_models: List[str]  # Entidades de BD involucradas


class AcceptanceCriterion(TypedDict):
    """Criterio de aceptación en formato DADO-CUANDO-ENTONCES"""

    given: str  # Contexto/precondición
    when: str  # Acción del usuario
    then: str  # Resultado esperado


class TestScenario(TypedDict):
    """Escenario de prueba"""

    type: Literal["happy_path", "edge_case", "error_handling"]
    description: str


class Dependency(TypedDict):
    """Dependencia de una user story"""

    requires: List[str]  # IDs de historias que deben completarse antes
    blocks: List[str]  # IDs de historias que dependen de esta


class Risk(TypedDict):
    """Riesgo identificado y su mitigación"""

    description: str
    impact: Literal["high", "medium", "low"]
    mitigation: str


class UserStory(TypedDict):
    """Una historia de usuario mejorada con contexto completo"""

    id: str
    epic_id: str  # Relación con épica
    title: str
    description: str  # Formato: "Como [rol], quiero [acción], para [beneficio]"
    technical_context: TechnicalContext
    acceptance_criteria: List[AcceptanceCriterion]
    definition_of_done: List[str]
    test_scenarios: List[TestScenario]
    dependencies: Dependency
    risks: List[Risk]
    technical_notes: str
    ux_ui_criteria: List[str]  # Criterios de UX/UI si aplican
    priority: Literal["high", "medium", "low"]
    priority_justification: str
    estimated_points: int
    estimation_breakdown: str  # Justificación de la estimación


class Task(TypedDict):
    """Una tarea asignada a un developer"""
    id: str
    user_story_id: str
    title: str
    description: str
    assigned_to: Literal["backend", "frontend"]
    status: Literal["pending", "in_progress", "completed"]
    dependencies: List[str]  # IDs de otras tareas


class CodeFile(TypedDict):
    """Un archivo de código generado"""
    path: str
    content: str
    language: str
    created_by: str


class TestFile(TypedDict):
    """Un archivo de test generado"""
    path: str
    content: str
    test_type: Literal["unit", "integration", "e2e"]
    coverage_target: float


class DevelopmentState(TypedDict):
    """Estado completo del proyecto de desarrollo"""
    
    # Input inicial
    user_requirement: str
    project_name: str
    workspace_path: str
    
    # Fase 1: Product Manager
    user_stories: List[UserStory]
    product_backlog_created: bool
    
    # Fase 2: Scrum Master
    tasks: List[Task]
    sprint_planned: bool
    current_sprint: int
    
    # Fase 3: Backend Development
    backend_files: List[CodeFile]
    backend_completed: bool
    backend_tech_stack: Dict[str, str]  # e.g., {"framework": "FastAPI", "database": "PostgreSQL"}
    
    # Fase 4: Frontend Development
    frontend_files: List[CodeFile]
    frontend_completed: bool
    frontend_tech_stack: Dict[str, str]  # e.g., {"framework": "React", "styling": "TailwindCSS"}
    
    # Fase 5: QA
    test_files: List[TestFile]
    test_coverage: float
    qa_completed: bool
    bugs_found: List[str]
    
    # Control de flujo
    needs_clarification: bool
    clarification_questions: List[str]
    human_review_needed: bool
    human_approved: bool
    
    # Metadata
    created_at: str
    updated_at: str
    errors: List[str]
    
    # Output final
    project_summary: str
    deployment_ready: bool


def create_initial_state(
    user_requirement: str,
    project_name: str,
    workspace_path: str = "./workspace"
) -> DevelopmentState:
    """Crea el estado inicial del proyecto"""
    
    timestamp = datetime.now().isoformat()
    
    return DevelopmentState(
        # Input
        user_requirement=user_requirement,
        project_name=project_name,
        workspace_path=workspace_path,
        
        # Fase 1
        user_stories=[],
        product_backlog_created=False,
        
        # Fase 2
        tasks=[],
        sprint_planned=False,
        current_sprint=1,
        
        # Fase 3
        backend_files=[],
        backend_completed=False,
        backend_tech_stack={
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "orm": "SQLAlchemy"
        },
        
        # Fase 4
        frontend_files=[],
        frontend_completed=False,
        frontend_tech_stack={
            "framework": "React",
            "styling": "TailwindCSS",
            "state": "Redux"
        },
        
        # Fase 5
        test_files=[],
        test_coverage=0.0,
        qa_completed=False,
        bugs_found=[],
        
        # Control
        needs_clarification=False,
        clarification_questions=[],
        human_review_needed=False,
        human_approved=False,
        
        # Metadata
        created_at=timestamp,
        updated_at=timestamp,
        errors=[],
        
        # Output
        project_summary="",
        deployment_ready=False
    )

