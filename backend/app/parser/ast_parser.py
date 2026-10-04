import re
import os
from typing import List, Dict, Any, Optional
import tree_sitter
from tree_sitter import Language, Parser

# Try importing language packages
TS_JS_LANGUAGE = None
TS_TS_LANGUAGE = None
TS_TSX_LANGUAGE = None

try:
    import tree_sitter_javascript as tsjavascript
    TS_JS_LANGUAGE = Language(tsjavascript.language())
except Exception:
    pass

try:
    import tree_sitter_typescript as tstypescript
    if hasattr(tstypescript, "language_typescript"):
        TS_TS_LANGUAGE = Language(tstypescript.language_typescript())
    elif hasattr(tstypescript, "language"):
        TS_TS_LANGUAGE = Language(tstypescript.language())

    if hasattr(tstypescript, "language_tsx"):
        TS_TSX_LANGUAGE = Language(tstypescript.language_tsx())
    elif hasattr(tstypescript, "language"):
        TS_TSX_LANGUAGE = Language(tstypescript.language())
except Exception:
    pass

def create_parser(lang: Optional[Language]) -> Optional[Parser]:
    if not lang:
        return None
    try:
        p = Parser(lang)
        return p
    except Exception:
        try:
            p = Parser()
            p.language = lang
            return p
        except Exception:
            return None

class CodeSymbol:
    def __init__(
        self,
        name: str,
        symbol_type: str,
        file_path: str,
        start_line: int,
        end_line: int,
        start_column: int = 0,
        end_column: int = 0,
        container_name: Optional[str] = None,
        source_code: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.symbol_type = symbol_type
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.start_column = start_column
        self.end_column = end_column
        self.container_name = container_name
        self.source_code = source_code
        self.extra_metadata = extra_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "symbol_type": self.symbol_type,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_column": self.start_column,
            "end_column": self.end_column,
            "container_name": self.container_name,
            "source_code": self.source_code,
            "extra_metadata": self.extra_metadata,
        }

class CodeASTParser:
    def __init__(self):
        self.js_parser = create_parser(TS_JS_LANGUAGE)
        self.ts_parser = create_parser(TS_TS_LANGUAGE)
        self.tsx_parser = create_parser(TS_TSX_LANGUAGE) or self.ts_parser or self.js_parser

    def get_parser(self, extension: str) -> Optional[Parser]:
        ext = extension.lower()
        if ext in ['.tsx', '.jsx']:
            return self.tsx_parser or self.js_parser
        elif ext in ['.ts']:
            return self.ts_parser or self.js_parser
        elif ext in ['.js', '.mjs', '.cjs']:
            return self.js_parser
        return None

    def parse_file(self, file_path: str, code_content: str) -> Dict[str, Any]:
        _, ext = os.path.splitext(file_path)
        parser = self.get_parser(ext)

        symbols: List[CodeSymbol] = []
        imports: List[Dict[str, Any]] = []
        exports: List[Dict[str, Any]] = []
        call_expressions: List[Dict[str, Any]] = []
        routes: List[Dict[str, Any]] = []
        api_calls: List[Dict[str, Any]] = []
        db_models: List[Dict[str, Any]] = []

        if parser and code_content:
            try:
                tree = parser.parse(bytes(code_content, "utf-8"))
                self._traverse_tree(
                    node=tree.root_node,
                    code_bytes=bytes(code_content, "utf-8"),
                    file_path=file_path,
                    symbols=symbols,
                    imports=imports,
                    exports=exports,
                    calls=call_expressions
                )
            except Exception:
                pass

        self._extract_pattern_facts(
            code_content=code_content,
            file_path=file_path,
            symbols=symbols,
            imports=imports,
            exports=exports,
            calls=call_expressions,
            routes=routes,
            api_calls=api_calls,
            db_models=db_models
        )

        return {
            "file_path": file_path,
            "symbols": [s.to_dict() for s in symbols],
            "imports": imports,
            "exports": exports,
            "calls": call_expressions,
            "routes": routes,
            "api_calls": api_calls,
            "db_models": db_models
        }

    def _traverse_tree(
        self,
        node,
        code_bytes: bytes,
        file_path: str,
        symbols: List[CodeSymbol],
        imports: List[Dict[str, Any]],
        exports: List[Dict[str, Any]],
        calls: List[Dict[str, Any]],
        container_name: Optional[str] = None
    ):
        ntype = node.type

        if ntype in ("function_declaration", "generator_function_declaration"):
            name_node = node.child_by_field_name("name")
            name = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8") if name_node else "anonymous"
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            source_snippet = code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            
            symbol_type = "component" if name and name[0].isupper() else "function"
            symbols.append(CodeSymbol(
                name=name,
                symbol_type=symbol_type,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                container_name=container_name,
                source_code=source_snippet[:500]
            ))
            container_name = name

        elif ntype == "class_declaration":
            name_node = node.child_by_field_name("name")
            name = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8") if name_node else "AnonymousClass"
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            source_snippet = code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

            symbols.append(CodeSymbol(
                name=name,
                symbol_type="class",
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                container_name=container_name,
                source_code=source_snippet[:500]
            ))
            container_name = name

        elif ntype == "method_definition":
            name_node = node.child_by_field_name("name")
            name = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8") if name_node else "method"
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            source_snippet = code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

            symbols.append(CodeSymbol(
                name=name,
                symbol_type="method",
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                container_name=container_name,
                source_code=source_snippet[:500]
            ))

        elif ntype in ("lexical_declaration", "variable_declaration"):
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    value_node = child.child_by_field_name("value")
                    if name_node and value_node:
                        vname = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")
                        if value_node.type in ("arrow_function", "function"):
                            start_line = child.start_point[0] + 1
                            end_line = child.end_point[0] + 1
                            source_snippet = code_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                            symbol_type = "component" if vname and vname[0].isupper() else "function"
                            symbols.append(CodeSymbol(
                                name=vname,
                                symbol_type=symbol_type,
                                file_path=file_path,
                                start_line=start_line,
                                end_line=end_line,
                                container_name=container_name,
                                source_code=source_snippet[:500]
                            ))

        elif ntype == "call_expression":
            fn_node = node.child_by_field_name("function")
            if fn_node:
                callee_name = code_bytes[fn_node.start_byte:fn_node.end_byte].decode("utf-8", errors="ignore")
                calls.append({
                    "callee": callee_name,
                    "caller_container": container_name,
                    "line": node.start_point[0] + 1
                })

        for child in node.children:
            self._traverse_tree(child, code_bytes, file_path, symbols, imports, exports, calls, container_name)

    def _extract_pattern_facts(
        self,
        code_content: str,
        file_path: str,
        symbols: List[CodeSymbol],
        imports: List[Dict[str, Any]],
        exports: List[Dict[str, Any]],
        calls: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        api_calls: List[Dict[str, Any]],
        db_models: List[Dict[str, Any]]
    ):
        lines = code_content.splitlines()

        import_regex = re.compile(r'import\s+(?:({[^}]+})|([a-zA-Z0-9_$]+)|(?:\*\s+as\s+([a-zA-Z0-9_$]+)))\s+from\s+[\'"]([^\'"]+)[\'"]')
        require_regex = re.compile(r'(?:const|let|var)\s+(?:({[^}]+})|([a-zA-Z0-9_$]+))\s*=\s*require\([\'"]([^\'"]+)[\'"]\)')

        for idx, line in enumerate(lines, 1):
            m_imp = import_regex.search(line)
            if m_imp:
                named, default_imp, ns_imp, module_spec = m_imp.groups()
                specifiers = []
                if named:
                    specifiers = [s.strip().split(' as ')[0] for s in named.strip('{}').split(',') if s.strip()]
                elif default_imp:
                    specifiers = [default_imp]
                elif ns_imp:
                    specifiers = [ns_imp]

                imports.append({
                    "source": module_spec,
                    "specifiers": specifiers,
                    "line": idx,
                    "file_path": file_path
                })
                continue

            m_req = require_regex.search(line)
            if m_req:
                named, default_imp, module_spec = m_req.groups()
                specifiers = []
                if named:
                    specifiers = [s.strip().split(':')[0] for s in named.strip('{}').split(',') if s.strip()]
                elif default_imp:
                    specifiers = [default_imp]

                imports.append({
                    "source": module_spec,
                    "specifiers": specifiers,
                    "line": idx,
                    "file_path": file_path
                })

        export_regex = re.compile(r'export\s+(?:default\s+)?(?:function|class|const|let|var)\s+([a-zA-Z0-9_$]+)')
        for idx, line in enumerate(lines, 1):
            m_exp = export_regex.search(line)
            if m_exp:
                exports.append({
                    "name": m_exp.group(1),
                    "line": idx,
                    "file_path": file_path
                })

        route_regex = re.compile(r'(?:app|router|server)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]')
        for idx, line in enumerate(lines, 1):
            m_route = route_regex.search(line)
            if m_route:
                method, path = m_route.groups()
                routes.append({
                    "method": method.upper(),
                    "path": path,
                    "file_path": file_path,
                    "line": idx
                })

        if "app/" in file_path.replace("\\", "/") or "pages/api" in file_path.replace("\\", "/"):
            next_handler_regex = re.compile(r'export\s+async\s+function\s+(GET|POST|PUT|DELETE|PATCH)\b')
            for idx, line in enumerate(lines, 1):
                m_next = next_handler_regex.search(line)
                if m_next:
                    method = m_next.group(1)
                    parts = file_path.replace("\\", "/").split("/")
                    route_path = "/" + "/".join(parts[parts.index("api") if "api" in parts else 0:])
                    route_path = route_path.replace("/route.ts", "").replace("/route.js", "").replace(".ts", "").replace(".js", "")
                    routes.append({
                        "method": method,
                        "path": route_path,
                        "file_path": file_path,
                        "line": idx
                    })

        fetch_regex = re.compile(r'(?:fetch|axios\.(?:get|post|put|delete|patch)|apiService\.[a-zA-Z0-9_$]+)\s*\(\s*[`\'"]([^\'`"]+)[`\'"]')
        for idx, line in enumerate(lines, 1):
            m_fetch = fetch_regex.search(line)
            if m_fetch:
                endpoint = m_fetch.group(1)
                method = "GET"
                if "post" in line.lower():
                    method = "POST"
                elif "put" in line.lower():
                    method = "PUT"
                elif "delete" in line.lower():
                    method = "DELETE"

                api_calls.append({
                    "endpoint": endpoint,
                    "method": method,
                    "file_path": file_path,
                    "line": idx
                })

        if file_path.endswith(".prisma"):
            prisma_model_regex = re.compile(r'model\s+([a-zA-Z0-9_$]+)\s*\{')
            for idx, line in enumerate(lines, 1):
                m_prisma = prisma_model_regex.search(line)
                if m_prisma:
                    db_models.append({
                        "name": m_prisma.group(1),
                        "model_type": "prisma",
                        "file_path": file_path,
                        "line": idx
                    })
        else:
            prisma_client_regex = re.compile(r'prisma\.([a-zA-Z0-9_$]+)\.(findMany|findUnique|findFirst|create|update|delete|upsert)\b')
            for idx, line in enumerate(lines, 1):
                m_pc = prisma_client_regex.search(line)
                if m_pc:
                    model_name = m_pc.group(1)
                    if not any(m["name"].lower() == model_name.lower() for m in db_models):
                        db_models.append({
                            "name": model_name.capitalize(),
                            "model_type": "prisma",
                            "file_path": file_path,
                            "line": idx
                        })
