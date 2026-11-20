from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 58)
    print("AI-Based Resume Screening System (Non-ML)")
    print("Open http://127.0.0.1:5000 in your browser")
    print("=" * 58)
    app.run(debug=True)
