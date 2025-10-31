"""
Entry point principal para AI Dev Team.

Uso:
    python -m src.main "Crear una aplicación de gestión de tareas"
    python -m src.main "Build a blog platform with user authentication"
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from src.state import create_initial_state
from src.graph import compile_workflow, WORKFLOW_DIAGRAM


console = Console()


def save_artifacts(state: dict, output_dir: str):
    """Guarda los artefactos del proyecto"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Guardar resumen
    summary_file = output_path / "PROJECT_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(state.get('project_summary', 'No summary available'))
    
    console.print(f"\n📄 Resumen guardado en: [cyan]{summary_file}[/cyan]")
    
    # Guardar user stories
    import json
    stories_file = output_path / "user_stories.json"
    with open(stories_file, 'w') as f:
        json.dump(state.get('user_stories', []), f, indent=2)
    
    console.print(f"📋 User stories en: [cyan]{stories_file}[/cyan]")
    
    # Guardar tasks
    tasks_file = output_path / "tasks.json"
    with open(tasks_file, 'w') as f:
        json.dump(state.get('tasks', []), f, indent=2)
    
    console.print(f"✅ Tareas en: [cyan]{tasks_file}[/cyan]")
    
    # Guardar metadata
    metadata_file = output_path / "metadata.json"
    metadata = {
        'project_name': state['project_name'],
        'user_requirement': state['user_requirement'],
        'user_stories_count': len(state.get('user_stories', [])),
        'tasks_count': len(state.get('tasks', [])),
        'backend_files_count': len(state.get('backend_files', [])),
        'frontend_files_count': len(state.get('frontend_files', [])),
        'test_files_count': len(state.get('test_files', [])),
        'test_coverage': state.get('test_coverage', 0),
        'deployment_ready': state.get('deployment_ready', False),
        'errors': state.get('errors', []),
    }
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    console.print(f"📊 Metadata en: [cyan]{metadata_file}[/cyan]")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Dev Team - Equipo de desarrollo de software automatizado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Desarrollo completo
  python -m src.main "Crear una app de gestión de tareas"
  
  # Con nombre de proyecto personalizado
  python -m src.main "Blog platform" --name "my-blog"
  
  # Especificar workspace
  python -m src.main "E-commerce site" --workspace ./projects
  
  # Ver diagrama del workflow
  python -m src.main --show-workflow
        """
    )
    
    parser.add_argument(
        'requirement',
        nargs='?',
        help='Requerimiento del usuario para el proyecto'
    )
    
    parser.add_argument(
        '--name',
        default=None,
        help='Nombre del proyecto (default: generado automáticamente)'
    )
    
    parser.add_argument(
        '--workspace',
        default='./workspace',
        help='Directorio workspace (default: ./workspace)'
    )
    
    parser.add_argument(
        '--output',
        default='./output',
        help='Directorio para guardar artefactos (default: ./output)'
    )
    
    parser.add_argument(
        '--show-workflow',
        action='store_true',
        help='Mostrar diagrama del workflow y salir'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Parse argumentos
    args = parse_args()
    
    # Si solo quiere ver el workflow
    if args.show_workflow:
        console.print(WORKFLOW_DIAGRAM)
        return 0
    
    # Validar que se proveyó un requerimiento
    if not args.requirement:
        console.print("[red]Error: Debes proporcionar un requerimiento[/red]")
        console.print("Uso: python -m src.main \"Tu requerimiento aquí\"")
        console.print("O usa --help para ver todas las opciones")
        return 1
    
    # Validar API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        console.print("[red]Error: ANTHROPIC_API_KEY no está configurada[/red]")
        console.print("Crea un archivo .env con tu API key:")
        console.print("  ANTHROPIC_API_KEY=tu_key_aqui")
        return 1
    
    # Generar nombre del proyecto si no se proveyó
    project_name = args.name
    if not project_name:
        # Generar nombre simple desde el requerimiento
        words = args.requirement.lower().split()[:3]
        project_name = "-".join(words)
        project_name = "".join(c for c in project_name if c.isalnum() or c == '-')
    
    # Banner de inicio
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🤖 AI Dev Team[/bold cyan]\n"
        "[dim]Equipo de desarrollo de software automatizado[/dim]\n"
        "[dim]LangGraph + Claude Agent SDK[/dim]",
        border_style="cyan"
    ))
    
    console.print(f"\n📋 Requerimiento: [cyan]{args.requirement}[/cyan]")
    console.print(f"📦 Proyecto: [yellow]{project_name}[/yellow]")
    console.print(f"📁 Workspace: [cyan]{args.workspace}[/cyan]")
    
    # Crear estado inicial
    initial_state = create_initial_state(
        user_requirement=args.requirement,
        project_name=project_name,
        workspace_path=args.workspace
    )
    
    # Compilar workflow
    console.print("\n⚙️  Compilando workflow...")
    app = compile_workflow()
    
    # Ejecutar el equipo de desarrollo
    console.print("\n🚀 Iniciando desarrollo...\n")
    console.print("="*70)
    
    try:
        # Ejecutar el workflow
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Equipo trabajando...", total=None)
            
            # Invocar el grafo
            final_state = app.invoke(initial_state)
            
            progress.update(task, description="✅ Desarrollo completado")
        
        console.print("="*70)
        
        # Mostrar resumen
        console.print("\n")
        console.print(Panel.fit(
            "[bold green]✅ Proyecto Completado[/bold green]",
            border_style="green"
        ))
        
        # Mostrar el resumen del proyecto
        if final_state.get('project_summary'):
            console.print("\n[bold cyan]📋 Resumen del Proyecto:[/bold cyan]\n")
            console.print(Markdown(final_state['project_summary']))
        
        # Guardar artefactos
        console.print("\n💾 Guardando artefactos...")
        save_artifacts(final_state, args.output)
        
        # Mostrar estadísticas finales
        console.print("\n[bold]📊 Estadísticas:[/bold]")
        console.print(f"  👔 User Stories: {len(final_state.get('user_stories', []))}")
        console.print(f"  📋 Tareas: {len(final_state.get('tasks', []))}")
        console.print(f"  🔧 Backend files: {len(final_state.get('backend_files', []))}")
        console.print(f"  🎨 Frontend files: {len(final_state.get('frontend_files', []))}")
        console.print(f"  🧪 Test files: {len(final_state.get('test_files', []))}")
        
        coverage = final_state.get('test_coverage', 0)
        color = "green" if coverage >= 0.8 else "yellow" if coverage >= 0.6 else "red"
        console.print(f"  📊 Test coverage: [{color}]{coverage*100:.1f}%[/{color}]")
        
        if final_state.get('deployment_ready'):
            console.print("\n[bold green]🎉 ¡Proyecto listo para deployment![/bold green]")
        else:
            console.print("\n[bold yellow]⚠️  Proyecto requiere revisión adicional[/bold yellow]")
        
        if final_state.get('errors'):
            console.print(f"\n[red]⚠️  {len(final_state['errors'])} error(es) durante el desarrollo[/red]")
        
        console.print("\n[bold green]✨ ¡Desarrollo exitoso![/bold green]\n")
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n\n[bold red]❌ Desarrollo interrumpido por usuario[/bold red]")
        return 130
    
    except Exception as e:
        console.print(f"\n\n[bold red]❌ Error durante el desarrollo:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        
        if '--debug' in sys.argv:
            import traceback
            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        
        return 1


if __name__ == '__main__':
    sys.exit(main())