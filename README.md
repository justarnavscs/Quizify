# Quizify / FlexQuiz

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python flexquiz.py
```

## Build EXE
```bash
pyinstaller --onefile --noconsole --icon=assets/icon.ico flexquiz.py
```

## Build installer
Compile `setup.iss` with Inno Setup to generate `FlexQuiz_Setup.exe`.
