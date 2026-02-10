# Charlie Tools Guide

This guide explains **when** to use each tool (use cases, not parameters).

## Core rule: tool choice

- Use internal tools first.
- Use web tools only if no internal tool can solve the task.

## System

- Use `get_time_tool` when you need the current local date or time for a response, a log message, or scheduling.

## Docker

- Use `get_all_images_tool` when the user asks what images are available or needs to verify an image exists.
- Use `get_all_containers_tool` when the user wants to see running or stopped containers or diagnose container state.
- Use `run_container_tool` when the user wants to launch a new container from an image.
- Use `start_container_tool` when a container exists but is stopped and should be started.
- Use `stop_container_tool` when a running container should be stopped safely.

## Schedule (RTU MIREA)

- Use `mirea_schedule_tool` when the user asks for a MIREA schedule for today or a specific date.

## Telegram

- Use `send_telegram_message_tool` when the user needs to receive a message or notification in Telegram.

## Documents

- Use `get_docs_design_rules_tool` when the user requests ГОСТ-style formatting rules or guidance.
- Use `get_charlie_tools_guide_tool` when the assistant needs to re-check tool usage guidance.

## Web (last resort)

- Use `web_search_tool` when the information is not available via internal tools and must be found online.
- Use `web_fetch_tool` when a specific URL needs to be read after you already know the target page.
