from task_tracker import create_app

app = create_app('task_tracker.config.DevelopmentConfig')
if __name__ == "__main__":
    app.run()