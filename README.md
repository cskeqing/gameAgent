# Game Agent - Hybrid Imitation Engine

A cross-platform (Windows/macOS) visual AI agent for game automation, featuring a hybrid decision engine (Rule-based + LLM) and human-like input simulation.

## Features

*   **Cross-Platform Vision**: High-performance screen capture using `dxcam` (Windows) and `mss` (Mac).
*   **Hybrid Brain**:
    *   **System 1 (Fast)**: Rule-based engine for real-time combat/navigation.
    *   **System 2 (Slow)**: LLM (GPT-4o/Local) for complex decision making and dialogue understanding.
*   **Humanized Input**: Bezier curve mouse movements and random jitter to avoid detection.
*   **Black Box Recorder**: Logs every decision with screenshots for debugging.
*   **Configurable**: YAML-based configuration for easy tuning without coding.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: For GPU acceleration with YOLO/PaddleOCR, ensure you have the correct CUDA versions installed.*

2.  Run the Agent:
    ```bash
    python src/main.py
    ```

## Configuration

Edit `configs/agent_config.yaml` to tweak:
*   **Mouse Speed**: `behavior.humanization.mouse_speed`
*   **LLM Model**: `llm.model`
*   **Game Rules**: Define triggers in `src/brain/rules.py` (or load from external JSON in future updates).

## Project Structure

*   `src/core`: Vision, Capture, and Input engines.
*   `src/brain`: LLM and Rule decision logic.
*   `src/ui`: PySide6 GUI.
*   `logs`: Snapshots and execution logs.
