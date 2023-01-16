from project_files import app, scheduler
from project_files import routes
# from project_files.functions import get_notes

if __name__ =="__main__":
  scheduler.start()
  app.run(debug=True)