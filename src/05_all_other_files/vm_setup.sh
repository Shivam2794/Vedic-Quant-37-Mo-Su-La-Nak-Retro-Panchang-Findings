#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv unzip tmux
unzip deploy.zip -d ~/scratch
cd ~/scratch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install lightrag-hku torch torchvision torchaudio
pip install sentence-transformers
pip install aiohttp asyncio pypdf
sed -i 's/llm_model_max_async = 3/llm_model_max_async = 15/g' nadi_master_pipeline.py
sed -i 's/llm_model_max_async = 3/llm_model_max_async = 15/g' jaimini_master_pipeline.py
sed -i 's/llm_model_max_async=3/llm_model_max_async=15/g' nadi_master_pipeline.py
sed -i 's/llm_model_max_async=3/llm_model_max_async=15/g' jaimini_master_pipeline.py

# Modify BOOKS_DIR paths in scripts
sed -i 's|C:\\Users\\patel\\Desktop\\Python\\Learn\\Books\\04_Vedic_Astrology_Gann_Theory|/home/patel/books/04_Vedic_Astrology_Gann_Theory|g' nadi_master_pipeline.py
sed -i 's|C:\\Users\\patel\\Desktop\\Python\\Learn\\Books\\04_Vedic_Astrology_Gann_Theory|/home/patel/books/04_Vedic_Astrology_Gann_Theory|g' jaimini_master_pipeline.py
sed -i 's|C:\\Users\\patel\\Desktop\\Python\\Learn\\Books\\05_Vedic_Astrology_Jaimini|/home/patel/books/04_Vedic_Astrology_Gann_Theory|g' jaimini_master_pipeline.py

echo "Setup complete!"
