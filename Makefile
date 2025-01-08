run:
	@echo "[+] Running ..."
	@streamlit run brandStrategist.py

activate:
	@echo "[+] Activating Enviroment"
	@echo ""
	@MarcelAIAgent\Scripts\activate

deactivate:
	./deactivate

install:
	@echo "[+] Install dependencies..."
	@pip install -r requirements.txt
