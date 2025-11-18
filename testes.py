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

when i run docker compose up build it works but if i try to run on my machine pnpm turbo dev it doesnt work. why

```

yordle@DESKTOP-RHRRBKP:~/IdeaProjects/SoFiA$ pnpm turbo dev
╭──────────────────────────────────────────────────────────────────────────╮
│                                                                          │
│                     Update available v2.5.8 ≫ v2.6.1                     │
│    Changelog: https://github.com/vercel/turborepo/releases/tag/v2.6.1    │
│          Run "pnpm dlx @turbo/codemod@latest update" to update           │
│                                                                          │
│          Follow @turborepo for updates: https://x.com/turborepo          │
╰──────────────────────────────────────────────────────────────────────────╯
turbo 2.5.8

• Packages in scope: backend, frontend
• Running dev in 2 packages
• Remote caching disabled
┌─ backend#dev > cache bypass, force executing 58befb84ea693a0d 

> backend@1.0.0 dev /home/yordle/IdeaProjects/SoFiA/apps/backend
> poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
└─ backend#dev ──
┌─ frontend#dev > cache bypass, force executing 5b7866974ba92ef4 

> frontend@0.0.0 dev /home/yordle/IdeaProjects/SoFiA/apps/frontend
> vite

failed to load config from /home/yordle/IdeaProjects/SoFiA/apps/frontend/vite.config.ts
error when starting dev server:
Error: EACCES: permission denied, open '/home/yordle/IdeaProjects/SoFiA/apps/frontend/node_modules/.vite-temp/vite.config.ts.timestamp-1763496324004-118ebfcbd8176.mjs'
    at async open (node:internal/fs/promises:641:25)
    at async Object.writeFile (node:internal/fs/promises:1215:14)
    at async loadConfigFromBundledFile (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/chunks/config.js:365
19:3)
    at async bundleAndLoadConfigFile (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/chunks/config.js:36415
:17)
    at async loadConfigFromFile (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/chunks/config.js:36382:42)
    at async resolveConfig (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/chunks/config.js:36031:22)
    at async _createServer (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/chunks/config.js:25979:67)
    at async CAC.<anonymous> (file:///home/yordle/IdeaProjects/SoFiA/node_modules/.pnpm/vite@7.2.2_@types+node@24.10.1_jiti@2.6.1_lightningcss@1.30.2/node_modules/vite/dist/node/cli.js:572:18)
 ELIFECYCLE  Command failed with exit code 1.
command finished with error: command (/home/yordle/IdeaProjects/SoFiA/apps/frontend) /home/yordle/.local/share/pnpm/.tools/pnpm/9.0.0/bin/pnpm run dev exited (1)
└─ frontend#dev ──
frontend#dev: command (/home/yordle/IdeaProjects/SoFiA/apps/frontend) /home/yordle/.local/share/pnpm/.tools/pnpm/9.0.0/bin/pnpm run dev exited (1)

 Tasks:    0 successful, 2 total
Cached:    0 cached, 2 total
  Time:    976ms 
Failed:    frontend#dev

 ERROR  run failed: command  exited (1)

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