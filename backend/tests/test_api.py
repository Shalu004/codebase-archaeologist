import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db
from app.parser.scanner import FileScanner
from app.parser.ast_parser import CodeASTParser

# Ensure DB tables are initialized before running tests
init_db()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Codebase Archaeologist" in data["service"]

def test_file_scanner():
    scanner = FileScanner(os.path.abspath("."))
    scanned = scanner.scan()
    assert isinstance(scanned, list)

def test_ast_parser():
    parser = CodeASTParser()
    sample_code = """
    import { useState } from 'react';

    export function LoginView() {
        const [email, setEmail] = useState('');
        const handleLogin = async () => {
            await fetch('/api/auth/login', { method: 'POST' });
        };
        return <button onClick={handleLogin}>Login</button>;
    }
    """
    res = parser.parse_file("LoginView.tsx", sample_code)
    assert "symbols" in res
    assert "routes" in res
    assert "api_calls" in res
    assert len(res["api_calls"]) > 0
    assert res["api_calls"][0]["endpoint"] == "/api/auth/login"

def test_analyze_fixture_endpoint():
    response = client.post("/api/repositories/analyze-fixture?name=CivicFixTest")
    assert response.status_code in (200, 404)
