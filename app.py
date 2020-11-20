from flowingbook import create_app
from selectors import DefaultSelector


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'], threaded=False)