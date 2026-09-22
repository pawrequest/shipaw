print('__name__ is', __name__)
DEV = True  # True for development with hot reload, False for production with no hot reload

from nicegui.ui_run import run as ui_run  # just importing the function to run the server

if (
    not DEV or not __name__ == '__main__'
):  # you can do `if True:` to bypass this to revert to the normal behavior, but that is slow...
    # Explanation: 2 reasons for running this code:
    # 1. not in dev mode, so there is no __mp_main__, this is already where NiceGUI will run
    # 2. or, in dev mode, and this is the __mp_main__, so we want to run this code

    print('Here are a bunch of startup tasks that must be run once, and before the server starts')
    print('Before-server-start startup tasks are done')

    from nicegui import app, ui  # the normal import

    @ui.page('/')
    def index():
        print('Here are some tasks you want to run before every page load')
        ui.label('You page definitions go here')

    def delayed_startup_tasks():
        print('Here are a bunch of startup tasks that also must be run once, but can be after the server has started')
        for _ in range(100000000):
            pass  # some long running task
        print('After-server-start startup tasks are done')

    app.on_startup(delayed_startup_tasks)

ui_run(reload=DEV, native=True)  # DEV mode will reload the server when the code changes

# This means:
# If it is DEV mode, __main__ simply runs ui_run, which will start the server, spawn __mp_main__ and run the code above to start the server
# If it is not DEV mode, __main__ will run the code above, and then run ui_run, which will start the server directly
