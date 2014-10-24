# -*- coding: utf-8 -*-
import shlex
import re
import logging


from yamt.core import Task, Environment


TASK_PATTERN = r"^#[ ]*(?P<outputs>[a-zA-Z0-9, _\-\[\]\*]+)*[ ]*<-[ ]*(?P<inputs>[a-zA-Z0-9, _\-\[\]\*]+)*[ ]*[:]*[ ]*(?P<options>[a-zA-Z0-9, _\-\[\]\*]+)*"


def old_parser(text):
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


def parse_input_file(text, **kwargs):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    tasks = []
    code = []
    comments = []
    task_found = False
    for line in text.splitlines():
        # line = line.rstrip()
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
                inputs = [item.strip() for item in inputs.split(",")]
                outputs = [item.strip() for item in outputs.split(",")]
                inputs = [item for item in inputs if not(item == "")]
                outputs = [item for item in outputs if not(item == "")]
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


def split_task_parameters(line):
    if line is None:
        result = []
    else:
       result = [parameter.strip() for parameter in line.split(",")]
    return result


def find_tasks(lines):
    tasks = []
    linenumbers = []
    pattern = re.compile(TASK_PATTERN)
    for n, line in enumerate(lines):
        if "#" in line and "<-" in line:
            #m = pattern.match(line)
            m = re.match(TASK_PATTERN, line)
            if m is not None:
                groupdict = m.groupdict()
                linenumbers.append(n)
                for key in groupdict:
                    groupdict[key] = split_task_parameters(groupdict[key])
                    logging.debug("{0}: {1}".format(key, ", ".join(groupdict[key])))
                tasks.append(groupdict)
    linenumbers.append(len(lines))
    return tasks, linenumbers


def create_environment(preamble):
    environment = Environment()
    for line in preamble:
        if " = " in line and not line.startswith("#"):
            tmp = line.split("=")
            key = tmp[0].strip()
            val = tmp[1].strip()
            environment__dict__.update({key: val})
    return environment


def parse_input_file(text, **kwargs):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    lines = text.splitlines()
    tasks, linenumbers = find_tasks(lines)
    preamble = [line for line in lines[:linenumbers[0]]]
    environment = create_environment(preamble)
    code_sections = []
    for n in range(len(linenumbers) - 1):
        code_sections.append((linenumbers[n], linenumbers[n+1]))
    for n, task in zip(code_sections, tasks):
        task["code"] = lines[n[0]: n[1]]
        task["environment"] = environment
    clean_tasks = []
    for task in tasks:
        clean_tasks.append(Task(**task))
    return clean_tasks
