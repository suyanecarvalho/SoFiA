import sys
import os
import json
import time
import argparse
import pandas as pd
from tqdm import tqdm
from apps.backend.benchmarking.utils import ui, db_setup, evaluation
from apps.backend.src.llm.factory import get_llm_instance

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(APP_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM Benchmarks for SofIA.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--local",
        nargs="+",
        metavar="MODEL_NAME",
        help="Benchmark one or more local models by name (e.g., -l mistral llama3).",
    )
    parser.add_argument(
        "-r",
        "--remote",
        nargs="+",
        metavar="API_KEY",
        help="Benchmark one or more remote models by API key (e.g., -r sk-...).",
    )
    parser.add_argument(
        "--dataset",
        default="dataset.jsonl",
        help="Path to the dataset file (default: dataset.jsonl).",
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.csv",
        help="Path to save the CSV results (default: benchmark_results.csv).",
    )
    args = parser.parse_args()
    models_to_run = []
    if args.local:
        for model_name in args.local:
            instance = get_llm_instance("local", model_name)
            models_to_run.append({"name": f"local-{model_name}", "instance": instance})

    if args.remote:
        for i, api_key in enumerate(args.remote):
            instance = get_llm_instance("remote", api_key)
            models_to_run.append({"name": f"remote-{i + 1}", "instance": instance})

    if not models_to_run:
        ui.print_warning(
            "No local or remote models specified. Running benchmark with DummyLLM."
        )
        instance = get_llm_instance("dummy")
        models_to_run.append({"name": "dummy", "instance": instance})

    ui.print_info(
        f"Models to benchmark: {', '.join([m['name'] for m in models_to_run])}"
    )
    ui.print_info(f"Using dataset: {args.dataset}")
    with open(args.dataset, "r") as f:
        test_cases = [json.loads(line) for line in f]
    results = []
    base_data_dir = "base_data"
    for model_info in models_to_run:
        model_name = model_info["name"]
        model_instance = model_info["instance"]
        ui.print_info(f"\nBenchmarking model: {model_name}")

        for case in tqdm(test_cases, desc=f"Model: {model_name}"):
            SessionLocal = db_setup.create_in_memory_db_session()
            db = SessionLocal()
            db_setup.seed_base_data(db, base_data_dir)
            db_setup.setup_test_case_state(db, case.get("setup", {}))
            actual_output = None
            start_time = time.perf_counter()
            try:
                if case["type"] == "get":
                    actual_output = model_instance.get_structured_answer(case["prompt"])
                elif case["type"] == "insert":
                    actual_output = model_instance.create_transaction_from_prompt(
                        case["prompt"]
                    )
            except Exception as e:
                actual_output = None
                ui.print_warning(f"  Execution error in test '{case['id']}': {e}")
            duration = time.perf_counter() - start_time
            score = evaluation.calculate_score(
                actual_output, case["expected"], case["type"], case["difficulty"]
            )
            results.append(
                {
                    "model_name": model_name,
                    "test_case_id": case["id"],
                    "difficulty": case.get("difficulty", "unknown"),
                    "score": score,
                    "duration_seconds": duration,
                }
            )
            db.close()

    if not results:
        ui.print_warning("No results were generated. Exiting.")
        return

    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, index=False)
    ui.print_success(f"Benchmark complete. Results saved to {args.output}")


if __name__ == "__main__":
    main()
