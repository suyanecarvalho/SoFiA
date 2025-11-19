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

```

Attaching to backend-1, frontend-1
backend-1  | Initializing Database...
frontend-1  | ! Corepack is about to download https://registry.npmjs.org/pnpm/-/pnpm-9.0.0.tgz
backend-1   | Connecting to the database and creating tables...
backend-1   | Database tables created successfully.
backend-1   | Seeding categories...
backend-1   |   Skipping 'Alimentação' (already exists).
backend-1   |   Skipping 'Transporte' (already exists).
backend-1   |   Skipping 'Contas de Casa' (already exists).
backend-1   |   Skipping 'Saúde' (already exists).
backend-1   |   Skipping 'Lazer & Entretenimento' (already exists).
backend-1   |   Skipping 'Educação' (already exists).
backend-1   | No new categories were added.
backend-1   | Starting Server...
frontend-1  | 
frontend-1  | > frontend@0.0.0 dev /app/apps/frontend
frontend-1  | > vite "--host"
frontend-1  | 
frontend-1  | 12:11:11 AM [vite] (client) Re-optimizing dependencies because lockfile has changed
frontend-1  | 
frontend-1  |   VITE v7.2.2  ready in 470 ms
frontend-1  | 
frontend-1  |   ➜  Local:   http://localhost:5173/
frontend-1  |   ➜  Network: http://172.18.0.2:5173/
backend-1   | INFO:     Started server process [1]
backend-1   | INFO:     Waiting for application startup.
backend-1   | INFO:     Application startup complete.
backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
backend-1   | {"timestamp": "2025-11-19T00:11:28.661550Z", "level": "INFO", "message": "Initializing LLM: remote (gemini-2.5-flash-lite)", "module": "chat_service"}
backend-1   | {"timestamp": "2025-11-19T00:11:31.166130Z", "level": "INFO", "message": "Raw Gemini JSON Response", "module": "remote_llm", "payload": {"text": "{\n  \"intent\": \"create_transaction\",\n  \"parameters\": {\n    \"amount\": 65.60,\n    \"description\": \"rod\u00edzio do Pizzaiolo\",\n    \"currency\": \"BRL\"\n  }\n}"}}
backend-1   | {"timestamp": "2025-11-19T00:11:31.166282Z", "level": "INFO", "message": "Intent Classification Result", "module": "chat_service", "payload": {"intent": "create_transaction", "parameters": {"amount": 65.6, "description": "rod\u00edzio do Pizzaiolo", "currency": "BRL"}}}
backend-1   | {"timestamp": "2025-11-19T00:11:31.166377Z", "level": "INFO", "message": "Creating transaction...", "module": "chat_service", "payload": {"amount": 65.6, "description": "rod\u00edzio do Pizzaiolo", "currency": "BRL"}}
backend-1   | {"timestamp": "2025-11-19T00:11:31.166456Z", "level": "ERROR", "message": "Tool Execution Failed", "module": "chat_service", "exception": "Traceback (most recent call last):\n  File \"/app/src/services/chat_service.py\", line 81, in _execute_tool\n    transaction_data = transaction_schema.TransactionCreate(**params)\n                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.12/typing.py\", line 1184, in __call__\n    result = self.__origin__(*args, **kwargs)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.12/typing.py\", line 1184, in __call__\n    result = self.__origin__(*args, **kwargs)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.12/typing.py\", line 501, in __call__\n    raise TypeError(f\"Cannot instantiate {self!r}\")\nTypeError: Cannot instantiate typing.Union"}
backend-1   | INFO:     172.18.0.1:45154 - "POST /api/v1/chat/sessions HTTP/1.1" 201 Created

```
---

POST {{BASE_URL}}/api/v1/chat/sessions

body:

```

{
    "message": "Olá, gastei R$65.60 no rodízio do Pizzaiolo ontem",
    "model_preference": "remote"
}

response: 

```

{
    "response": "Olá! Entendido, você gastou R$ 65,60 no rodízio do Pizzaiolo ontem.\n\nPosso ajudar em algo mais com essa informação? Por exemplo, você gostaria de:\n\n*   Registrar esse gasto em um orçamento?\n*   Comparar com gastos anteriores?\n*   Saber se esse valor está dentro do esperado para um rodízio?\n\nMe diga como posso te ajudar!",
    "session_id": 2,
    "session_title": "**Pizzaiolo: R$65.60 Rodízio**",
    "action_taken": "Error creating transaction"
}

```

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