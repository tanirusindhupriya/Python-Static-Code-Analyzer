import ast
import re
import json
import html


def find_unused_imports(tree):
    imports = []
    used_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                imports.append(item.asname or item.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            for item in node.names:
                imports.append(item.asname or item.name)

        elif isinstance(node, ast.Name):
            used_names.add(node.id)

    return [name for name in imports if name not in used_names]


def find_long_functions(tree):
    long_functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 5:
                long_functions.append(node.name)

    return long_functions


def find_excessive_nesting(tree):
    results = []

    class NestingVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0

        def visit_If(self, node):
            self.depth += 1
            if self.depth >= 3:
                results.append(node.lineno)
            self.generic_visit(node)
            self.depth -= 1

        def visit_For(self, node):
            self.depth += 1
            if self.depth >= 3:
                results.append(node.lineno)
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node):
            self.depth += 1
            if self.depth >= 3:
                results.append(node.lineno)
            self.generic_visit(node)
            self.depth -= 1

    NestingVisitor().visit(tree)

    return sorted(set(results))


def find_naming_problems(tree):
    naming_problems = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                naming_problems.append(node.name)

        elif isinstance(node, ast.Name):
            if not re.match(r"^[a-z_][a-z0-9_]*$", node.id):
                naming_problems.append(node.id)

    return sorted(set(naming_problems))


def calculate_complexity(tree):
    complexity = 1

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
            complexity += 1

    return complexity


def analyze_file(filename):

    with open(filename, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    unused_imports = find_unused_imports(tree)
    long_functions = find_long_functions(tree)
    excessive_nesting = find_excessive_nesting(tree)
    naming_problems = find_naming_problems(tree)
    complexity = calculate_complexity(tree)

    total_issues = (
        len(unused_imports)
        + len(long_functions)
        + len(excessive_nesting)
        + len(naming_problems)
    )

    report = {
        "file": filename,
        "unused_imports": unused_imports,
        "long_functions": long_functions,
        "excessive_nesting": excessive_nesting,
        "naming_problems": naming_problems,
        "complexity_score": complexity,
        "total_issues": total_issues
    }

    with open("report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("STATIC CODE ANALYZER")
    print("--------------------")
    print("File:", filename)
    print("Unused Imports:", unused_imports)
    print("Long Functions:", long_functions)
    print("Excessive Nesting:", excessive_nesting)
    print("Naming Problems:", naming_problems)
    print("Complexity Score:", complexity)
    print("Total Issues:", total_issues)
    print("JSON report created: report.json")

    file_name = html.escape(filename)

    unused_text = (
        ", ".join(map(str, unused_imports))
        if unused_imports else "No issues found"
    )

    long_text = (
        ", ".join(map(str, long_functions))
        if long_functions else "No issues found"
    )

    nesting_text = (
        ", ".join(map(str, excessive_nesting))
        if excessive_nesting else "No issues found"
    )

    naming_text = (
        ", ".join(map(str, naming_problems))
        if naming_problems else "No issues found"
    )

    html_report = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Python Static Code Analyzer</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
    color: #1e293b;
}}

.container {{
    max-width: 1100px;
    margin: auto;
    padding: 35px 20px;
}}

.header {{
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 35px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(79,70,229,0.25);
    animation: slideDown 0.8s ease;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
}}

.header p {{
    margin-top: 10px;
    opacity: 0.9;
}}

.file {{
    margin-top: 15px;
    font-weight: bold;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-top: 25px;
}}

.card {{
    background: white;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    transition: transform 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.8s ease;
}}

.card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}}

.card h3 {{
    margin: 0;
    font-size: 16px;
}}

.number {{
    font-size: 35px;
    font-weight: bold;
    margin-top: 12px;
}}

.dashboard {{
    margin-top: 25px;
    background: white;
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}}

.dashboard h2 {{
    margin-top: 0;
}}

.bar {{
    margin: 20px 0;
}}

.bar-title {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 7px;
    font-weight: bold;
}}

.bar-bg {{
    height: 14px;
    background: #e2e8f0;
    border-radius: 20px;
    overflow: hidden;
}}

.bar-fill {{
    height: 100%;
    border-radius: 20px;
    animation: grow 1.5s forwards;
}}

.imports {{
    background: #ef4444;
    width: {max(5, min(100, len(unused_imports) * 20))}%;
}}

.functions {{
    background: #f59e0b;
    width: {max(5, min(100, len(long_functions) * 20))}%;
}}

.nesting {{
    background: #8b5cf6;
    width: {max(5, min(100, len(excessive_nesting) * 20))}%;
}}

.naming {{
    background: #06b6d4;
    width: {max(5, min(100, len(naming_problems) * 20))}%;
}}

.complexity {{
    margin-top: 25px;
    text-align: center;
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #312e81);
    color: white;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}}

.complexity h2 {{
    margin: 0;
}}

.score {{
    font-size: 55px;
    font-weight: bold;
    margin-top: 10px;
}}

.issue {{
    margin-top: 18px;
    padding: 20px;
    border-radius: 12px;
    background: #f8fafc;
    border-left: 5px solid #4f46e5;
    transition: transform 0.3s;
}}

.issue:hover {{
    transform: translateX(8px);
}}

.issue h3 {{
    margin-top: 0;
}}

.footer {{
    text-align: center;
    margin-top: 30px;
    color: #64748b;
}}

@keyframes fadeUp {{
    from {{
        opacity: 0;
        transform: translateY(25px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes slideDown {{
    from {{
        opacity: 0;
        transform: translateY(-30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes grow {{
    from {{
        width: 0;
    }}
}}

@media (max-width: 800px) {{
    .cards {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 500px) {{
    .cards {{
        grid-template-columns: 1fr;
    }}
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>Python Static Code Analyzer</h1>

<p>Automated Source Code Quality Dashboard</p>

<div class="file">
Analyzed File: {file_name}
</div>

</div>

<div class="cards">

<div class="card">
<h3>Unused Imports</h3>
<div class="number">{len(unused_imports)}</div>
</div>

<div class="card">
<h3>Long Functions</h3>
<div class="number">{len(long_functions)}</div>
</div>

<div class="card">
<h3>Naming Problems</h3>
<div class="number">{len(naming_problems)}</div>
</div>

<div class="card">
<h3>Total Issues</h3>
<div class="number">{total_issues}</div>
</div>

</div>

<div class="dashboard">

<h2>Issue Analysis</h2>

<div class="bar">

<div class="bar-title">
<span>Unused Imports</span>
<span>{len(unused_imports)}</span>
</div>

<div class="bar-bg">
<div class="bar-fill imports"></div>
</div>

</div>

<div class="bar">

<div class="bar-title">
<span>Long Functions</span>
<span>{len(long_functions)}</span>
</div>

<div class="bar-bg">
<div class="bar-fill functions"></div>
</div>

</div>

<div class="bar">

<div class="bar-title">
<span>Excessive Nesting</span>
<span>{len(excessive_nesting)}</span>
</div>

<div class="bar-bg">
<div class="bar-fill nesting"></div>
</div>

</div>

<div class="bar">

<div class="bar-title">
<span>Naming Problems</span>
<span>{len(naming_problems)}</span>
</div>

<div class="bar-bg">
<div class="bar-fill naming"></div>
</div>

</div>

</div>

<div class="complexity">

<h2>Complexity Score</h2>

<div class="score">{complexity}</div>

<p>Basic complexity indicator</p>

</div>

<div class="dashboard">

<h2>Detailed Findings</h2>

<div class="issue">
<h3>Unused Imports</h3>
<p>{unused_text}</p>
</div>

<div class="issue">
<h3>Long Functions</h3>
<p>{long_text}</p>
</div>

<div class="issue">
<h3>Excessive Nesting</h3>
<p>{nesting_text}</p>
</div>

<div class="issue">
<h3>Naming Problems</h3>
<p>{naming_text}</p>
</div>

</div>

<div class="footer">

Generated automatically by Python Static Code Analyzer

</div>

</div>

</body>

</html>
"""

    with open("report.html", "w", encoding="utf-8") as file:
        file.write(html_report)

    print("HTML report created: report.html")


analyze_file("sample.py")