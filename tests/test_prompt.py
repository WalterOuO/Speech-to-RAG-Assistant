from app.services import prompt
from app.services.prompt import build_prompt

def test_build_prompt_content():
    context = "The sky is blue."
    question = "What color is the sky?"
    prompt = build_prompt(context, question)
    assert context in prompt
    assert question in prompt
    assert "你是一個文件問答系統" in prompt

def test_build_prompt_empty():
    prompt = build_prompt("", "")
    assert "參考資料：" in prompt
    assert "問題：" in prompt
    assert "答案：" in prompt
