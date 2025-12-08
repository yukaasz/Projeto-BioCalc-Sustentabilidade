"""
run.py - Executar a aplicação
"""

from app import app

if __name__ == '__main__':
    print("Iniciando BioCalc na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)