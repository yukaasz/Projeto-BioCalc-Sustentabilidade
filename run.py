from app import app

# executa a aplicação web
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)