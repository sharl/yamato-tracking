# yamato-tracking

クロネコヤマトの荷物追跡サービスを利用して、タスクトレイに常駐して荷物を追跡

## Run

```powershell
git clone https://github.com/sharl/yamato-tracking.git
cd yamato-tracking
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python yamato-tracking.py xxxxxxxxxxxx
```

### Re-run

```powershell
cd yamato-tracking
.\.venv\Scripts\activate
python yamato-tracking.py xxxxxxxxxxxx
```
