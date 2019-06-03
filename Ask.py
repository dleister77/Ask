from app import create_app, db
from app.models import User, Address, State, Category, Review, Provider, Group

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"User":User, "Address":Address, "State":State, "Category": 
    Category, "Review": Review, "Provider": Provider, "db": db, "Group": Group}