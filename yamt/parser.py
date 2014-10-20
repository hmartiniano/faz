# -*- coding: utf-8 -*-
import shlex
from .core import Task


def parser(text):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    tasks = []
    code = []
    comments = []
    task_found = False
    for line in text.splitlines():
        if line.startswith("#"):
            if task_found:
                tasks.append(
                    Task(interpreter, inputs, outputs, code, comments))
                comments = []
            if "<-" in line:
                interpreter = "bash"
                inputs = []
                outputs = []
                code = []
                lexer = shlex.shlex(line[1:])
                tokens = [token for token in lexer]
                print tokens
                found = False
                found_interpreter = False
                for token in tokens:
                    if "]" in token:
                        break
                    elif found_interpreter:
                        interpreter = token
                        found_interpreter = False
                    elif "[" in token:
                        found_interpreter = True
                    elif "<" in token or "-" in token:
                        found = True
                    elif "," in token:
                        continue
                    elif found:
                        inputs.append(token)
                    else:
                        outputs.append(token)
                task_found = True
            else:
                comments.append(line[1:])
                task_found = False
        else:
            code.append(line)
    if task_found:
        tasks.append(Task(interpreter, inputs, outputs, code, comments))
    return tasks


def parser(text):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    tasks = []
    code = []
    comments = []
    task_found = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            if task_found:
                tasks.append(
                    Task(interpreter, inputs, outputs, code, comments))
                comments = []
            if "<-" in line:
                if "[python]" in line:
                    interpreter = "python"
                elif "[ruby]" in line:
                    interpreter = "ruby"
                else:
                    interpreter = "bash"
                line = line.replace("[" + interpreter + "]", "")
                outputs, inputs = line[1:].split("<-")
                print inputs, outputs
                inputs = [item.strip() for item in inputs.split(",")]
                outputs = [item.strip() for item in outputs.split(",")]
                inputs = [item for item in inputs if not(item == "")]
                outputs = [item for item in outputs if not(item == "")]
                print inputs, outputs
                task_found = True
                code = []
            else:
                comments.append(line[1:])
                task_found = False
        else:
            code.append(line)
    if task_found:
        tasks.append(Task(interpreter, inputs, outputs, code, comments))
    return tasks
