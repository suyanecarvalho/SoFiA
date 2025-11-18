import sys
from pathlib import Path

# --- CONFIGURATION ---

# Automatically detect paths relative to this script (which is at project root)
PROJECT_ROOT = Path(__file__).parent
# Target the backend folder seen in your screenshot
PYTHON_SRC_ROOT = PROJECT_ROOT / "apps" / "backend"

OUTPUT_PROMPT_FILE = "generated_prompt.txt"

# Describe what you want the AI to do with the generated context
task_description = """

when i send the message thru postman it works but on browser not

```

"""

def get_python_code_base(root_path):
    print(f"-> Scanning for Python files in: {root_path}")
    python_files_content = []

    if not root_path.is_dir():
        print(f"Error: Python source directory not found at '{root_path}'")
        return ""

    # Recursively find all .py files in apps/backend
    # Excluding virtual environment or standard exclude folders if they exist
    python_files = sorted(list(root_path.rglob("*.py")))

    # Optional: Filter out specific cache or venv folders if necessary
    python_files = [p for p in python_files if ".venv" not in p.parts and "__pycache__" not in p.parts]

    print(f"-> Found {len(python_files)} Python files.")

    for file_path in python_files:
        try:
            # Create a relative path for cleaner reading (e.g., "src/api/main.py")
            relative_path = file_path.relative_to(root_path)
            content = file_path.read_text(encoding="utf-8").strip()
            formatted_block = f"{relative_path}:\n\n```python\n{content}\n```\n\n---"
            python_files_content.append(formatted_block)
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")

    return "\n\n".join(python_files_content)


def create_final_prompt(task_description, python_code):
    """
    Assembles the final prompt adapting to the SoFiA Monorepo + FastAPI context.
    """
    prompt_template = f"""
### REFERENCE CONTEXT

#### Current 'SoFiA' Backend Codebase (FastAPI/Python)

The code below represents the contents of `apps/backend`.
The project is a Monorepo (Turborepo) structure.
Key technologies: Python, FastAPI, Docker, Poetry.

---

{python_code}

---

**WORKFLOW RULES (STRICT):**
    1. **PLAN → CODE**: Always outline the approach before writing code.
    2. **Context Awareness**: You are inside a Dockerized Monorepo. 
       - Imports usually start from `src.` or strict relative imports.
       - Dependencies are managed via `poetry`.

    ### PLAN
    - **Goal**: Brief description of the objective.
    - **Architecture**: Explain how changes affect the `api`, `db`, or `llm` modules.
    - **Steps**:
        1. Update Pydantic models...
        2. Modify Dockerfile (if needed)...
        3. Implement endpoints...

    ### CODE
    - Generate the necessary changes. 
    - If modifying existing files, show enough context to locate the change.
    - If creating new files, indicate the full path (e.g., `apps/backend/src/api/new_route.py`).

---

> **"SoFiA Project Context"**
    You are a Senior Software Architect and Backend Engineer specializing in Python microservices and Monorepos.

    Your goal is to maintain a high-performance, clean, and scalable FastAPI backend. 
    You strictly adhere to:
    - **Dependency Injection** for database sessions and services.
    - **Type Safety** using Pydantic and Python Type Hints.
    - Professional MVC setup and folder and file organzation, not making monolithic pieces of code and following DRY principles.

---

NEXT TASK: 

{task_description}

---

"""
    return prompt_template.strip()


def main():
    """
    Main function to orchestrate the prompt generation.
    """
    print("--- Starting SoFiA Context Generation ---")

    python_code = get_python_code_base(PYTHON_SRC_ROOT)

    if not python_code:
        print("No python code found. Check paths.")
        return

    print("-> Assembling the final implementation plan.")
    final_prompt = create_final_prompt(task_description, python_code)

    try:
        output_path = Path(OUTPUT_PROMPT_FILE)
        output_path.write_text(final_prompt, encoding="utf-8")
        print(f"-> Successfully wrote implementation plan to: {output_path.resolve()}")
    except Exception as e:
        print(f"Error writing to output file {OUTPUT_PROMPT_FILE}: {e}")
        return

    print("\n--- Generation Complete ---")


if __name__ == "__main__":
    main()