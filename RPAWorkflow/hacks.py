def dispatch_while_working(initial_workflow_handler, *args, **kwargs):
    current_workflow_handler = initial_workflow_handler

    while True:
        try:
            initial_workflow_handler.dispatch_while_working(*args, **kwargs)

            break
        except WorkflowHandlerMigration as ex:
            current_workflow_handler = ex.new_workflow_handler
