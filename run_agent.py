#!/usr/bin/env python3
"""CLI entry point for the Test QA Agent.

Usage:
    python3 run_agent.py generate          # Generate new test cases
    python3 run_agent.py analyze           # Analyze coverage gaps
    python3 run_agent.py heal              # Self-heal flaky tests
    python3 run_agent.py all               # Run all agent actions
"""
import sys
from pathlib import Path
from src.agent.test_generator import generator
from src.agent.self_healer import healer
from src.utils.logger import logger


def cmd_generate():
    logger.info("Test QA Agent: Generating test cases...")
    generated = generator.generate_all_tests()
    logger.info(f"Generated {len(generated)} test file(s):")
    for f in generated:
        logger.info(f"  {f}")

    gaps = generator.coverage_gap_analysis()
    if gaps:
        logger.info(f"Coverage gaps detected ({len(gaps)}):")
        for gap in gaps:
            logger.info(f"  - {gap}")
    else:
        logger.info("No coverage gaps detected")


def cmd_analyze():
    logger.info("Test QA Agent: Analyzing test coverage...")
    analysis = generator.analyze_existing_tests()
    logger.info(f"Analysis: {analysis['total_tests']} existing tests")
    logger.info(f"Test files: {analysis['test_files']}")

    gaps = generator.coverage_gap_analysis()
    if gaps:
        logger.info(f"Missing tests ({len(gaps)}):")
        for g in gaps:
            logger.info(f"  - {g}")


def cmd_heal():
    logger.info("Test QA Agent: Checking for flaky tests...")
    db_path = Path("reports/heal_db.json")
    if not db_path.exists():
        logger.info("No heal database found. No flaky tests to heal.")
        return

    flaky = []
    for record in healer.heal_db:
        if healer.is_flaky(record.test_name):
            flaky.append(record.test_name)
            code = healer.generate_healed_test(record.test_name)
            if code:
                path = f"tests/test_healed_{record.test_name}.py"
                Path(path).write_text(code)
                logger.info(f"Generated self-healed test: {path}")

    if not flaky:
        logger.info("No flaky tests detected")


def cmd_all():
    cmd_analyze()
    cmd_generate()
    cmd_heal()
    logger.info("All agent actions completed")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    commands = {
        "generate": cmd_generate,
        "analyze": cmd_analyze,
        "heal": cmd_heal,
        "all": cmd_all,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    commands[command]()


if __name__ == "__main__":
    main()
